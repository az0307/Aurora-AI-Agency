#!/usr/bin/env python3
"""
HexStrike Phone TUI — Rich terminal dashboard for the USB lab.
Connects over SSH tunnel or local WiFi. Falls back to local LLM planning.

Install: pip install rich requests
Run:     python3 tui.py [lab_host:port]
"""

import os
import sys
import json
import time
import select
import threading
import subprocess
import urllib.parse
from pathlib import Path
from datetime import datetime

try:
    import requests
    _REQUESTS = True
except ImportError:
    import urllib.request
    _REQUESTS = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    _RICH = True
except ImportError:
    print("Install rich: pip install rich")
    sys.exit(1)

console = Console()

LAB = os.environ.get("HEXSTRIKE_LAB", sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8888")
if not LAB.startswith("http"):
    LAB = f"http://{LAB}"
LAB = LAB.rstrip("/")

MODEL_PATH = Path.home() / "models"
LLAMA_BIN  = Path.home() / "llama.cpp" / "build" / "bin" / "llama-cli"


# ── HTTP helpers ──────────────────────────────────────────────────────────────
def _get(path: str, params: dict = None, timeout: int = 5) -> dict:
    url = f"{LAB}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        if _REQUESTS:
            r = requests.get(url, timeout=timeout)
            return r.json()
        else:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

def _post(path: str, data: dict = None, timeout: int = 10) -> dict:
    url = f"{LAB}{path}"
    payload = json.dumps(data or {}).encode()
    try:
        if _REQUESTS:
            r = requests.post(url, json=data, timeout=timeout)
            return r.json()
        else:
            req = urllib.request.Request(url, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


# ── Local LLM ─────────────────────────────────────────────────────────────────
def local_llm(prompt: str, max_tokens: int = 512) -> str:
    models = list(MODEL_PATH.glob("*.gguf"))
    if not models or not LLAMA_BIN.exists():
        return "[dim]No local model — run ~/download-model.sh[/dim]"
    model = models[0]
    try:
        result = subprocess.run(
            [str(LLAMA_BIN), "-m", str(model), "-p", prompt,
             "-n", str(max_tokens), "--temp", "0.15", "-c", "2048", "--quiet"],
            capture_output=True, text=True, timeout=90
        )
        return result.stdout.strip() or "[yellow]No output[/yellow]"
    except subprocess.TimeoutExpired:
        return "[red]Inference timeout[/red]"
    except Exception as e:
        return f"[red]Error: {e}[/red]"


# ── State ─────────────────────────────────────────────────────────────────────
class State:
    def __init__(self):
        self.lab_online    = False
        self.health        = {}
        self.glm_status    = {}
        self.agents        = []
        self.active_eid    = None
        self.agent_logs    = []
        self.log_offset    = 0
        self.scope_list    = []
        self.sessions      = {}
        self.last_refresh  = 0
        self._lock         = threading.Lock()

    def refresh(self):
        h = _get("/health", timeout=3)
        with self._lock:
            self.lab_online = "error" not in h
            self.health     = h

        if self.lab_online:
            glm = _get("/glm/status", timeout=3)
            agents = _get("/agent/status", timeout=3)
            scope = _get("/scope/list", timeout=3)
            with self._lock:
                self.glm_status = glm
                self.agents     = agents.get("agents", []) if isinstance(agents, dict) else []
                self.scope_list = scope.get("authorizations", [])

            if self.active_eid:
                logs = _get("/agent/logs",
                            {"engagement_id": self.active_eid, "since": self.log_offset}, timeout=3)
                with self._lock:
                    new_logs = logs.get("logs", [])
                    self.agent_logs.extend(new_logs)
                    self.agent_logs = self.agent_logs[-200:]
                    self.log_offset = logs.get("total", self.log_offset)

                msf = _get("/msf/status", {"engagement_id": self.active_eid}, timeout=2)
                with self._lock:
                    self.sessions = msf.get("sessions", {})

        self.last_refresh = time.time()


state = State()


# ── Renderers ─────────────────────────────────────────────────────────────────
SEVERITY_COLORS = {"P0": "red", "P1": "yellow", "P2": "green", "CRIT": "red bold",
                   "HIGH": "yellow", "MED": "cyan"}

def render_header() -> Panel:
    now = datetime.now().strftime("%H:%M:%S")
    lab_txt = (
        f"[green]● LAB ONLINE[/green] {LAB}"
        if state.lab_online else
        f"[red]● LAB OFFLINE[/red] {LAB}"
    )
    backend = state.glm_status.get("active_backend", "?")
    backend_color = {"glm-4.5": "cyan", "ollama": "green", "simulation": "dim"}.get(backend, "white")
    backend_txt = f"[{backend_color}]LLM: {backend}[/{backend_color}]"
    return Panel(
        f"[bold red]☠ HEXSTRIKE[/bold red]  [dim]PHONE CONTROLLER[/dim]   "
        f"{lab_txt}   {backend_txt}   [dim]{now}[/dim]",
        box=box.HORIZONTALS,
        style="on black",
    )


def render_agents() -> Table:
    t = Table(box=box.SIMPLE, show_header=True, header_style="bold dim",
              title="[bold]ACTIVE AGENTS[/bold]", title_style="dim")
    t.add_column("ENG", style="cyan", no_wrap=True, width=18)
    t.add_column("TARGET", width=16)
    t.add_column("STATUS", width=12)
    t.add_column("PHASE", width=10)
    t.add_column("FINDINGS", justify="right")

    if not state.agents:
        t.add_row("[dim]no agents[/dim]", "", "", "", "")
        return t

    status_colors = {
        "running": "green", "paused": "yellow", "complete": "cyan",
        "aborted": "red", "error": "red bold",
    }
    for a in state.agents:
        sc = status_colors.get(a.get("status", ""), "white")
        is_active = a.get("engagement_id") == state.active_eid
        prefix = "[green]▶[/green] " if is_active else "  "
        t.add_row(
            prefix + (a.get("engagement_id") or "")[:16],
            (a.get("target") or "")[:14],
            f"[{sc}]{a.get('status', '?')}[/{sc}]",
            a.get("current_phase") or "—",
            str(a.get("findings", 0)),
        )
    return t


def render_scope() -> Table:
    t = Table(box=box.SIMPLE, show_header=True, header_style="bold dim",
              title="[bold]AUTHORIZATIONS[/bold]", title_style="dim")
    t.add_column("ENG", style="cyan", width=18)
    t.add_column("TARGET", width=18)
    t.add_column("STATUS", width=10)
    t.add_column("EXPIRES", width=12)

    sc_colors = {"active": "green", "revoked": "red", "expired": "yellow"}
    for s in state.scope_list[:6]:
        sc = sc_colors.get(s.get("status", ""), "white")
        exp = (s.get("testing_window_end") or "")[:10]
        t.add_row(
            (s.get("engagement_id") or "")[:16],
            (s.get("target") or "")[:16],
            f"[{sc}]{s.get('status', '?')}[/{sc}]",
            exp,
        )
    if not state.scope_list:
        t.add_row("[dim]no authorizations[/dim]", "", "", "")
    return t


def render_sessions() -> Table:
    t = Table(box=box.SIMPLE, show_header=True, header_style="bold dim",
              title="[bold]MSF SESSIONS[/bold]", title_style="dim")
    t.add_column("#", width=4)
    t.add_column("TYPE", width=12)
    t.add_column("TARGET", width=16)
    t.add_column("USER", width=12)

    if not state.sessions:
        t.add_row("[dim]—[/dim]", "[dim]no sessions[/dim]", "", "")
        return t

    for sid, s in list(state.sessions.items())[:5]:
        t.add_row(
            str(sid),
            s.get("type", "?")[:10],
            (s.get("target_host") or s.get("tunnel_peer",""))[:14],
            (s.get("username") or "?")[:10],
        )
    return t


def render_logs() -> Panel:
    lines = []
    log_colors = {
        "critical": "red bold", "error": "red", "warn": "yellow",
        "ok": "green", "phase": "cyan bold", "complete": "green bold",
        "adapt": "magenta", "start": "cyan",
    }
    for entry in state.agent_logs[-20:]:
        lvl   = entry.get("lvl", "info")
        msg   = entry.get("msg", "")
        color = log_colors.get(lvl, "dim")
        lines.append(f"[{color}]{msg}[/{color}]")

    if not lines:
        lines = ["[dim]// no logs — start an engagement[/dim]"]

    return Panel(
        "\n".join(lines[-18:]),
        title=f"[bold]AGENT LOG[/bold] [dim]{state.active_eid or 'none'}[/dim]",
        box=box.SIMPLE,
    )


def render_status_bar() -> Text:
    t = Text()
    t.append("  ◈ ", style="dim")
    cmds = ["[r]un", "[a]bort", "[A]pprove", "[l]og", "[p]lan", "[s]cope",
            "[m]sf", "[q]uit"]
    for i, c in enumerate(cmds):
        t.append(c, style="cyan")
        if i < len(cmds)-1:
            t.append("  ", style="dim")
    return t


# ── Dashboard layout ──────────────────────────────────────────────────────────
def build_dashboard():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="statusbar", size=1),
    )
    layout["body"].split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=3),
    )
    layout["left"].split_column(
        Layout(name="agents"),
        Layout(name="scope"),
        Layout(name="sessions"),
    )
    return layout


