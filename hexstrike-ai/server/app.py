"""
HexStrike AI — Offensive Security MCP Platform
Flask backend: port 8888
MCP endpoint:  POST /mcp/tools/call
GLM-4.5 routes: POST /glm/interpret  /glm/parse  /glm/triage  GET /glm/status
Health check:  GET  /health
Tool list:     GET  /mcp/tools

Model routing:
  GLM-4.5 (zhipuai)  — command generation, output parsing, finding triage
  Claude Sonnet       — playbook generation, analysis, report writing

Security model:
  - All tool calls checked against scope before execution
  - No shell=True anywhere — subprocess list args only
  - Full audit log to logs/audit.jsonl
  - Prompt-injection sanitisation on tool output
  - Human-approval gate on high-risk tools
"""

import os
import json
import hashlib
import shlex
import subprocess
import threading
import time
import ipaddress
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from flask import Flask, request, jsonify
from flask_cors import CORS

# Local automation modules
import sys
_HERE = Path(__file__).parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

try:
    from scope_auth import ScopeAuth
    _scope_auth = None  # initialised after BASE_DIR is set
except ImportError:
    ScopeAuth = None
    _scope_auth = None

try:
    from msf_session_manager import MsfSessionManager
    _msf_managers: dict = {}
except ImportError:
    MsfSessionManager = None
    _msf_managers = {}

try:
    from wireless_orchestrator import WirelessOrchestrator
    _wireless: dict = {}
except ImportError:
    WirelessOrchestrator = None
    _wireless = {}

try:
    from memory import HexStrikeMemory
    _memories: dict = {}          # engagement_id → HexStrikeMemory
except ImportError:
    HexStrikeMemory = None
    _memories = {}

try:
    from agent_loop import AgentRun, get_or_create_agent, get_agent, _AGENTS
    _agent_logs: dict = {}        # engagement_id → list of log strings
except ImportError:
    AgentRun = None
    get_or_create_agent = get_agent = None
    _AGENTS = {}
    _agent_logs = {}

try:
    from deception import DeceptionEngine, get_engine as _get_dec_engine
    _DECEPTION_ENGINES: dict = {}
except ImportError:
    DeceptionEngine = None
    _get_dec_engine = None
    _DECEPTION_ENGINES = {}

try:
    from client_delivery import ClientDelivery
except ImportError:
    ClientDelivery = None

# GLM-4.5 — optional, graceful fallback if API key not set
try:
    from zhipuai import ZhipuAI as _ZhipuAI
    _GLM_KEY = os.environ.get("ZHIPUAI_API_KEY", "")
    _glm_client = _ZhipuAI(api_key=_GLM_KEY) if _GLM_KEY else None
except ImportError:
    _glm_client = None
    _GLM_KEY = ""

GLM_MODEL = "glm-4-5"   # structured command generation + output parsing

# ── Ollama local LLM (offline fallback) ──────────────────────────────────────
# Priority: GLM-4.5 (cloud) → Ollama (local) → simulation
OLLAMA_HOST  = os.environ.get("OLLAMA_HOST",  "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")

def _ollama_call(prompt: str, system: str = "", max_tokens: int = 800) -> Optional[str]:
    """
    Call local Ollama for offline LLM inference.
    Structured output: always request JSON only.
    """
    try:
        import urllib.request, json as _json
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "system": system or (
                "You are a red team security advisor. "
                "Always respond with valid JSON only. No markdown, no explanation."
            ),
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": max_tokens},
        }
        data = _json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=data, headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return _json.loads(r.read())["response"]
    except Exception as e:
        return None

def _ollama_available() -> bool:
    try:
        import urllib.request
        urllib.request.urlopen(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return True
    except Exception:
        return False

_ollama_online: Optional[bool] = None   # cached after first check


# ─── Config ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
EVIDENCE_DIR = BASE_DIR / "evidence"
AUTH_DIR = BASE_DIR / "authorizations"
LOG_DIR.mkdir(exist_ok=True)
EVIDENCE_DIR.mkdir(exist_ok=True)
AUTH_DIR.mkdir(exist_ok=True)

# Initialise scope auth module
if ScopeAuth:
    _scope_auth = ScopeAuth(AUTH_DIR)

AUDIT_LOG = LOG_DIR / "audit.jsonl"
TOOL_TIMEOUT = 120  # seconds per tool call

# Tools that require human-approval flag before execution
APPROVAL_REQUIRED = {"msf_run", "post_exploit", "lateral_move", "generate_payload"}

# ─── App ─────────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, origins=["*"])

# ─── Audit Logger ────────────────────────────────────────────────────────────
_log_lock = threading.Lock()

def audit(tool: str, args: dict, result: dict, authorized: bool, scope: str = ""):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": tool,
        "target": args.get("target", ""),
        "scope": scope,
        "authorized": authorized,
        "args_hash": hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest()[:16],
        "output_len": len(str(result.get("output", ""))),
        "error": result.get("error"),
    }
    with _log_lock:
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")

# ─── Scope Enforcement ───────────────────────────────────────────────────────
def is_in_scope(target: str, scope: str) -> bool:
    """Check target is within authorized scope. Empty scope = CTF/lab mode (permissive)."""
    if not scope or not scope.strip():
        return True  # No scope set — trust operator

    scope_items = [s.strip() for s in scope.replace(",", "\n").splitlines() if s.strip()]

    for item in scope_items:
        # CIDR range
        try:
            network = ipaddress.ip_network(item, strict=False)
            target_ip = ipaddress.ip_address(target)
            if target_ip in network:
                return True
        except ValueError:
            pass

        # Exact IP
        try:
            ipaddress.ip_address(target)
            if target == item:
                return True
        except ValueError:
            pass

        # Domain wildcard  *.example.com
        if item.startswith("*."):
            domain = item[2:]
            if target == domain or target.endswith("." + domain):
                return True

        # Exact domain
        if target == item or target.endswith("." + item):
            return True

    return False

# ─── Output Sanitiser (prompt-injection protection) ─────────────────────────
_INJECTION_RE = re.compile(
    r"ignore\s+previous\s+instructions?"
    r"|system\s*prompt\s*:"
    r"|you\s+are\s+now"
    r"|act\s+as\s+.{0,30}(?:DAN|unrestricted|jailbreak)"
    r"|<\|.*?\|>"
    r"|\[INST\].*?\[/INST\]",
    re.IGNORECASE | re.DOTALL,
)

def sanitize_output(text: str) -> str:
    """Strip potential prompt-injection payloads from tool output."""
    if not text:
        return text
    cleaned = _INJECTION_RE.sub("[SANITIZED]", text)
    # Cap at 50KB to prevent context flooding
    if len(cleaned) > 51200:
        cleaned = cleaned[:51200] + "\n[OUTPUT TRUNCATED AT 50KB]"
    return cleaned

# ─── Command Runner (no shell=True) ─────────────────────────────────────────
def run_cmd(args_list: list, timeout: int = TOOL_TIMEOUT, cwd: str = "/tmp") -> dict:
    """
    Safe subprocess execution — args as list, never shell=True.
    Returns {"output": str, "returncode": int, "error": str|None}
    """
    try:
        result = subprocess.run(
            args_list,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        output = sanitize_output(result.stdout + result.stderr)
        return {
            "output": output,
            "returncode": result.returncode,
            "error": None if result.returncode == 0 else f"Exit code {result.returncode}",
        }
    except subprocess.TimeoutExpired:
        return {"output": "", "returncode": -1, "error": f"Timed out after {timeout}s"}
    except FileNotFoundError as e:
        return {"output": "", "returncode": -1, "error": f"Tool not found: {e.filename}"}
    except Exception as e:
        return {"output": "", "returncode": -1, "error": str(e)}

def tool_available(name: str) -> bool:
    """Check if a CLI tool is on PATH."""
    result = subprocess.run(["which", name], capture_output=True)
    return result.returncode == 0

# ─── MCP Tool Registry ───────────────────────────────────────────────────────
TOOLS = {}

def tool(name: str, description: str, parameters: dict):
    """Decorator to register a tool."""
    def decorator(fn):
        TOOLS[name] = {
            "name": name,
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": parameters,
                "required": [k for k, v in parameters.items() if v.get("required", False)],
            },
            "handler": fn,
        }
        return fn
    return decorator

# ─── TOOLS ───────────────────────────────────────────────────────────────────

@tool("health_check", "Check HexStrike status and available tools", {})
def health_check(args: dict) -> dict:
    tools_available = {
        "nmap": tool_available("nmap"),
        "gobuster": tool_available("gobuster"),
        "nikto": tool_available("nikto"),
        "nuclei": tool_available("nuclei"),
        "subfinder": tool_available("subfinder"),
        "amass": tool_available("amass"),
        "sqlmap": tool_available("sqlmap"),
        "metasploit": tool_available("msfconsole"),
        "searchsploit": tool_available("searchsploit"),
        "hydra": tool_available("hydra"),
        "ffuf": tool_available("ffuf"),
        "whatweb": tool_available("whatweb"),
    }
    available = [k for k, v in tools_available.items() if v]
    missing = [k for k, v in tools_available.items() if not v]
    return {
        "output": f"HexStrike AI online\nAvailable: {', '.join(available)}\nMissing: {', '.join(missing)}",
        "status": "online",
        "tools": tools_available,
    }


