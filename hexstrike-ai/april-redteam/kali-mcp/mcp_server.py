#!/usr/bin/env python3
"""
Kali MCP Server — SSH+PTY+tmux bridge
Exposes Kali Linux as MCP tools for AI agents (Claude, etc.)
Part of the April 2026 Red Team Stack
"""

import asyncio
import logging
import os
import sys
import subprocess
from typing import Any, Optional

import paramiko
from mcp.server.fastmcp import FastMCP

# ── Config ────────────────────────────────────────────────────
TARGET_HOST = os.getenv("TARGET_HOST", "localhost")
TARGET_PORT = int(os.getenv("TARGET_PORT", "22"))
TARGET_USER = os.getenv("TARGET_USER", "kali")
TARGET_SSH_KEY = os.path.expanduser(os.getenv("TARGET_SSH_KEY", "~/.ssh/kali_mcp_ed25519"))
TARGET_PASSWORD = os.getenv("TARGET_PASSWORD", "")
MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "10"))
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "300"))

logging.basicConfig(level=logging.INFO, stream=sys.stderr,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("kali-mcp")

# ── FastMCP server ────────────────────────────────────────────
mcp = FastMCP("kali-mcp", description="Kali Linux SSH+PTY MCP Server — live terminal access")

# ── SSH session store ─────────────────────────────────────────
_sessions: dict[str, Any] = {}
_ssh_client: Optional[paramiko.SSHClient] = None


def get_ssh():
    global _ssh_client
    if _ssh_client is None or not _ssh_client.get_transport() or \
       not _ssh_client.get_transport().is_active():
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connect_kwargs = {
            "hostname": TARGET_HOST,
            "port": TARGET_PORT,
            "username": TARGET_USER,
            "timeout": 10,
        }
        if TARGET_SSH_KEY and os.path.exists(TARGET_SSH_KEY):
            connect_kwargs["key_filename"] = TARGET_SSH_KEY
        elif TARGET_PASSWORD:
            connect_kwargs["password"] = TARGET_PASSWORD
        client.connect(**connect_kwargs)
        _ssh_client = client
        log.info(f"SSH connected to {TARGET_USER}@{TARGET_HOST}:{TARGET_PORT}")
    return _ssh_client


def run_ssh_command(command: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Execute a command over SSH and return stdout+stderr."""
    ssh = get_ssh()
    _, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    exit_code = stdout.channel.recv_exit_status()
    result = out
    if err:
        result += f"\n[STDERR]\n{err}"
    if exit_code != 0:
        result += f"\n[EXIT CODE: {exit_code}]"
    return result.strip()


# ── TOOLS ─────────────────────────────────────────────────────

@mcp.tool()
def kali_exec(command: str, timeout: int = 60) -> str:
    """
    Execute any command on the Kali Linux system.
    Returns stdout + stderr. For interactive tools use kali_tmux_*.
    IMPORTANT: Only use on authorized targets.
    """
    log.info(f"Executing: {command[:80]}...")
    return run_ssh_command(command, timeout=timeout)


@mcp.tool()
def kali_nmap(target: str, flags: str = "-sV -sC --open", ports: str = "") -> str:
    """
    Run nmap scan against target. Requires NET_RAW capability.
    target: IP, hostname, or CIDR range (authorized targets only)
    flags: nmap flags (default: service+script scan, open ports only)
    ports: port specification e.g. '80,443,8080' or '1-65535' (empty = top 1000)
    """
    port_arg = f"-p {ports}" if ports else ""
    cmd = f"nmap {flags} {port_arg} {target} 2>&1"
    return run_ssh_command(cmd, timeout=300)


@mcp.tool()
def kali_msf_run(resource_script: str) -> str:
    """
    Run a Metasploit resource script. Write the script first with kali_write_file.
    resource_script: full path to .rc file on Kali system
    """
    cmd = f"msfconsole -q -r {resource_script} 2>&1"
    return run_ssh_command(cmd, timeout=300)


@mcp.tool()
def kali_msf_search(query: str) -> str:
    """Search Metasploit modules. Returns module list with descriptions."""
    cmd = f'msfconsole -q -x "search {query}; exit" 2>&1'
    return run_ssh_command(cmd, timeout=60)


@mcp.tool()
def kali_sqlmap(url: str, flags: str = "--batch --level=2 --risk=1") -> str:
    """
    Run sqlmap against a URL. For authorized targets only.
    url: target URL with parameter e.g. 'http://target/page?id=1'
    flags: sqlmap flags (default: batch mode, level 2, risk 1)
    """
    cmd = f"sqlmap -u '{url}' {flags} 2>&1"
    return run_ssh_command(cmd, timeout=300)


@mcp.tool()
def kali_gobuster(target: str, wordlist: str = "/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt", flags: str = "-q") -> str:
    """
    Run gobuster directory/file brute-force.
    target: base URL e.g. 'http://target'
    wordlist: path to wordlist on Kali
    """
    cmd = f"gobuster dir -u {target} -w {wordlist} {flags} 2>&1"
    return run_ssh_command(cmd, timeout=300)


@mcp.tool()
def kali_hydra(target: str, service: str, username: str = "",
               userlist: str = "", password: str = "",
               passlist: str = "") -> str:
    """
    Run hydra brute-force attack. For authorized targets only.
    service: ssh, ftp, http-post-form, smb, etc.
    """
    user_part = f"-l {username}" if username else f"-L {userlist}"
    pass_part = f"-p {password}" if password else f"-P {passlist}"
    cmd = f"hydra {user_part} {pass_part} {target} {service} -t 4 2>&1"
    return run_ssh_command(cmd, timeout=300)


@mcp.tool()
def kali_tmux_new(session_name: str) -> str:
    """Create a new tmux session on Kali. Use for interactive tools like msfconsole."""
    cmd = f"tmux new-session -d -s {session_name} 2>&1 || echo 'Session may already exist'"
    return run_ssh_command(cmd)


@mcp.tool()
def kali_tmux_send(session_name: str, command: str) -> str:
    """Send a command to an existing tmux session."""
    cmd = f"tmux send-keys -t {session_name} '{command}' Enter 2>&1"
    return run_ssh_command(cmd)


@mcp.tool()
def kali_tmux_read(session_name: str, lines: int = 50) -> str:
    """Read the last N lines of output from a tmux session."""
    cmd = f"tmux capture-pane -t {session_name} -p 2>&1 | tail -{lines}"
    return run_ssh_command(cmd)


@mcp.tool()
def kali_write_file(path: str, content: str) -> str:
    """Write a file to the Kali system. Useful for MSF resource scripts, payloads, etc."""
    # Escape single quotes in content
    escaped = content.replace("'", "'\"'\"'")
    cmd = f"cat > '{path}' << 'KALI_MCP_EOF'\n{content}\nKALI_MCP_EOF"
    return run_ssh_command(cmd)


@mcp.tool()
def kali_read_file(path: str, lines: int = 100) -> str:
    """Read a file from the Kali system."""
    cmd = f"cat '{path}' 2>&1 | head -{lines}"
    return run_ssh_command(cmd)


@mcp.tool()
def kali_which_tools() -> str:
    """List available pentesting tools on the Kali system."""
    tools = [
        "nmap", "masscan", "msfconsole", "sqlmap", "gobuster", "dirb",
        "nikto", "hydra", "hashcat", "john", "netcat", "curl", "wget",
        "wfuzz", "ffuf", "nuclei", "subfinder", "amass", "httpx",
        "feroxbuster", "crackmapexec", "netexec", "impacket-*",
        "responder", "bloodhound-python", "evil-winrm",
        "hexstrike_server", "hexstrike_mcp"
    ]
    cmd = f"which {' '.join(tools)} 2>/dev/null | sort"
    return run_ssh_command(cmd)


@mcp.tool()
def kali_health() -> str:
    """Check Kali MCP server health — SSH connectivity, disk, memory."""
    cmd = "echo 'SSH: OK' && df -h / && free -h && uptime"
    return run_ssh_command(cmd)


# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info(f"Kali MCP Server starting — target: {TARGET_USER}@{TARGET_HOST}:{TARGET_PORT}")
    mcp.run()