# ── Command handlers ──────────────────────────────────────────────────────────
def cmd_run():
    console.print("[cyan]Run new engagement[/cyan]")
    eid    = Prompt.ask("Engagement ID", default="ENG-2026-0001")
    target = Prompt.ask("Target IP/host")
    scope  = Prompt.ask("Scope (CIDR or *.domain)", default=target)
    phases_raw = Prompt.ask("Phases", default="recon,vuln,report")
    auto   = Confirm.ask("Auto-mode (no approval gates)?", default=False)
    phases = [p.strip() for p in phases_raw.split(",")]

    with console.status("[cyan]Authorizing scope...[/cyan]"):
        auth = _post("/scope/authorize", {
            "engagement_id": eid, "operator": "operator",
            "target": target, "scope": scope,
            "engagement_type": "Internal", "methodology": "PTES",
            "authorization_ref": f"CLI-{int(time.time())}",
            "client_contact": "operator@local",
            "testing_window_end": "2026-12-31T23:59:00+00:00",
        })
        if "error" in auth:
            console.print(f"[red]Scope auth failed: {auth['error']}[/red]")
            return

    with console.status("[cyan]Starting agent...[/cyan]"):
        res = _post("/agent/run", {
            "engagement_id": eid,
            "target": target, "scope": scope,
            "phases": phases, "auto_mode": auto,
        })

    if "error" in res:
        console.print(f"[red]Agent error: {res['error']}[/red]")
    else:
        state.active_eid = eid
        state.agent_logs.clear()
        state.log_offset = 0
        console.print(f"[green]Agent started — {eid}[/green]")