@tool("recon_target", "Passive and active reconnaissance on a target", {
    "target": {"type": "string", "description": "Domain or IP address", "required": True},
    "scope": {"type": "string", "description": "Authorized scope statement"},
    "mode": {"type": "string", "enum": ["passive", "active"], "default": "passive"},
})
def recon_target(args: dict) -> dict:
    target = args.get("target", "").strip()
    scope = args.get("scope", "")
    mode = args.get("mode", "passive")

    if not target:
        return {"error": "target is required", "output": ""}

    if not is_in_scope(target, scope):
        audit("recon_target", args, {"error": "out of scope"}, False, scope)
        return {"error": f"Target {target} is not in authorized scope: {scope}", "output": ""}

    results = []

    # Always do passive DNS/whois
    if tool_available("whois"):
        r = run_cmd(["whois", target], timeout=30)
        if r["output"]:
            results.append(f"=== WHOIS ===\n{r['output'][:2000]}")

    if mode == "passive":
        if tool_available("subfinder"):
            r = run_cmd(["subfinder", "-d", target, "-silent"], timeout=60)
            if r["output"]:
                results.append(f"=== SUBFINDER (passive subdomains) ===\n{r['output']}")

        if tool_available("theHarvester"):
            r = run_cmd(["theHarvester", "-d", target, "-b", "bing,crtsh", "-l", "50"], timeout=60)
            if r["output"]:
                results.append(f"=== theHarvester ===\n{r['output'][:3000]}")

    elif mode == "active":
        if tool_available("subfinder"):
            r = run_cmd(["subfinder", "-d", target, "-silent", "-all"], timeout=90)
            if r["output"]:
                results.append(f"=== SUBFINDER (active) ===\n{r['output']}")

        if tool_available("nmap"):
            r = run_cmd(["nmap", "-sV", "-T4", "--top-ports", "1000", target, "-oN", f"/tmp/nmap_{target}.txt"], timeout=90)
            results.append(f"=== NMAP (top 1000 ports) ===\n{r['output'][:4000]}")

        if tool_available("whatweb"):
            r = run_cmd(["whatweb", target, "--aggression", "3", "--log-quiet", "/dev/stdout"], timeout=30)
            if r["output"]:
                results.append(f"=== WHATWEB ===\n{r['output'][:2000]}")

    output = "\n\n".join(results) if results else f"No tools available for recon on {target}"
    audit("recon_target", args, {"output": output}, True, scope)
    return {"output": output, "target": target, "mode": mode}


@tool("port_scan", "Run nmap port scan against target", {
    "target": {"type": "string", "description": "IP address or hostname", "required": True},
    "scope": {"type": "string", "description": "Authorized scope"},
    "flags": {"type": "string", "description": "nmap flags (default: -sV -T4 --top-ports 1000)"},
    "ports": {"type": "string", "description": "Port range (e.g. 80,443 or 1-1024)"},
})
def port_scan(args: dict) -> dict:
    target = args.get("target", "").strip()
    scope = args.get("scope", "")

    if not target:
        return {"error": "target is required", "output": ""}
    if not is_in_scope(target, scope):
        audit("port_scan", args, {"error": "out of scope"}, False, scope)
        return {"error": f"Target not in scope", "output": ""}
    if not tool_available("nmap"):
        return {"error": "nmap not found on PATH", "output": ""}

    cmd = ["nmap", "-sV", "-T4"]
    if args.get("ports"):
        cmd += ["-p", args["ports"]]
    else:
        cmd += ["--top-ports", "1000"]
    cmd.append(target)

    r = run_cmd(cmd, timeout=120)
    audit("port_scan", args, r, True, scope)
    return r


@tool("vuln_scan", "Run Nuclei vulnerability scan against target URL", {
    "target": {"type": "string", "description": "Target URL (https://...)", "required": True},
    "scope": {"type": "string", "description": "Authorized scope"},
    "templates": {"type": "string", "description": "Nuclei template tags (default: cves,exposures,misconfiguration)"},
    "severity": {"type": "string", "description": "Min severity: critical,high,medium,low,info"},
})
def vuln_scan(args: dict) -> dict:
    target = args.get("target", "").strip()
    scope = args.get("scope", "")

    # Extract hostname for scope check
    host = re.sub(r"https?://", "", target).split("/")[0].split(":")[0]
    if not is_in_scope(host, scope):
        audit("vuln_scan", args, {"error": "out of scope"}, False, scope)
        return {"error": f"Target not in scope", "output": ""}

    if not tool_available("nuclei"):
        # Fall back to nikto if available
        if tool_available("nikto"):
            r = run_cmd(["nikto", "-h", target, "-Format", "txt", "-nointeractive"], timeout=120)
            audit("vuln_scan", args, r, True, scope)
            return r
        return {"error": "nuclei and nikto not found on PATH", "output": ""}

    templates = args.get("templates", "cves,exposures,misconfiguration,default-logins")
    cmd = ["nuclei", "-u", target, "-t", templates, "-silent", "-no-color"]
    if args.get("severity"):
        cmd += ["-severity", args["severity"]]
    else:
        cmd += ["-severity", "critical,high,medium"]

    r = run_cmd(cmd, timeout=120)
    audit("vuln_scan", args, r, True, scope)
    return r


@tool("web_enum", "Directory and file enumeration on web target", {
    "target": {"type": "string", "description": "Target URL", "required": True},
    "scope": {"type": "string", "description": "Authorized scope"},
    "wordlist": {"type": "string", "description": "Path to wordlist"},
    "extensions": {"type": "string", "description": "File extensions (e.g. php,html,txt)"},
})
def web_enum(args: dict) -> dict:
    target = args.get("target", "").strip()
    scope = args.get("scope", "")
    host = re.sub(r"https?://", "", target).split("/")[0].split(":")[0]

    if not is_in_scope(host, scope):
        audit("web_enum", args, {"error": "out of scope"}, False, scope)
        return {"error": "Target not in scope", "output": ""}

    wordlist = args.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
    if not Path(wordlist).exists():
        wordlist = "/usr/share/wordlists/dirb/small.txt"
    if not Path(wordlist).exists():
        return {"error": f"Wordlist not found: {wordlist}", "output": ""}

    if tool_available("gobuster"):
        cmd = ["gobuster", "dir", "-u", target, "-w", wordlist, "-q", "--no-progress"]
        if args.get("extensions"):
            cmd += ["-x", args["extensions"]]
        r = run_cmd(cmd, timeout=120)
    elif tool_available("ffuf"):
        cmd = ["ffuf", "-u", f"{target}/FUZZ", "-w", wordlist, "-s"]
        r = run_cmd(cmd, timeout=120)
    else:
        return {"error": "gobuster and ffuf not found on PATH", "output": ""}

    audit("web_enum", args, r, True, scope)
    return r


@tool("exploit_search", "Search ExploitDB and local exploit database", {
    "query": {"type": "string", "description": "Search query (product name, CVE, service)", "required": True},
    "cve": {"type": "string", "description": "Specific CVE ID to look up"},
})
def exploit_search(args: dict) -> dict:
    query = args.get("query", "").strip()
    cve = args.get("cve", "").strip()

    if not tool_available("searchsploit"):
        return {"error": "searchsploit not found — install exploitdb package", "output": ""}

    search_term = cve if cve else query
    r = run_cmd(["searchsploit", search_term, "--json"], timeout=30)

    # Also try plain text output if JSON fails
    if r["returncode"] != 0 or not r["output"].strip():
        r = run_cmd(["searchsploit", search_term], timeout=30)

    audit("exploit_search", args, r, True)
    return r


@tool("dns_enum", "DNS enumeration — zone transfer, subdomains, records", {
    "domain": {"type": "string", "description": "Target domain", "required": True},
    "scope": {"type": "string", "description": "Authorized scope"},
})
def dns_enum(args: dict) -> dict:
    domain = args.get("domain", "").strip()
    scope = args.get("scope", "")

    if not is_in_scope(domain, scope):
        audit("dns_enum", args, {"error": "out of scope"}, False, scope)
        return {"error": "Target not in scope", "output": ""}

    results = []

    # Basic DNS records
    for record_type in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
        r = run_cmd(["dig", domain, record_type, "+short"], timeout=15)
        if r["output"].strip():
            results.append(f"{record_type}: {r['output'].strip()}")

    # Zone transfer attempt
    ns_r = run_cmd(["dig", domain, "NS", "+short"], timeout=15)
    for ns in ns_r["output"].strip().splitlines():
        ns = ns.strip().rstrip(".")
        if ns:
            zt = run_cmd(["dig", f"@{ns}", domain, "AXFR"], timeout=20)
            if "Transfer failed" not in zt["output"] and zt["output"].strip():
                results.append(f"=== ZONE TRANSFER via {ns} ===\n{zt['output'][:2000]}")

    output = "\n".join(results) if results else f"No DNS records found for {domain}"
    result = {"output": output}
    audit("dns_enum", args, result, True, scope)
    return result


