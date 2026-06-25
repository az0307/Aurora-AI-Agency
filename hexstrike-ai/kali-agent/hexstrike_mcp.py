"""
HexStrike MCP Tool Definitions — FastMCP server for Kali Agent
Replace/expand existing mcp_bridge.py with this.
AutoBoros.ai | 2026-03-27

Install: pip install fastmcp --break-system-packages
Run:     python hexstrike_mcp.py (serves on stdio for MCP clients)
"""

import json
import re
import subprocess
import shlex
import os
from datetime import datetime, timezone
from typing import Optional

from fastmcp import FastMCP

from scope_guard import ScopeGuard, load_scope_from_file
from audit_logger import AuditLogger
from sanitizer import sanitize_tool_output

# --- Initialize ---
mcp = FastMCP("HexStrike AI — Kali Agent MCP Server")

# Global state (loaded per-engagement)
_scope_guard: Optional[ScopeGuard] = None
_audit_logger: Optional[AuditLogger] = None

PENTEST_BASE = "/tmp/pentest"

# ============================================================
# COMMAND EXECUTION — SAFE (NO shell=True)
# ============================================================

# Allowlisted binaries — only these can be executed
ALLOWED_COMMANDS = {
    "nmap", "masscan", "subfinder", "amass", "theHarvester",
    "whatweb", "nuclei", "nikto", "wpscan", "gobuster", "ffuf",
    "sqlmap", "searchsploit", "hydra", "john", "hashcat",
    "whois", "dig", "nslookup", "host", "traceroute", "ping",
    "curl", "wget", "tshark", "tcpdump",
    "enum4linux", "enum4linux-ng", "smbclient", "rpcclient",
    "crackmapexec", "netexec",
    "msfconsole", "msfvenom",
    "wfuzz", "dirb", "feroxbuster",
    "dnsrecon", "dnstwist",
    "hcxdumptool", "hcxpcapngtool",
    "aircrack-ng", "airodump-ng", "aireplay-ng", "airmon-ng",
    "reaver", "bully", "wifite",
    "kerbrute", "bloodhound-python",
    "certutil", "certipy",
    "socat", "nc", "netcat", "ncat",
    "python3", "python",
    "sort", "cat", "head", "tail", "grep", "awk", "sed", "wc",
    "find", "ls", "mkdir", "cp",
}

# Commands that require explicit operator approval before execution
APPROVAL_REQUIRED = {
    "msfconsole", "msfvenom", "hydra", "hashcat", "john",
    "crackmapexec", "netexec",
    "aircrack-ng", "airodump-ng", "aireplay-ng",
    "reaver", "bully", "wifite",
    "responder", "ntlmrelayx",
}

# Blocked argument patterns (prevent destructive operations)
BLOCKED_ARG_PATTERNS = [
    r'rm\s+-rf',
    r'>\s*/dev/',
    r'mkfs\.',
    r'dd\s+if=',
    r':\(\)\{.*\}',  # fork bomb
    r'wget.*\|\s*(ba)?sh',  # pipe to shell
    r'curl.*\|\s*(ba)?sh',
]


class CommandValidationError(Exception):
    """Raised when a command fails security validation."""
    pass


def _validate_command(cmd_parts: list[str]) -> None:
    """
    Validate a command against the allowlist and blocked patterns.
    Raises CommandValidationError if validation fails.
    """
    if not cmd_parts:
        raise CommandValidationError("Empty command")

    binary = os.path.basename(cmd_parts[0])

    # Check allowlist
    if binary not in ALLOWED_COMMANDS:
        raise CommandValidationError(
            f"🚫 BLOCKED: '{binary}' is not in the allowed commands list. "
            f"Allowed: {', '.join(sorted(ALLOWED_COMMANDS)[:20])}..."
        )

    # Check for blocked argument patterns
    full_cmd_str = " ".join(cmd_parts)
    for pattern in BLOCKED_ARG_PATTERNS:
        if re.search(pattern, full_cmd_str):
            raise CommandValidationError(
                f"🚫 BLOCKED: Dangerous argument pattern detected in command"
            )

    # Check for shell metacharacters in arguments (should not be present with shell=False)
    for arg in cmd_parts[1:]:
        if any(c in arg for c in ['|', '`', '$(']):
            raise CommandValidationError(
                f"🚫 BLOCKED: Shell metacharacter in argument: {arg[:50]}"
            )