def cmd_abort():
    eid = Prompt.ask("Engagement ID", default=state.active_eid or "")
    if not eid:
        return
    res = _post("/agent/abort", {"engagement_id": eid})
    console.print(f"[yellow]Abort: {res.get('status','?')}[/yellow]")


def cmd_approve():
    eid = state.active_eid or Prompt.ask("Engagement ID")
    if not eid:
        return
    if Confirm.ask(f"[yellow]Approve pending tool step for {eid}?[/yellow]"):
        res = _post("/agent/approve", {"engagement_id": eid})
        console.print(f"[green]Approved: {res.get('status')}[/green]")
    else:
        res = _post("/agent/deny", {"engagement_id": eid})
        console.print(f"[red]Denied: {res.get('status')}[/red]")


def cmd_plan():
    q = Prompt.ask("[magenta]Ask local LLM[/magenta]")
    if not q:
        return
    console.print("[dim]Thinking...[/dim]")
    # Try GLM/Ollama via HexStrike interpret
    res = _post("/glm/interpret", {
        "skill": "tactical_planning",
        "target": state.active_eid or "unknown",
        "context": {"question": q, "agent_state": state.agents[:3]},
    })
    if "error" not in res:
        console.print(Panel(json.dumps(res, indent=2), title="[cyan]LLM[/cyan]", box=box.SIMPLE))
    else:
        # Fall to local llama.cpp
        answer = local_llm(f"Red team tactical question: {q}\nBe concise and practical.")
        console.print(Panel(answer, title="[magenta]Local LLM[/magenta]", box=box.SIMPLE))