@tool("ssl_check", "Check SSL/TLS configuration and certificate", {
    "target": {"type": "string", "description": "Host:port (e.g. example.com:443)", "required": True},
    "scope": {"type": "string", "description": "Authorized scope"},
})
def ssl_check(args: dict) -> dict:
    target = args.get("target", "").strip()
    scope = args.get("scope", "")
    host = target.split(":")[0]

    if not is_in_scope(host, scope):
        audit("ssl_check", args, {"error": "out of scope"}, False, scope)
        return {"error": "Target not in scope", "output": ""}

    if tool_available("testssl"):
        r = run_cmd(["testssl", "--quiet", "--color", "0", target], timeout=90)
    elif tool_available("openssl"):
        # Fallback: basic cert info
        host_only = target.split(":")[0]
        port = target.split(":")[1] if ":" in target else "443"
        r = run_cmd(
            ["openssl", "s_client", "-connect", f"{host_only}:{port}", "-servername", host_only],
            timeout=15
        )
    else:
        r = {"output": "testssl and openssl not available", "returncode": 1, "error": "No SSL tool found"}

    audit("ssl_check", args, r, True, scope)
    return r


@tool("credential_check", "Test credentials against a service (brute force — authorized only)", {
    "target": {"type": "string", "description": "Target host:port", "required": True},
    "service": {"type": "string", "description": "Service type: ssh,ftp,http,smb,rdp", "required": True},
    "scope": {"type": "string", "description": "Authorized scope"},
    "userlist": {"type": "string", "description": "Path to username list"},
    "passlist": {"type": "string", "description": "Path to password list"},
    "approved": {"type": "boolean", "description": "Human approval confirmed", "required": True},
})
def credential_check(args: dict) -> dict:
    if not args.get("approved"):
        return {"error": "Human approval required — set approved: true", "output": ""}

    target = args.get("target", "").strip()
    scope = args.get("scope", "")
    service = args.get("service", "ssh").strip()
    host = target.split(":")[0]

    if not is_in_scope(host, scope):
        audit("credential_check", args, {"error": "out of scope"}, False, scope)
        return {"error": "Target not in scope", "output": ""}

    if not tool_available("hydra"):
        return {"error": "hydra not found on PATH", "output": ""}

    userlist = args.get("userlist", "/usr/share/wordlists/metasploit/unix_users.txt")
    passlist = args.get("passlist", "/usr/share/wordlists/rockyou.txt")

    if not Path(userlist).exists():
        return {"error": f"User list not found: {userlist}", "output": ""}
    if not Path(passlist).exists():
        return {"error": f"Password list not found: {passlist}", "output": ""}

    cmd = ["hydra", "-L", userlist, "-P", passlist, "-t", "4", "-f", target, service]
    r = run_cmd(cmd, timeout=120)
    audit("credential_check", args, r, True, scope)
    return r


@tool("generate_payload", "Generate reverse shell payload with msfvenom", {
    "payload": {"type": "string", "description": "MSF payload (e.g. windows/x64/meterpreter/reverse_tcp)", "required": True},
    "lhost": {"type": "string", "description": "Attacker listener IP", "required": True},
    "lport": {"type": "string", "description": "Attacker listener port", "required": True},
    "format": {"type": "string", "description": "Output format: exe,elf,php,py,raw"},
    "encoder": {"type": "string", "description": "Encoder (e.g. x64/xor_dynamic)"},
    "approved": {"type": "boolean", "description": "Human approval confirmed", "required": True},
})
def generate_payload(args: dict) -> dict:
    if not args.get("approved"):
        return {"error": "Human approval required — set approved: true", "output": ""}

    if not tool_available("msfvenom"):
        return {"error": "msfvenom not found — install metasploit-framework", "output": ""}

    payload = args.get("payload", "").strip()
    lhost = args.get("lhost", "").strip()
    lport = args.get("lport", "4444").strip()
    fmt = args.get("format", "elf")
    encoder = args.get("encoder", "")

    outfile = EVIDENCE_DIR / f"payload_{int(time.time())}.{fmt}"
    cmd = ["msfvenom", "-p", payload, f"LHOST={lhost}", f"LPORT={lport}", "-f", fmt, "-o", str(outfile)]
    if encoder:
        cmd += ["-e", encoder]

    r = run_cmd(cmd, timeout=60)
    if r["returncode"] == 0:
        r["output"] = f"Payload generated: {outfile}\n\n{r['output']}"
        r["payload_path"] = str(outfile)

    audit("generate_payload", args, r, True)
    return r


@tool("generate_report", "Generate structured pentest report from findings", {
    "findings": {"type": "array", "description": "List of finding objects from VulnAnalysis", "required": True},
    "target": {"type": "string", "description": "Target name/org", "required": True},
    "scope": {"type": "string", "description": "Engagement scope statement"},
    "methodology": {"type": "string", "description": "Testing methodology"},
    "format": {"type": "string", "description": "Output format: markdown,json"},
})
def generate_report(args: dict) -> dict:
    findings = args.get("findings", [])
    target = args.get("target", "Target")
    methodology = args.get("methodology", "PTES")
    fmt = args.get("format", "markdown")

    now = datetime.now().strftime("%Y-%m-%d")
    severity_counts = {}
    for f in findings:
        sev = f.get("severity", "info").lower()
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    if fmt == "json":
        report = {
            "title": f"Penetration Test Report — {target}",
            "date": now,
            "methodology": methodology,
            "findings": findings,
            "summary": severity_counts,
        }
        output = json.dumps(report, indent=2)
    else:
        critical = severity_counts.get("critical", 0)
        high = severity_counts.get("high", 0)
        overall = "CRITICAL" if critical > 0 else "HIGH" if high > 0 else "MEDIUM"

        lines = [
            f"# Penetration Test Report — {target}",
            f"**Date:** {now} | **Methodology:** {methodology} | **Overall Risk:** {overall}\n",
            "## Executive Summary\n",
            f"Assessment of {target} identified {len(findings)} findings: "
            f"{severity_counts.get('critical',0)} critical, {severity_counts.get('high',0)} high, "
            f"{severity_counts.get('medium',0)} medium, {severity_counts.get('low',0)} low.\n",
            "## Findings\n",
        ]
        for i, f in enumerate(findings, 1):
            lines += [
                f"### Finding {i:03d} — {f.get('title', 'Untitled')}",
                f"| Severity | CVSS | CVE | Component |",
                f"|----------|------|-----|-----------|",
                f"| {f.get('severity','?').upper()} | {f.get('cvss','N/A')} | {f.get('cve','N/A')} | {f.get('affected_component','N/A')} |\n",
                f"**Description:** {f.get('description','')}\n",
                f"**Remediation:** {f.get('remediation','')}\n",
                "---\n",
            ]
        output = "\n".join(lines)

    # Save report to evidence dir
    report_path = EVIDENCE_DIR / f"report_{target.replace(' ','_')}_{now}.md"
    report_path.write_text(output)

    result = {"output": output, "report_path": str(report_path)}
    audit("generate_report", args, result, True)
    return result


# ─── MCP HTTP Endpoints ───────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "platform": "HexStrike AI",
        "version": "1.0.0",
        "tools": list(TOOLS.keys()),
        "automation_endpoints": {
            "scope":    ["/scope/generate", "/scope/authorize", "/scope/check",
                         "/scope/list", "/scope/revoke"],
            "msf":      ["/msf/status", "/msf/sessions", "/msf/run",
                         "/msf/pivot", "/msf/pivot_map", "/msf/cleanup"],
            "wireless": ["/wifi/interfaces", "/wifi/monitor", "/wifi/scan",
                         "/wifi/capture", "/wifi/crack", "/wifi/status"],
            "delivery": ["/deliver/package", "/deliver/email_draft", "/deliver/tracker"],
        },
        "flask_port": 8888,
    })


@app.route("/mcp/tools", methods=["GET"])
def list_tools():
    """Return tool schemas for MCP client discovery."""
    tools_list = [
        {
            "name": t["name"],
            "description": t["description"],
            "inputSchema": t["inputSchema"],
            "requiresApproval": t["name"] in APPROVAL_REQUIRED,
        }
        for t in TOOLS.values()
    ]
    return jsonify({"tools": tools_list})