def _run_cmd(cmd_parts: list[str], timeout: int = 300, env: Optional[dict] = None) -> str:
    """
    Execute a command safely using shell=False with argument list.

    Args:
        cmd_parts: List of command and arguments, e.g. ["nmap", "-sV", "10.0.0.1"]
        timeout: Maximum execution time in seconds
        env: Optional environment variables to merge with os.environ

    Returns:
        Command output string (stdout + stderr on failure)

    Security:
        - shell=False prevents shell injection
        - Command must be in ALLOWED_COMMANDS allowlist
        - Dangerous argument patterns are blocked
        - Shell metacharacters in arguments are rejected
    """
    try:
        _validate_command(cmd_parts)
    except CommandValidationError as e:
        return f"[SECURITY] {str(e)}"

    run_env = None
    if env:
        run_env = {**os.environ, **env}

    try:
        result = subprocess.run(
            cmd_parts,
            shell=False,  # CRITICAL: never shell=True
            capture_output=True,
            text=True,
            timeout=timeout,
            env=run_env,
            cwd=PENTEST_BASE,
        )
        output = result.stdout
        if result.returncode != 0 and result.stderr:
            output += f"\n[STDERR]: {result.stderr}"
        return output
    except FileNotFoundError:
        return f"[ERROR] Command not found: {cmd_parts[0]}"
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] Command exceeded {timeout}s limit: {cmd_parts[0]}"
    except Exception as e:
        return f"[ERROR] {type(e).__name__}: {str(e)}"


def _run_cmd_str(cmd_str: str, timeout: int = 300) -> str:
    """
    Parse a command string into parts and execute safely.
    Uses shlex.split() for proper tokenization, then validates via _run_cmd.
    This is the migration path — new code should use _run_cmd() directly.
    """
    try:
        parts = shlex.split(cmd_str)
    except ValueError as e:
        return f"[ERROR] Failed to parse command: {e}"
    return _run_cmd(parts, timeout=timeout)


def _ensure_dir(target: str) -> str:
    """Create pentest working directory for target."""
    # Sanitize target to safe directory name
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', target)
    if not safe_name or safe_name.startswith('.'):
        safe_name = "target_" + safe_name
    path = os.path.join(PENTEST_BASE, safe_name)
    os.makedirs(path, exist_ok=True)
    return path


def _check_scope(target: str, tool: str) -> Optional[str]:
    """Check scope before tool execution. Returns error message or None if OK."""
    if _scope_guard is None:
        return "⚠️ No scope defined. Run init_engagement() first."
    result = _scope_guard.validate(target)
    if not result["allowed"]:
        if _audit_logger:
            _audit_logger.log_scope_check(target, False, result["reason"], tool)
        return f"🚫 SCOPE VIOLATION: {result['reason']}"
    if _audit_logger:
        _audit_logger.log_scope_check(target, True, result["reason"], tool)
    return None


# ============================================================
# ENGAGEMENT MANAGEMENT
# ============================================================

@mcp.tool()
def init_engagement(scope_config: str) -> dict:
    """
    Initialize a new penetration testing engagement with scope definition.
    scope_config: JSON string with engagement + scope definition.
    Must be called before any scanning or exploitation tools.
    """
    global _scope_guard, _audit_logger
    try:
        config = json.loads(scope_config)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {e}"}

    _scope_guard = ScopeGuard(config)
    eid = config.get("engagement", {}).get("id", f"ENG-{datetime.now().strftime('%Y%m%d')}")
    _audit_logger = AuditLogger(eid)

    _audit_logger.log_tool_execution(
        skill="scope-guard", tool="init_engagement", action="engagement_init",
        target="N/A", command="init_engagement()", result_summary="Engagement initialized",
        phase="setup", approval="operator_confirmed",
    )

    return {
        "status": "success",
        "engagement_id": eid,
        "scope_summary": _scope_guard.get_scope_summary(),
        "ctf_mode": _scope_guard.is_ctf_mode(),
    }


@mcp.tool()
def check_scope(target: str) -> dict:
    """
    Validate whether a target (IP, domain, or URL) is within authorized scope.
    Call this before running any active security tools.
    """
    if _scope_guard is None:
        return {"allowed": False, "reason": "No engagement initialized"}
    return _scope_guard.validate(target)