def cmd_scope():
    res = _post("/scope/generate", {
        "engagement_id": Prompt.ask("Engagement ID"),
        "target": Prompt.ask("Target"),
        "scope": Prompt.ask("Scope"),
        "operator": "operator",
        "engagement_type": Prompt.ask("Type", default="Internal"),
        "methodology": "PTES",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": Prompt.ask("End date", default="2026-12-31"),
    })
    if "error" not in res:
        console.print(Panel(res.get("document", ""), title="[cyan]SCOPE DOCUMENT[/cyan]",
                            box=box.SIMPLE))
    else:
        console.print(f"[red]{res['error']}[/red]")


def cmd_msf():
    eid = state.active_eid or Prompt.ask("Engagement ID")
    cmd = Prompt.ask("MSF command (or 'list')", default="list")
    if cmd == "list":
        res = _get("/msf/sessions", {"engagement_id": eid})
        console.print_json(json.dumps(res, indent=2))
    else:
        sid = Prompt.ask("Session ID")
        approved = Confirm.ask(f"[yellow]Approve: {cmd}[/yellow]?")
        res = _post("/msf/run", {
            "engagement_id": eid, "session_id": sid,
            "command": cmd, "approved": approved,
        })
        console.print_json(json.dumps(res, indent=2))


# ── Main TUI loop ─────────────────────────────────────────────────────────────
COMMANDS = {
    "r": cmd_run, "a": cmd_abort, "A": cmd_approve,
    "p": cmd_plan, "s": cmd_scope, "m": cmd_msf,
}

def background_refresh():
    while True:
        try:
            state.refresh()
        except Exception as exc:
            console.log(f"[dim]Refresh error: {exc}[/dim]")
        time.sleep(5)


def main():
    console.clear()
    console.print(Panel(
        "[bold red]☠[/bold red] [bold]HEXSTRIKE PHONE CONTROLLER[/bold]\n"
        f"[dim]Connecting to {LAB}[/dim]",
        box=box.DOUBLE_EDGE,
    ))

    # Initial connect
    with console.status("[cyan]Connecting to lab...[/cyan]"):
        state.refresh()

    if not state.lab_online:
        console.print("[yellow]Lab offline — local LLM planning mode[/yellow]")
        console.print("[dim]Tip: bash ~/tunnel.sh to connect[/dim]")

    # Start background refresh
    t = threading.Thread(target=background_refresh, daemon=True)
    t.start()

    layout = build_dashboard()

    # Main live loop
    with Live(layout, refresh_per_second=1, screen=True) as live:
        while True:
            # Render
            layout["header"].update(render_header())
            layout["agents"].update(render_agents())
            layout["scope"].update(render_scope())
            layout["sessions"].update(render_sessions())
            layout["right"].update(render_logs())
            layout["statusbar"].update(render_status_bar())

            # Non-blocking input check via separate thread
            time.sleep(0.3)

            # Handle keyboard (crude but portable on Termux)
            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.read(1).strip()
                if key == "q":
                    live.stop()
                    console.print("[dim]Goodbye.[/dim]")
                    return
                elif key == "l":
                    live.stop()
                    state.active_eid = Prompt.ask("Watch engagement", default=state.active_eid or "")
                    state.agent_logs.clear()
                    state.log_offset = 0
                    live.start(refresh=True)
                elif key in COMMANDS:
                    live.stop()
                    try:
                        COMMANDS[key]()
                    except KeyboardInterrupt:
                        pass
                    finally:
                        live.start(refresh=True)


if __name__ == "__main__":
    import termios, tty
    old = termios.tcgetattr(sys.stdin.fileno())
    try:
        tty.setcbreak(sys.stdin.fileno())
        main()
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