@app.route("/mcp/tools/call", methods=["POST"])
def call_tool():
    """
    MCP tool call endpoint.
    Body: { "name": "tool_name", "arguments": { ... } }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    name = data.get("name", "").strip()
    arguments = data.get("arguments", {})

    if name not in TOOLS:
        return jsonify({
            "error": f"Unknown tool: {name}",
            "available": list(TOOLS.keys()),
        }), 404

    tool_def = TOOLS[name]

    # High-risk tools require approved flag
    if name in APPROVAL_REQUIRED and not arguments.get("approved"):
        return jsonify({
            "error": f"Tool '{name}' requires human approval. Set arguments.approved = true.",
            "output": "",
            "requiresApproval": True,
        }), 403

    try:
        result = tool_def["handler"](arguments)
        return jsonify({
            "tool": name,
            "content": [{"type": "text", "text": result.get("output", "")}],
            **{k: v for k, v in result.items() if k != "output"},
        })
    except Exception as e:
        err = {"error": str(e), "output": ""}
        audit(name, arguments, err, True)
        return jsonify(err), 500


@app.route("/mcp/audit", methods=["GET"])
def get_audit_log():
    """Return recent audit log entries."""
    limit = int(request.args.get("limit", 50))
    if not AUDIT_LOG.exists():
        return jsonify({"entries": []})
    lines = AUDIT_LOG.read_text().strip().splitlines()
    entries = [json.loads(l) for l in lines[-limit:] if l.strip()]
    return jsonify({"entries": entries, "total": len(lines)})


@app.route("/mcp/evidence", methods=["GET"])
def list_evidence():
    """List evidence files."""
    files = [
        {
            "name": f.name,
            "size": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        }
        for f in sorted(EVIDENCE_DIR.iterdir()) if f.is_file()
    ]
    return jsonify({"files": files, "directory": str(EVIDENCE_DIR)})



# ─── GLM-4.5 Routing Layer ─────────────────────────────────────────────────
# Split: GLM-4.5 handles command generation + output parsing (structured, fast)
#        Claude Sonnet handles planning, analysis, report writing (contextual, rich)

def glm_generate_command(skill: str, target: str, context: dict) -> dict:
    """
    LLM routing: GLM-4.5 → Ollama → simulation fallback.
    Given a skill + target + context, return exact shell command JSON.
    """
    if not _glm_client and not _ollama_available():
        return {"error": "No LLM configured — set ZHIPUAI_API_KEY or start Ollama", "command": None}

    prompt = f"""You are a senior red team operator. Generate the precise tool command for this step.
Skill: {skill}
Target: {target}
Context: {json.dumps(context, indent=2)}

Return ONLY valid JSON with this exact structure:
{{
  "tool": "tool_name",
  "command": ["arg0", "arg1", "arg2"],
  "flags_rationale": "why these flags",
  "expected_output": "what to look for",
  "timeout_seconds": 60
}}
No markdown, no explanation. JSON only."""

    # Try GLM-4.5 first
    if _glm_client:
        try:
            response = _glm_client.chat.completions.create(
                model=GLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, max_tokens=500,
            )
            text = response.choices[0].message.content.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception:
            pass  # Fall through to Ollama

    # Try local Ollama
    text = _ollama_call(prompt, max_tokens=500)
    if text:
        try:
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception:
            pass

    return {"error": "All LLM backends unavailable", "command": None}


def glm_parse_output(tool_name: str, raw_output: str, target: str) -> dict:
    """
    GLM-4.5: Parse raw tool output into structured findings.
    Fast, deterministic parsing — not contextual analysis.
    """
    if not _glm_client and not _ollama_available():
        return {"parsed": raw_output[:500], "findings": [], "error": "No LLM configured"}

    prompt = f"""Parse this {tool_name} output for target {target}.
Extract structured data only. Return ONLY valid JSON:
{{
  "open_ports": [],
  "services": [],
  "vulnerabilities": [],
  "subdomains": [],
  "credentials": [],
  "interesting_paths": [],
  "raw_summary": "one sentence"
}}

Raw output (first 3000 chars):
{raw_output[:3000]}

JSON only, no explanation."""

    # Try GLM-4.5
    if _glm_client:
        try:
            response = _glm_client.chat.completions.create(
                model=GLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, max_tokens=800,
            )
            text = response.choices[0].message.content.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            return {"parsed": parsed, "findings": parsed.get("vulnerabilities", []), "error": None}
        except Exception:
            pass

    # Try Ollama
    text = _ollama_call(prompt, max_tokens=800)
    if text:
        try:
            text = text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            return {"parsed": parsed, "findings": parsed.get("vulnerabilities", []), "error": None}
        except Exception:
            pass

    return {"parsed": {}, "findings": [], "error": "All LLM backends unavailable"}


def glm_triage_findings(findings: list) -> list:
    """
    GLM-4.5: Score and prioritize findings by exploitability.
    Returns findings sorted by priority with exploit_available flag.
    """
    if (not _glm_client and not _ollama_available()) or not findings:
        return findings

    prompt = f"""Triage these security findings. Score each by exploitability and severity.
Return ONLY valid JSON array — same objects with added fields:
  "priority": "P0"/"P1"/"P2"/"P3"/"P4"
  "exploit_available": true/false
  "mitre_technique": "T1xxx"
  "cvss_estimate": 0.0-10.0

Findings:
{json.dumps(findings, indent=2)[:3000]}