# ============================================================
# RECONNAISSANCE TOOLS
# ============================================================

@mcp.tool()
def recon_target(target: str, mode: str = "passive") -> dict:
    """
    Run reconnaissance on a target domain or IP.
    mode: 'passive' (DNS/WHOIS/subfinder only) or 'active' (adds nmap + whatweb)
    """
    scope_err = _check_scope(target, "recon_target")
    if scope_err:
        return {"status": "blocked", "reason": scope_err}

    work_dir = _ensure_dir(target)
    results = {}

    # Passive recon (always)
    results["whois"] = sanitize_tool_output(
        _run_cmd(["whois", target]), "whois"
    ).output
    results["dns_a"] = _run_cmd(["dig", target, "A", "+short"])
    results["dns_mx"] = _run_cmd(["dig", target, "MX", "+short"])
    results["dns_ns"] = _run_cmd(["dig", target, "NS", "+short"])
    results["dns_txt"] = _run_cmd(["dig", target, "TXT", "+short"])
    results["subdomains_passive"] = _run_cmd(
        ["subfinder", "-d", target, "-silent"], timeout=120
    )

    if mode == "active":
        scope_err_active = _check_scope(target, "nmap")
        if scope_err_active:
            results["active_scan"] = scope_err_active
        else:
            results["ports"] = sanitize_tool_output(
                _run_cmd(
                    ["nmap", "-sV", "--top-ports", "1000", "-T4", target],
                    timeout=600,
                ),
                "nmap",
            ).output
            whatweb_out = os.path.join(work_dir, "whatweb.json")
            results["whatweb"] = sanitize_tool_output(
                _run_cmd(
                    ["whatweb", target, f"--log-json={whatweb_out}"],
                    timeout=120,
                ),
                "whatweb",
            ).output

    if _audit_logger:
        _audit_logger.log_tool_execution(
            skill="recon-osint", tool="recon_target", action=f"recon_{mode}",
            target=target, command=f"recon_target({target}, {mode})",
            result_summary=f"Recon complete — {len(results)} data points collected",
            phase="recon",
        )

    return {"status": "success", "target": target, "mode": mode, "results": results}


@mcp.tool()
def port_scan(target: str, flags: str = "-sV -T4 --top-ports 1000") -> dict:
    """
    Run nmap port scan against target.
    target: IP or hostname
    flags: nmap flag string (default: service version detection, top 1000 ports)
    """
    scope_err = _check_scope(target, "nmap")
    if scope_err:
        return {"status": "blocked", "reason": scope_err}

    work_dir = _ensure_dir(target)
    output_file = os.path.join(work_dir, "nmap_scan.txt")

    # Parse flags safely — split the flags string into individual args
    try:
        flag_parts = shlex.split(flags)
    except ValueError:
        return {"status": "error", "message": "Invalid nmap flags"}

    cmd_parts = ["nmap"] + flag_parts + ["-oN", output_file, target]
    raw = _run_cmd(cmd_parts, timeout=900)
    sanitized = sanitize_tool_output(raw, "nmap")

    if _audit_logger:
        _audit_logger.log_tool_execution(
            skill="recon-osint", tool="nmap", action="port_scan",
            target=target, command=" ".join(cmd_parts), result_summary=raw[:200],
            output_file=output_file, phase="recon",
        )

    return {"status": "success", "output": sanitized.output, "output_file": output_file}


# ============================================================
# VULNERABILITY SCANNING
# ============================================================

@mcp.tool()
def vuln_scan(target: str, templates: str = "cves,exposures,misconfiguration") -> dict:
    """
    Run Nuclei vulnerability scan against target URL or list.
    templates: comma-separated template categories (cves, exposures, misconfiguration, default-logins, xss)
    """
    scope_err = _check_scope(target, "nuclei")
    if scope_err:
        return {"status": "blocked", "reason": scope_err}

    work_dir = _ensure_dir(target)
    output_file = os.path.join(work_dir, "nuclei_results.json")

    # Build nuclei command safely
    cmd_parts = ["nuclei", "-u", target, "-severity", "critical,high,medium",
                 "-json", "-o", output_file]
    for t in templates.split(","):
        t = t.strip()
        if t and re.match(r'^[a-zA-Z0-9_-]+$', t):  # Validate template name
            cmd_parts.extend(["-t", f"{t}/"])

    raw = _run_cmd(cmd_parts, timeout=900)
    sanitized = sanitize_tool_output(raw, "nuclei")

    if _audit_logger:
        _audit_logger.log_tool_execution(
            skill="vuln-analysis", tool="nuclei", action="vuln_scan",
            target=target, command=" ".join(cmd_parts), result_summary=raw[:200],
            output_file=output_file, phase="vuln_scan",
        )

    return {"status": "success", "output": sanitized.output, "output_file": output_file}