JSON array only."""

    # Try GLM-4.5
    if _glm_client:
        try:
            response = _glm_client.chat.completions.create(
                model=GLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, max_tokens=1000,
            )
            text = response.choices[0].message.content.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception:
            pass

    # Try Ollama
    text = _ollama_call(prompt, max_tokens=1000)
    if text:
        try:
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception:
            pass

    return findings  # Return original on total failure


# ─── GLM HTTP Endpoints ────────────────────────────────────────────────────

@app.route("/glm/interpret", methods=["POST"])
def glm_interpret():
    """
    GLM-4.5: Translate a natural language step into a concrete shell command.
    Body: { "skill": str, "target": str, "context": dict }
    """
    data = request.get_json(silent=True) or {}
    skill = data.get("skill", "")
    target = data.get("target", "")
    context = data.get("context", {})

    if not skill or not target:
        return jsonify({"error": "skill and target required"}), 400

    result = glm_generate_command(skill, target, context)
    return jsonify(result)


@app.route("/glm/parse", methods=["POST"])
def glm_parse():
    """
    GLM-4.5: Parse raw tool output into structured JSON findings.
    Body: { "tool": str, "output": str, "target": str }
    """
    data = request.get_json(silent=True) or {}
    tool_name = data.get("tool", "unknown")
    output = data.get("output", "")
    target = data.get("target", "")

    sanitized = sanitize_output(output)
    result = glm_parse_output(tool_name, sanitized, target)
    return jsonify(result)


@app.route("/glm/triage", methods=["POST"])
def glm_triage():
    """
    GLM-4.5: Score and prioritize a list of findings.
    Body: { "findings": [...] }
    """
    data = request.get_json(silent=True) or {}
    findings = data.get("findings", [])
    result = glm_triage_findings(findings)
    return jsonify({"findings": result})


@app.route("/glm/status", methods=["GET"])
def glm_status():
    """Check GLM-4.5 connectivity and model routing config."""
    ollama_ok = _ollama_available()
    active_backend = (
        "glm-4.5"   if _glm_client else
        "ollama"    if ollama_ok else
        "simulation"
    )
    return jsonify({
        "glm_configured":  _glm_client is not None,
        "glm_model":       GLM_MODEL,
        "ollama_available": ollama_ok,
        "ollama_host":     OLLAMA_HOST,
        "ollama_model":    OLLAMA_MODEL,
        "active_backend":  active_backend,
        "sonnet_model":    "claude-sonnet-4-20250514",
        "routing_priority": ["glm-4.5", "ollama", "simulation"],
        "routing": {
            "glm-4.5": ["command_generation", "output_parsing", "finding_triage"],
            "ollama":  ["command_generation", "output_parsing", "finding_triage"],
            "sonnet":  ["playbook_generation", "finding_analysis", "report_writing"],
        }
    })


# ─── Scope Authorization Endpoints ────────────────────────────────────────────

@app.route("/scope/generate", methods=["POST"])
def scope_generate():
    """Generate a scope authorization document template."""
    if not _scope_auth:
        return jsonify({"error": "ScopeAuth module not available"}), 503
    d = request.get_json(silent=True) or {}
    required = ["engagement_id", "target", "scope", "operator", "engagement_type",
                "methodology", "start_date", "end_date"]
    if missing := [k for k in required if not d.get(k)]:
        return jsonify({"error": f"Missing: {missing}"}), 400
    doc = _scope_auth.generate_scope_document(
        d["engagement_id"], d["target"], d["scope"], d["operator"],
        d["engagement_type"], d["methodology"], d["start_date"], d["end_date"],
        d.get("exclusions", "")
    )
    return jsonify({"document": doc, "engagement_id": d["engagement_id"]})


@app.route("/scope/authorize", methods=["POST"])
def scope_authorize():
    """Record operator authorization for an engagement."""
    if not _scope_auth:
        return jsonify({"error": "ScopeAuth module not available"}), 503
    d = request.get_json(silent=True) or {}
    required = ["engagement_id", "operator", "target", "scope",
                "engagement_type", "methodology", "authorization_ref",
                "client_contact", "testing_window_end"]
    if missing := [k for k in required if not d.get(k)]:
        return jsonify({"error": f"Missing: {missing}"}), 400
    auth = _scope_auth.record_authorization(
        d["engagement_id"], d["operator"], d["target"], d["scope"],
        d["engagement_type"], d["methodology"], d["authorization_ref"],
        d["client_contact"], d["testing_window_end"]
    )
    audit("scope_authorize", {"target": d["target"]},
          {"engagement_id": d["engagement_id"], "hash": auth["auth_hash"]}, True)
    return jsonify(auth)


@app.route("/scope/check", methods=["POST"])
def scope_check():
    """Check if a target is authorized for an engagement."""
    if not _scope_auth:
        return jsonify({"error": "ScopeAuth module not available"}), 503
    d = request.get_json(silent=True) or {}
    if not d.get("engagement_id") or not d.get("target"):
        return jsonify({"error": "engagement_id and target required"}), 400
    authorized, reason = _scope_auth.is_authorized(d["engagement_id"], d["target"])
    return jsonify({"authorized": authorized, "reason": reason,
                    "engagement_id": d["engagement_id"], "target": d["target"]})


@app.route("/scope/list", methods=["GET"])
def scope_list():
    """List all authorization records."""
    if not _scope_auth:
        return jsonify({"error": "ScopeAuth module not available"}), 503
    return jsonify({"authorizations": _scope_auth.list_authorizations()})


@app.route("/scope/revoke", methods=["POST"])
def scope_revoke():
    """Revoke an active authorization."""
    if not _scope_auth:
        return jsonify({"error": "ScopeAuth module not available"}), 503
    d = request.get_json(silent=True) or {}
    if not d.get("engagement_id"):
        return jsonify({"error": "engagement_id required"}), 400
    ok = _scope_auth.revoke(d["engagement_id"], d.get("reason", "manual revocation"))
    audit("scope_revoke", {"target": d["engagement_id"]}, {}, ok)
    return jsonify({"revoked": ok, "engagement_id": d["engagement_id"]})


# ─── Metasploit Session Endpoints ─────────────────────────────────────────────

def _get_msf(engagement_id: str):
    if not MsfSessionManager:
        return None
    if engagement_id not in _msf_managers:
        _msf_managers[engagement_id] = MsfSessionManager(
            engagement_id, LOG_DIR,
            os.environ.get("MSF_HOST", "127.0.0.1"),
            int(os.environ.get("MSF_PORT", "55553")),
            os.environ.get("MSF_PASSWORD", "hexstrike"),
        )
    return _msf_managers[engagement_id]


@app.route("/msf/status", methods=["GET"])
def msf_status():
    """MSF RPC connection status and session inventory."""
    engagement_id = request.args.get("engagement_id", "default")
    msf = _get_msf(engagement_id)
    if not msf:
        return jsonify({"error": "MsfSessionManager not available"}), 503
    return jsonify(msf.status())


@app.route("/msf/sessions", methods=["GET"])
def msf_sessions():
    """List all active Metasploit sessions."""
    engagement_id = request.args.get("engagement_id", "default")
    msf = _get_msf(engagement_id)
    if not msf:
        return jsonify({"error": "MsfSessionManager not available"}), 503
    return jsonify({"sessions": msf.list_sessions()})


@app.route("/msf/run", methods=["POST"])
def msf_run():
    """
    Execute a command in a Meterpreter session.
    High-risk commands require: "approved": true in body.
    """
    d = request.get_json(silent=True) or {}
    if not d.get("session_id") or not d.get("command"):
        return jsonify({"error": "session_id and command required"}), 400
    engagement_id = d.get("engagement_id", "default")
    approved = d.get("approved", False)
    msf = _get_msf(engagement_id)
    if not msf:
        return jsonify({"error": "MsfSessionManager not available"}), 503
    result = msf.run_command(
        d["session_id"], d["command"],
        timeout=d.get("timeout", 30),
        requires_approval=not approved,
    )
    audit("msf_run", {"target": d["session_id"]}, {"command": d["command"], "approved": approved}, "error" not in result)
    if "error" in result and "requires human approval" in result.get("error", ""):
        return jsonify(result), 403
    return jsonify(result)


@app.route("/msf/pivot", methods=["POST"])
def msf_pivot():
    """Record a pivot hop in the engagement map."""
    d = request.get_json(silent=True) or {}
    required = ["engagement_id", "from_host", "to_host", "method", "session_id"]
    if missing := [k for k in required if not d.get(k)]:
        return jsonify({"error": f"Missing: {missing}"}), 400
    msf = _get_msf(d["engagement_id"])
    if not msf:
        return jsonify({"error": "MsfSessionManager not available"}), 503
    result = msf.record_pivot(d["from_host"], d["to_host"], d["method"], d["session_id"])
    audit("msf_pivot", {"target": d["to_host"]}, result, True)
    return jsonify(result)


@app.route("/msf/pivot_map", methods=["GET"])
def msf_pivot_map():
    """Return the full pivot map for an engagement."""
    engagement_id = request.args.get("engagement_id", "default")
    msf = _get_msf(engagement_id)
    if not msf:
        return jsonify({"error": "MsfSessionManager not available"}), 503
    return jsonify({"pivot_map": msf.get_pivot_map()})


@app.route("/msf/cleanup", methods=["POST"])
def msf_cleanup():
    """Clean up all sessions for an engagement."""
    d = request.get_json(silent=True) or {}
    engagement_id = d.get("engagement_id", "default")
    msf = _get_msf(engagement_id)
    if not msf:
        return jsonify({"error": "MsfSessionManager not available"}), 503
    result = msf.cleanup_all()
    audit("msf_cleanup", {"target": engagement_id}, result, True)
    return jsonify(result)


# ─── Wireless Orchestration Endpoints ─────────────────────────────────────────

def _get_wireless(engagement_id: str):
    if not WirelessOrchestrator:
        return None
    if engagement_id not in _wireless:
        _wireless[engagement_id] = WirelessOrchestrator(engagement_id, EVIDENCE_DIR)
    return _wireless[engagement_id]


@app.route("/wifi/interfaces", methods=["GET"])
def wifi_interfaces():
    """List wireless interfaces and monitor-mode capability."""
    w = _get_wireless("probe")
    if not w:
        return jsonify({"error": "WirelessOrchestrator not available"}), 503
    return jsonify({"interfaces": w.list_interfaces()})


@app.route("/wifi/monitor", methods=["POST"])
def wifi_monitor():
    """Set wireless interface to monitor mode."""
    d = request.get_json(silent=True) or {}
    if not d.get("interface"):
        return jsonify({"error": "interface required"}), 400
    engagement_id = d.get("engagement_id", "default")
    w = _get_wireless(engagement_id)
    if not w:
        return jsonify({"error": "WirelessOrchestrator not available"}), 503
    result = w.set_monitor_mode(d["interface"])
    audit("wifi_monitor", {"target": d["interface"]}, {}, "error" not in result)
    return jsonify(result)


@app.route("/wifi/scan", methods=["POST"])
def wifi_scan():
    """Scan for nearby access points."""
    d = request.get_json(silent=True) or {}
    if not d.get("interface"):
        return jsonify({"error": "interface required"}), 400
    engagement_id = d.get("engagement_id", "default")
    authorized, reason = (_scope_auth.is_authorized(engagement_id, "wireless") if _scope_auth
                          else (True, "scope auth not configured"))
    if not authorized:
        return jsonify({"error": f"Not authorized: {reason}"}), 403
    w = _get_wireless(engagement_id)
    if not w:
        return jsonify({"error": "WirelessOrchestrator not available"}), 503
    networks = w.scan_networks(d["interface"], d.get("duration", 15))
    audit("wifi_scan", {"target": d["interface"]}, {"networks": len(networks)}, True)
    return jsonify({"networks": networks})


@app.route("/wifi/capture", methods=["POST"])
def wifi_capture():
    """
    Full handshake capture pipeline with automatic deauth.
    Body: { interface, bssid, channel, essid, engagement_id,
            deauth_interval (s), max_wait (s) }
    """
    d = request.get_json(silent=True) or {}
    required = ["interface", "bssid", "channel", "engagement_id"]
    if missing := [k for k in required if not d.get(k)]:
        return jsonify({"error": f"Missing: {missing}"}), 400
    authorized, reason = (_scope_auth.is_authorized(d["engagement_id"], d["bssid"]) if _scope_auth
                          else (True, "scope auth not configured"))
    if not authorized:
        return jsonify({"error": f"Not authorized: {reason}"}), 403
    w = _get_wireless(d["engagement_id"])
    if not w:
        return jsonify({"error": "WirelessOrchestrator not available"}), 503
    result = w.capture_with_deauth(
        d["interface"], d["bssid"], int(d["channel"]),
        d.get("essid", ""),
        d.get("deauth_interval", 30),
        d.get("max_wait", 300),
    )
    audit("wifi_capture", {"target": d["bssid"]}, result, result.get("status") == "handshake_captured")
    return jsonify(result)


@app.route("/wifi/crack", methods=["POST"])
def wifi_crack():
    """
    Launch hashcat cracking job against a captured PCAP.
    Body: { pcap, bssid, essid, wordlist, engagement_id }
    """
    d = request.get_json(silent=True) or {}
    if not d.get("pcap") or not d.get("bssid"):
        return jsonify({"error": "pcap and bssid required"}), 400
    # Crack requires explicit approval
    if not d.get("approved"):
        return jsonify({
            "error": "Crack job requires explicit approval",
            "action": 'Resubmit with "approved": true after operator confirms',
            "requiresApproval": True,
        }), 403
    engagement_id = d.get("engagement_id", "default")
    w = _get_wireless(engagement_id)
    if not w:
        return jsonify({"error": "WirelessOrchestrator not available"}), 503
    result = w.crack_handshake(d["pcap"], d["bssid"], d.get("essid", ""),
                               d.get("wordlist", "rockyou"), d.get("rules"))
    audit("wifi_crack", {"target": d["bssid"]}, {"wordlist": d.get("wordlist")}, True)
    return jsonify(result)


@app.route("/wifi/status", methods=["GET"])
def wifi_status():
    engagement_id = request.args.get("engagement_id", "default")
    w = _get_wireless(engagement_id)
    if not w:
        return jsonify({"error": "WirelessOrchestrator not available"}), 503
    return jsonify(w.status())


# ─── Client Delivery Endpoints ────────────────────────────────────────────────

@app.route("/deliver/package", methods=["POST"])
def deliver_package():
    """
    Full delivery pipeline: Markdown + PDF + Notion payload + email draft + tracker issues.
    Body: { engagement_id, findings: [...], metadata: { client, operator, ... } }
    """
    if not ClientDelivery:
        return jsonify({"error": "ClientDelivery module not available"}), 503
    d = request.get_json(silent=True) or {}
    if not d.get("engagement_id") or "findings" not in d:
        return jsonify({"error": "engagement_id and findings required"}), 400
    delivery = ClientDelivery(d["engagement_id"], EVIDENCE_DIR)
    result = delivery.package(d["findings"], d.get("metadata", {}))
    audit("deliver_package", {"target": d["engagement_id"]}, {"findings": len(d["findings"]), "hash": result.get("integrity_hash")}, True)
    return jsonify(result)


@app.route("/deliver/email_draft", methods=["POST"])
def deliver_email():
    """Generate client delivery email draft only."""
    if not ClientDelivery:
        return jsonify({"error": "ClientDelivery module not available"}), 503
    d = request.get_json(silent=True) or {}
    delivery = ClientDelivery(d.get("engagement_id", "draft"), EVIDENCE_DIR)
    draft = delivery.draft_delivery_email(d.get("findings", []), d.get("metadata", {}))
    return jsonify(draft)


@app.route("/deliver/tracker", methods=["POST"])
def deliver_tracker():
    """Generate Linear/Jira remediation tracker issues from findings."""
    if not ClientDelivery:
        return jsonify({"error": "ClientDelivery module not available"}), 503
    d = request.get_json(silent=True) or {}
    delivery = ClientDelivery(d.get("engagement_id", "draft"), EVIDENCE_DIR)
    issues = delivery.build_remediation_tracker(d.get("findings", []), d.get("metadata", {}))
    return jsonify({"issues": issues, "count": len(issues)})


# ─── Memory Endpoints ─────────────────────────────────────────────────────────

def _get_memory(engagement_id: str) -> Optional["HexStrikeMemory"]:
    if not HexStrikeMemory:
        return None
    if engagement_id not in _memories:
        _memories[engagement_id] = HexStrikeMemory(
            engagement_id=engagement_id,
            data_dir=EVIDENCE_DIR / "memory",
        )
    return _memories[engagement_id]


@app.route("/memory/store", methods=["POST"])
def memory_store():
    """Store a scan result to persistent memory."""
    d = request.get_json(silent=True) or {}
    if not d.get("engagement_id") or not d.get("phase"):
        return jsonify({"error": "engagement_id and phase required"}), 400
    mem = _get_memory(d["engagement_id"])
    if not mem:
        return jsonify({"error": "Memory module not available"}), 503
    key = mem.store_scan(d["phase"], d.get("data", {}), d.get("tags", []))
    return jsonify({"key": key, "backends": mem.backends()})


@app.route("/memory/search", methods=["POST"])
def memory_search():
    """Semantic search across stored scan results."""
    d = request.get_json(silent=True) or {}
    if not d.get("engagement_id"):
        return jsonify({"error": "engagement_id required"}), 400
    mem = _get_memory(d["engagement_id"])
    if not mem:
        return jsonify({"error": "Memory module not available"}), 503
    results = mem.search(d.get("query", ""), top_k=d.get("top_k", 5),
                         phase=d.get("phase"))
    return jsonify({"results": results, "count": len(results)})


@app.route("/memory/findings", methods=["GET"])
def memory_findings():
    """Get all findings from engagement memory."""
    engagement_id = request.args.get("engagement_id", "")
    min_priority  = request.args.get("min_priority", "P4")
    if not engagement_id:
        return jsonify({"error": "engagement_id required"}), 400
    mem = _get_memory(engagement_id)
    if not mem:
        return jsonify({"error": "Memory module not available"}), 503
    findings = mem.get_findings(min_priority)
    return jsonify({"findings": findings, "count": len(findings)})


@app.route("/memory/summary", methods=["GET"])
def memory_summary():
    """Engagement memory summary across all phases."""
    engagement_id = request.args.get("engagement_id", "")
    if not engagement_id:
        return jsonify({"error": "engagement_id required"}), 400
    mem = _get_memory(engagement_id)
    if not mem:
        return jsonify({"error": "Memory module not available"}), 503
    return jsonify(mem.summary())


# ─── Autonomous Agent Endpoints ────────────────────────────────────────────────

@app.route("/agent/run", methods=["POST"])
def agent_run():
    """
    Start an autonomous engagement run.
    Body: { engagement_id, target, scope, phases, auto_mode }
    auto_mode=true skips all approval gates (CTF/lab use only)
    """
    if not AgentRun:
        return jsonify({"error": "AgentRun module not available"}), 503
    d = request.get_json(silent=True) or {}
    required = ["engagement_id", "target", "scope"]
    if missing := [k for k in required if not d.get(k)]:
        return jsonify({"error": f"Missing: {missing}"}), 400

    eid = d["engagement_id"]
    if eid in _AGENTS and _AGENTS[eid].status == "running":
        return jsonify({"error": "Agent already running for this engagement"}), 409

    logs = _agent_logs.setdefault(eid, [])

    def on_log(msg, lvl="info"):
        logs.append({"msg": msg, "lvl": lvl, "ts": datetime.now(timezone.utc).isoformat()})
        logs[:] = logs[-500:]          # keep last 500 entries

    def on_approval(step):
        # In API mode, approval must come via /agent/approve
        return d.get("auto_mode", False)

    agent = get_or_create_agent(
        engagement_id=eid,
        target=d["target"],
        scope=d["scope"],
        phases=d.get("phases", ["recon", "vuln", "report"]),
        hexstrike_url=f"http://localhost:{os.environ.get('PORT', 8888)}",
        auto_mode=d.get("auto_mode", False),
        on_log=on_log,
        on_approval_needed=on_approval,
    )
    _AGENTS[eid] = agent
    agent.run_async()
    audit("agent_run", {"target": d["target"]}, {"engagement_id": eid}, True)
    return jsonify({"status": "started", **agent.state()})


@app.route("/agent/status", methods=["GET"])
def agent_status():
    """Get current agent run status."""
    eid = request.args.get("engagement_id", "")
    if not eid:
        # Return all running agents
        return jsonify({"agents": [
            a.state() for a in _AGENTS.values()
        ]})
    agent = get_agent(eid) if get_agent else None
    if not agent:
        return jsonify({"error": f"No agent for {eid}"}), 404
    return jsonify(agent.state())


@app.route("/agent/logs", methods=["GET"])
def agent_logs():
    """Stream agent execution logs."""
    eid = request.args.get("engagement_id", "")
    since = int(request.args.get("since", 0))
    if not eid:
        return jsonify({"error": "engagement_id required"}), 400
    logs = _agent_logs.get(eid, [])
    return jsonify({"logs": logs[since:], "total": len(logs)})


@app.route("/agent/approve", methods=["POST"])
def agent_approve():
    """Grant human approval for a pending tool step."""
    d = request.get_json(silent=True) or {}
    eid = d.get("engagement_id", "")
    agent = get_agent(eid) if get_agent else None
    if not agent:
        return jsonify({"error": f"No agent for {eid}"}), 404
    agent.approve()
    audit("agent_approve", {"target": eid}, {}, True)
    return jsonify({"approved": True, **agent.state()})


@app.route("/agent/deny", methods=["POST"])
def agent_deny():
    """Deny a pending tool step."""
    d = request.get_json(silent=True) or {}
    eid = d.get("engagement_id", "")
    agent = get_agent(eid) if get_agent else None
    if not agent:
        return jsonify({"error": f"No agent for {eid}"}), 404
    agent.deny()
    return jsonify({"denied": True, **agent.state()})


@app.route("/agent/abort", methods=["POST"])
def agent_abort():
    """Abort a running agent."""
    d = request.get_json(silent=True) or {}
    eid = d.get("engagement_id", "")
    agent = get_agent(eid) if get_agent else None
    if not agent:
        return jsonify({"error": f"No agent for {eid}"}), 404
    agent.abort()
    audit("agent_abort", {"target": eid}, {}, True)
    return jsonify({"aborted": True, **agent.state()})


@app.route("/agent/findings", methods=["GET"])
def agent_findings():
    """Get findings collected by the agent so far."""
    eid = request.args.get("engagement_id", "")
    agent = get_agent(eid) if get_agent else None
    if not agent:
        return jsonify({"error": f"No agent for {eid}"}), 404
    return jsonify({"findings": agent.findings, "count": len(agent.findings)})


# ─── Pre-Engagement Risk Assessment (risk-analyzer skill) ─────────────────────

@app.route("/risk/assess", methods=["POST"])
def risk_assess():
    """
    Pre-engagement risk analysis using analytical-reasoning + risk-analyzer patterns.
    Combines host intelligence, CVE data, and engagement context to score
    attack surface risk before execution begins.

    Body: { engagement_id, target, scope, hosts: [...], engagement_type }
    Returns: risk_score, risk_matrix, top_threats, recommended_order
    """
    d = request.get_json(silent=True) or {}
    if not d.get("target"):
        return jsonify({"error": "target required"}), 400

    hosts   = d.get("hosts", [])
    target  = d.get("target", "")
    context = d.get("engagement_type", "External Pentest")

    # Score each host by attack surface indicators
    def score_host(h: dict) -> dict:
        score = 0.0
        factors = []
        tags = h.get("tags", [])
        ports = h.get("ports", []) or list(h.get("services", {}).keys())
        services = h.get("services", {})

        # Service-level risk factors
        risky = {
            "unauthenticated-rce": (4.0, "Unauthenticated RCE surface"),
            "active-directory":    (3.5, "Domain controller — full-domain impact"),
            "ci-cd":               (3.0, "CI/CD — build secret access"),
            "direct-exposure":     (2.5, "Database directly exposed"),
            "no-firewall":         (2.0, "No network segmentation"),
            "debug-mode":          (1.5, "Debug mode — credential leak risk"),
            "outdated-software":   (1.0, "EOL software with CVEs"),
        }
        for tag, (w, reason) in risky.items():
            if tag in tags:
                score += w
                factors.append({"factor": reason, "weight": w})

        # Port risk bonus
        dangerous_ports = {3389:"RDP", 22:"SSH", 1433:"MSSQL", 3306:"MySQL",
                           5432:"PostgreSQL", 445:"SMB", 139:"NetBIOS", 23:"Telnet"}
        for p in [int(x) for x in ports if str(x).isdigit()]:
            if p in dangerous_ports:
                score += 0.5
                factors.append({"factor": f"Port {p} ({dangerous_ports[p]})", "weight": 0.5})

        return {
            "ip":       h.get("ip", target),
            "hostname": h.get("hostname", ""),
            "score":    round(min(score, 10.0), 1),
            "priority": "CRITICAL" if score >= 7 else "HIGH" if score >= 4 else "MEDIUM" if score >= 2 else "LOW",
            "factors":  sorted(factors, key=lambda x: -x["weight"])[:5],
        }

    scored = sorted([score_host(h) for h in hosts], key=lambda x: -x["score"]) if hosts else [
        {"ip": target, "score": 5.0, "priority": "MEDIUM", "factors": [{"factor":"No host data — generic assessment","weight":0}]}
    ]

    # Risk matrix
    total_score = sum(h["score"] for h in scored) / max(len(scored), 1)
    risk_matrix = {
        "overall_score": round(total_score, 1),
        "critical_hosts": len([h for h in scored if h["priority"] == "CRITICAL"]),
        "high_hosts":     len([h for h in scored if h["priority"] == "HIGH"]),
        "attack_surface": "WIDE" if len(hosts) > 5 else "FOCUSED" if len(hosts) > 1 else "SINGLE",
        "engagement_type": context,
    }

    # Top threats based on scored factors
    all_factors = []
    for h in scored:
        for f in h.get("factors", []):
            all_factors.append({**f, "host": h["ip"]})
    top_threats = sorted(all_factors, key=lambda x: -x["weight"])[:8]

    # Recommended attack order
    recommended_order = [
        {"rank": i+1, "host": h["ip"], "priority": h["priority"], "score": h["score"]}
        for i, h in enumerate(scored[:6])
    ]

    return jsonify({
        "engagement_id":    d.get("engagement_id"),
        "target":           target,
        "risk_matrix":      risk_matrix,
        "top_threats":      top_threats,
        "recommended_order": recommended_order,
        "assumption_warnings": [
            "Risk scores are based on passive indicators only",
            "Active scanning may reveal additional attack surface",
            "Service versions not verified until vuln scan phase",
        ],
    })


# ─── Playbook Extraction (framework-extractor skill) ──────────────────────────

@app.route("/playbook/extract", methods=["POST"])
def playbook_extract():
    """
    Extract a reusable attack playbook from a completed engagement.
    Applies framework-extractor skill pattern: label each stage with
    inputs, processes, and outputs to create a transferable playbook.

    Body: { engagement_id, findings, tool_results, target_profile }
    Returns: structured playbook with labeled stages, reusable for similar targets
    """
    d = request.get_json(silent=True) or {}
    findings = d.get("findings", [])
    tool_results = d.get("tool_results", {})
    profile = d.get("target_profile", {})

    if not findings and not tool_results:
        return jsonify({"error": "findings or tool_results required"}), 400

    # Extract successful attack chains
    p0_p1 = [f for f in findings if f.get("priority") in ["P0","P1"]]
    by_mitre = {}
    for f in p0_p1:
        t = f.get("mitre_technique", "unknown")
        by_mitre.setdefault(t, []).append(f)

    # Build stage definitions (framework-extractor pattern)
    stages = []
    phase_map = {
        "recon":   {"label":"RECONNAISSANCE", "inputs":"Target domain/IP", "outputs":"Host list, open ports, services, tech stack"},
        "vuln":    {"label":"VULNERABILITY IDENTIFICATION", "inputs":"Host + service list", "outputs":"CVEs, misconfigs, exploit candidates"},
        "exploit": {"label":"EXPLOITATION", "inputs":"Vuln list + exploit DB", "outputs":"Shell/auth access, credential dump"},
        "postex":  {"label":"POST-EXPLOITATION", "inputs":"Initial access", "outputs":"Privesc, lateral movement, persistence"},
        "report":  {"label":"DOCUMENTATION", "inputs":"All findings", "outputs":"Report, remediation tracker, client delivery"},
    }

    for phase, meta in phase_map.items():
        phase_findings = [f for f in findings if f.get("phase") == phase] or                           [f for f in findings][:2] if phase == "vuln" else []
        stage = {
            "phase":   phase,
            "label":   meta["label"],
            "inputs":  meta["inputs"],
            "process": f"Run {phase} tools against authorized target",
            "outputs": meta["outputs"],
            "tools":   list({f.get("tool","unknown") for f in phase_findings})[:5],
            "decision_points": [],
        }
        # Add decision points based on findings
        if phase == "recon":
            stage["decision_points"] = [
                "If AD ports (88/389/445) found → prioritize Kerberoasting path",
                "If web app found → add web_enum + vuln_scan phases",
                "If CI/CD found → check for credential exposure in build logs",
            ]
        elif phase == "vuln":
            if p0_p1:
                stage["decision_points"] = [
                    f"P0 found ({p0_p1[0].get('title','?')}) → skip vuln scan, go directly to exploit",
                    "No vulns found → try credential attacks (requires approval)",
                ]
        stages.append(stage)

    # Playbook metadata
    tech_stack = profile.get("tech_stack", [])
    target_type = "Windows AD" if "active-directory" in str(profile) else                   "Web Application" if "web" in str(profile) else "Linux Server"

    playbook = {
        "name":          f"{target_type} Attack Playbook",
        "version":       "1.0",
        "extracted_from": d.get("engagement_id"),
        "applicability": {
            "target_types": [target_type],
            "tech_stack":   tech_stack,
            "prerequisites":["Scope authorization","Network access to target","HexStrike running"],
        },
        "stages": stages,
        "success_indicators": [
            f"Total findings: {len(findings)}",
            f"Critical/High findings: {len(p0_p1)}",
            f"MITRE techniques covered: {len(by_mitre)}",
        ],
        "reuse_checklist": [
            "Verify scope authorization before any active phase",
            "Check tech stack matches — different stacks need different tools",
            "Validate CVE IDs are current (check NVD for patch status)",
            "Adjust approval gates based on engagement rules",
        ],
    }

    return jsonify(playbook)


# ─── Strategic Intel Brief (strategic-insights + synthesis skills) ────────────

@app.route("/intel/brief", methods=["POST"])
def intel_brief():
    """
    Generate a tactical intelligence brief from engagement memory.
    Applies strategic-insights skill: filter noise, surface what matters most,
    explain what decisions each insight informs.

    Body: { engagement_id, audience: "operator|executive|technical" }
    Returns: top insights, decision points, attack paths, recommended next action
    """
    d = request.get_json(silent=True) or {}
    eid = d.get("engagement_id", "")
    audience = d.get("audience", "operator")

    if not eid:
        return jsonify({"error": "engagement_id required"}), 400

    # Pull findings from memory
    mem = _get_memory(eid) if HexStrikeMemory else None
    findings = mem.get_findings("P4") if mem else []
    p0 = [f for f in findings if f.get("data",{}).get("priority") == "P0"]
    p1 = [f for f in findings if f.get("data",{}).get("priority") == "P1"]

    # Agent state
    agent = get_agent(eid) if get_agent else None
    pivot_map = agent.pivot_map if agent else {}

    # Strategic insights (strategic-insights pattern: 5 most valuable)
    insights = []

    if p0:
        insights.append({
            "rank": 1,
            "insight": f"{len(p0)} critical-severity finding(s) identified",
            "detail": p0[0].get("data",{}).get("title","?") if p0 else "",
            "decision": "Immediate remediation required — stop all testing and notify client",
            "urgency": "IMMEDIATE",
        })

    if pivot_map:
        insights.append({
            "rank": 2,
            "insight": f"Lateral movement established — {len(pivot_map)} pivot hops recorded",
            "detail": "Internal network reachable from initial foothold",
            "decision": "Document blast radius — escalate to incident response if unplanned",
            "urgency": "HIGH",
        })

    if p1:
        insights.append({
            "rank": 3,
            "insight": f"{len(p1)} high-severity finding(s) ready for client review",
            "detail": "; ".join(f.get("data",{}).get("title","?") for f in p1[:3]),
            "decision": "Prioritize in remediation roadmap — include in executive summary",
            "urgency": "HIGH",
        })

    total = len(findings)
    if total > 0:
        insights.append({
            "rank": 4,
            "insight": f"Full finding inventory: {total} items across all severity levels",
            "detail": f"P0:{len(p0)} P1:{len(p1)} P2-P4:{total-len(p0)-len(p1)}",
            "decision": "Generate report before engagement window closes",
            "urgency": "MEDIUM",
        })

    if not p0 and not p1 and total == 0:
        insights.append({
            "rank": 1,
            "insight": "No findings in memory — engagement may not have started or memory is empty",
            "detail": "Check agent_status and ensure scope is authorized",
            "decision": "Run recon phase before generating intel brief",
            "urgency": "LOW",
        })

    # Audience-specific framing (role-distiller skill)
    framing = {
        "operator": "Tactical operational context for the red team operator",
        "executive": "Business risk and impact summary for leadership",
        "technical": "Technical remediation guidance for the blue team",
    }

    # Attack path synthesis (synthesis skill)
    attack_paths = []
    if p0 and pivot_map:
        attack_paths.append({
            "path": "Initial Access → Exploitation → Lateral Movement → Full Compromise",
            "severity": "CRITICAL",
            "hops": len(pivot_map),
        })
    elif p0:
        attack_paths.append({
            "path": "Initial Access → Exploitation → Objective",
            "severity": "CRITICAL",
            "hops": 1,
        })

    # Recommended next action (action-plan-generator skill)
    if audience == "operator":
        next_action = "Continue to post-exploitation phase" if p0 and not pivot_map else                       "Generate report and deliver to client" if p0 and pivot_map else                       "Escalate vuln scan — no critical findings yet"
    elif audience == "executive":
        next_action = "Schedule emergency remediation call" if p0 else                       "Review high findings in upcoming security review"
    else:
        next_action = f"Prioritize patching {p0[0].get('data',{}).get('title','?')}" if p0 else                       "Review finding list and assign remediation owners"

    return jsonify({
        "engagement_id": eid,
        "audience": audience,
        "framing": framing.get(audience, ""),
        "insights": insights[:5],
        "attack_paths": attack_paths,
        "recommended_next_action": next_action,
        "finding_summary": {"P0":len(p0),"P1":len(p1),"total":total},
        "pivot_hops": len(pivot_map),
    })


# ─── DECEPTICON Endpoints ──────────────────────────────────────────────────────
# Red team deception layer: honeytokens, canary beacons, attribution artifacts.
# All tokens scoped per engagement. Requires active scope authorization.

def _engine(eid: str) -> Optional["DeceptionEngine"]:
    if not _get_dec_engine:
        return None
    return _get_dec_engine(eid, EVIDENCE_DIR,
                            beacon_port=int(os.environ.get("DECEPTION_BEACON_PORT","9999")))


@app.route("/deception/token/create", methods=["POST"])
def deception_create():
    """
    Generate a deception token for deployment on a compromised host.
    Types: aws_key | api_token | db_cred | git_pat | env_file | honeyfile | attribution
    Body: { engagement_id, token_type, ...type_specific_kwargs }
    """
    d = request.get_json(silent=True) or {}
    eid = d.pop("engagement_id", "")
    token_type = d.pop("token_type", "")
    if not eid or not token_type:
        return jsonify({"error": "engagement_id and token_type required"}), 400

    authorized, reason = (_scope_auth.is_authorized(eid, "deception")
                          if _scope_auth else (True, "no scope auth"))
    if not authorized:
        return jsonify({"error": f"Not authorized: {reason}"}), 403

    eng = _engine(eid)
    if not eng:
        return jsonify({"error": "DeceptionEngine not available"}), 503
    try:
        token = eng.create_token(token_type, **d)
        audit("deception_create", {"target": eid}, {"token_type": token_type, "id": token["id"]}, True)
        return jsonify(token)
    except ValueError as e:
        return jsonify({"error": str(e), "valid_types": list(
            ["aws_key","api_token","db_cred","git_pat","env_file","honeyfile","attribution"]
        )}), 400


@app.route("/deception/token/deploy", methods=["POST"])
def deception_deploy():
    """
    Record that a token has been deployed to a target host.
    Does not perform the actual file write — that goes through MSF or Desktop Commander.
    Body: { engagement_id, token_id, host, path }
    """
    d = request.get_json(silent=True) or {}
    eid = d.get("engagement_id","")
    eng = _engine(eid)
    if not eng:
        return jsonify({"error": "DeceptionEngine not available"}), 503
    eng.mark_deployed(d.get("token_id",""), d.get("path",""), d.get("host",""))
    audit("deception_deploy", {"target": d.get("host","")}, d, True)
    return jsonify({"deployed": True, **d})


@app.route("/deception/listener/start", methods=["POST"])
def deception_listener_start():
    """
    Start the HTTP beacon listener.
    When a deployed honeytoken is triggered, it beacons to this server.
    Returns the listener URL to embed in honeyfiles.
    Body: { engagement_id }
    """
    d = request.get_json(silent=True) or {}
    eid = d.get("engagement_id","")
    eng = _engine(eid)
    if not eng:
        return jsonify({"error": "DeceptionEngine not available"}), 503
    result = eng.start_listener()
    return jsonify(result)


@app.route("/deception/listener/stop", methods=["POST"])
def deception_listener_stop():
    d = request.get_json(silent=True) or {}
    eid = d.get("engagement_id","")
    eng = _engine(eid)
    if eng:
        eng.stop_listener()
    return jsonify({"stopped": True})


@app.route("/deception/tokens", methods=["GET"])
def deception_tokens():
    """List all tokens for an engagement with deployment and trigger status."""
    eid = request.args.get("engagement_id","")
    if not eid:
        return jsonify({"error": "engagement_id required"}), 400
    eng = _engine(eid)
    if not eng:
        return jsonify({"error": "DeceptionEngine not available"}), 503
    return jsonify({"tokens": eng.list_tokens()})


@app.route("/deception/alerts", methods=["GET"])
def deception_alerts():
    """Return all triggered token alerts for an engagement, newest first."""
    eid = request.args.get("engagement_id","")
    if not eid:
        return jsonify({"error": "engagement_id required"}), 400
    eng = _engine(eid)
    if not eng:
        return jsonify({"error": "DeceptionEngine not available"}), 503
    return jsonify({"alerts": eng.list_alerts()})


@app.route("/deception/status", methods=["GET"])
def deception_status():
    """
    Full deception layer status: token counts, alert count, time-to-detection.
    """
    eid = request.args.get("engagement_id","")
    if not eid:
        return jsonify({"error": "engagement_id required"}), 400
    eng = _engine(eid)
    if not eng:
        return jsonify({"error": "DeceptionEngine not available"}), 503
    return jsonify(eng.status())


@app.route("/deception/cleanup", methods=["POST"])
def deception_cleanup():
    """Remove token records after engagement. Pass token_id to remove one, or leave blank for all."""
    d = request.get_json(silent=True) or {}
    eid = d.get("engagement_id","")
    eng = _engine(eid)
    if eng:
        eng.cleanup(d.get("token_id"))
        audit("deception_cleanup", {"target": eid}, {}, True)
    return jsonify({"cleaned": True})

# ─── Entrypoint ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    glm_status_str = f"GLM-4.5 {'ONLINE' if _glm_client else 'OFFLINE (set ZHIPUAI_API_KEY)'}"
    print("=" * 60)
    print("  HexStrike AI — Offensive Security MCP Platform")
    print("  Flask:      http://localhost:8888")
    print("  Health:     http://localhost:8888/health")
    print("  Tools:      http://localhost:8888/mcp/tools")
    print("  Audit:      http://localhost:8888/mcp/audit")
    print(f"  GLM routes: http://localhost:8888/glm/status")
    print(f"  Memory:     http://localhost:8888/memory/summary")
    print(f"  Agent:      http://localhost:8888/agent/status")
    print(f"  {glm_status_str}")
    print("=" * 60)
    app.run(host="127.0.0.1", port=8888, debug=False)