@mcp.tool()
def web_enum(target: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt") -> dict:
    """
    Directory and file enumeration with gobuster/ffuf.
    target: base URL (e.g. https://example.com)
    wordlist: path to wordlist file
    """
    scope_err = _check_scope(target, "ffuf")
    if scope_err:
        return {"status": "blocked", "reason": scope_err}

    work_dir = _ensure_dir(target)
    output_file = os.path.join(work_dir, "ffuf_dirs.json")

    # Validate wordlist path exists and is under expected directories
    if not os.path.isfile(wordlist):
        return {"status": "error", "message": f"Wordlist not found: {wordlist}"}
    allowed_wordlist_dirs = ["/usr/share/wordlists", "/usr/share/seclists", "/tmp/pentest"]
    if not any(os.path.abspath(wordlist).startswith(d) for d in allowed_wordlist_dirs):
        return {"status": "error", "message": f"Wordlist must be in /usr/share/wordlists or /tmp/pentest"}

    fuzz_url = f"{target.rstrip('/')}/FUZZ"
    cmd_parts = ["ffuf", "-u", fuzz_url, "-w", wordlist,
                 "-mc", "200,301,302,403", "-o", output_file, "-of", "json"]
    raw = _run_cmd(cmd_parts, timeout=600)
    sanitized = sanitize_tool_output(raw, "ffuf")

    if _audit_logger:
        _audit_logger.log_tool_execution(
            skill="web-app-security", tool="ffuf", action="web_enum",
            target=target, command=" ".join(cmd_parts), result_summary=raw[:200],
            output_file=output_file, phase="vuln_scan",
        )

    return {"status": "success", "output": sanitized.output, "output_file": output_file}


# ============================================================
# EXPLOIT RESEARCH
# ============================================================

@mcp.tool()
def exploit_search(query: str) -> dict:
    """
    Search ExploitDB for exploits matching a product/version query.
    query: search terms (e.g. 'WordPress 6.4', 'Apache 2.4.52 RCE')
    """
    cmd_parts = ["searchsploit", query, "--json"]
    raw = _run_cmd(cmd_parts, timeout=30)
    sanitized = sanitize_tool_output(raw, "searchsploit")

    if _audit_logger:
        _audit_logger.log_tool_execution(
            skill="exploit-dev", tool="searchsploit", action="exploit_search",
            target=query, command=" ".join(cmd_parts), result_summary=raw[:200],
            phase="exploitation",
        )

    return {"status": "success", "query": query, "output": sanitized.output}


# ============================================================
# REPORTING
# ============================================================

@mcp.tool()
def generate_report(target: str, format: str = "markdown") -> dict:
    """
    Generate a penetration testing report from all collected findings.
    Aggregates data from the engagement working directory.
    format: 'markdown' or 'json'
    """
    if _audit_logger is None:
        return {"status": "error", "message": "No engagement initialized"}

    report_data = _audit_logger.export_for_report()
    work_dir = _ensure_dir(target)

    if format == "json":
        report_path = f"{work_dir}/reports/engagement_report.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2, default=str)
    else:
        report_path = f"{work_dir}/reports/engagement_report.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            f.write(f"# Penetration Test Report — {target}\n\n")
            f.write(f"**Engagement ID:** {report_data['engagement_id']}\n\n")
            f.write(f"## Engagement Statistics\n\n")
            stats = report_data["stats"]
            f.write(f"- Total actions: {stats['total_actions']}\n")
            f.write(f"- Scope checks: {stats['scope_checks']}\n")
            f.write(f"- Scope violations blocked: {stats['scope_violations']}\n")
            f.write(f"- Findings: {stats['findings']}\n")
            f.write(f"- Exploitation attempts: {stats['exploitation_attempts']}\n")
            f.write(f"- Tools used: {', '.join(stats.get('tools_used', []))}\n\n")
            f.write(f"## Timeline\n\n```\n{report_data['timeline']}\n```\n")

    return {"status": "success", "report_path": report_path, "stats": report_data["stats"]}


@mcp.tool()
def get_engagement_status() -> dict:
    """Get current engagement status, stats, and scope summary."""
    if _scope_guard is None or _audit_logger is None:
        return {"status": "no_engagement", "message": "No engagement initialized. Call init_engagement() first."}

    return {
        "status": "active",
        "scope_summary": _scope_guard.get_scope_summary(),
        "ctf_mode": _scope_guard.is_ctf_mode(),
        "stats": _audit_logger.get_stats(),
    }


# ============================================================
# FINDINGS EXPORT
# ============================================================

@mcp.tool()
def export_findings(target: str, format: str = "all") -> dict:
    """
    Export engagement findings to external formats.
    format: 'csv', 'jira', 'linear', 'markdown', 'sarif', or 'all'
    Findings are collected from the engagement audit log.
    """
    if _audit_logger is None:
        return {"status": "error", "message": "No engagement initialized"}

    # Load findings from log
    findings = []
    if os.path.exists(_audit_logger.findings_log):
        with open(_audit_logger.findings_log, "r") as f:
            for line in f:
                try:
                    findings.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

    if not findings:
        return {"status": "error", "message": "No findings to export"}

    work_dir = _ensure_dir(target)
    export_dir = os.path.join(work_dir, "exports")
    os.makedirs(export_dir, exist_ok=True)

    try:
        from findings_exporter import export_csv, export_jira_bulk, export_linear, export_markdown_table, export_sarif, export_all

        if format == "all":
            paths = export_all(findings, export_dir, _audit_logger.engagement_id)
        elif format == "csv":
            path = os.path.join(export_dir, "findings.csv")
            export_csv(findings, path)
            paths = {"csv": path}
        elif format == "jira":
            path = os.path.join(export_dir, "findings_jira.json")
            export_jira_bulk(findings, output_path=path)
            paths = {"jira": path}
        elif format == "linear":
            path = os.path.join(export_dir, "findings_linear.json")
            export_linear(findings, output_path=path)
            paths = {"linear": path}
        elif format == "markdown":
            path = os.path.join(export_dir, "findings.md")
            export_markdown_table(findings, path)
            paths = {"markdown": path}
        elif format == "sarif":
            path = os.path.join(export_dir, "findings.sarif")
            export_sarif(findings, output_path=path)
            paths = {"sarif": path}
        else:
            return {"status": "error", "message": f"Unknown format: {format}"}

        return {"status": "success", "findings_count": len(findings), "exported_files": paths}
    except ImportError:
        return {"status": "error", "message": "findings_exporter module not found"}


@mcp.tool()
def deduplicate_findings(target: str) -> dict:
    """
    Deduplicate findings from multiple scanning tools.
    Merges overlapping results from nuclei, nikto, sqlmap, Burp, etc.
    """
    if _audit_logger is None:
        return {"status": "error", "message": "No engagement initialized"}

    # Load findings from log
    findings = []
    if os.path.exists(_audit_logger.findings_log):
        with open(_audit_logger.findings_log, "r") as f:
            for line in f:
                try:
                    findings.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

    if len(findings) < 2:
        return {"status": "ok", "message": "Not enough findings to deduplicate", "count": len(findings)}

    try:
        from deduplicator import deduplicate_findings as dedup, dedup_stats

        deduped = dedup(findings)
        stats = dedup_stats(findings, deduped)

        # Write deduplicated findings back
        work_dir = _ensure_dir(target)
        dedup_path = os.path.join(work_dir, "findings_deduped.json")
        with open(dedup_path, "w") as f:
            json.dump(deduped, f, indent=2, default=str)

        return {
            "status": "success",
            "original": stats["original_count"],
            "deduplicated": stats["deduplicated_count"],
            "removed": stats["removed"],
            "reduction_pct": stats["reduction_pct"],
            "output_file": dedup_path,
        }
    except ImportError:
        return {"status": "error", "message": "deduplicator module not found"}


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    mcp.run()
