# 💀 KALI AGENT — AI-Driven Penetration Testing Platform

**AutoBoros.ai | Aurora AI Agency | 2026**

An AI-orchestrated penetration testing system that chains 15 specialized skills across the full pentest kill chain, with scope enforcement, audit logging, prompt injection protection, and professional report generation.

## Architecture

```
User Request → Curator (AI Orchestrator)
                    ↓
              Playbook Generation
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
scope-guard    recon-osint     vuln-analysis
    ↓               ↓               ↓
audit-logger   threat-intel    web-app-security
    ↓               ↓               ↓
    └───────── exploit-dev ─────────┘
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
payload-craft  post-exploit   active-directory
                    ↓
            credential-attack
                    ↓
            red-team-report → .docx / .pdf / .md

Cross-cutting: tool-output-sanitizer (every tool output)
               audit-logger (every action)
               scope-guard (every active tool)
```

## Quick Start

```bash
# 1. Clone and install
chmod +x install_kali_agent.sh
./install_kali_agent.sh

# 2. Start the MCP server
cd ~/hexstrike-ai
python3 hexstrike_mcp.py

# 3. Run tests
python3 test_modules.py        # 39 unit tests
python3 integration_test.py    # 74 integration tests
```

## Components

### Skills (15 installed)

| Skill | Phase | Expert Tools |
|-------|-------|-------------|
| `scope-guard` | Pre-engagement | IP/domain/CIDR validation, time windows |
| `audit-logger` | Cross-cutting | JSONL compliance trail, timeline generation |
| `tool-output-sanitizer` | Cross-cutting | Prompt injection defense (7 tag + 10 phrase patterns) |
| `recon-osint` | Reconnaissance | subfinder, amass, theHarvester, whatweb, nmap, Shodan |
| `threat-intel` | Intelligence | Shodan CVEDB, ExploitDB, EPSS, CISA KEV, MITRE ATT&CK |
| `vuln-analysis` | Vulnerability | nuclei, nikto, wpscan, sqlmap, CVE correlation |
| `web-app-security` | Vulnerability | OWASP Top 10, sqlmap, XSStrike, commix, ffuf |
| `exploit-dev` | Exploitation | searchsploit, Metasploit, PoC research |
| `payload-craft` | Exploitation | msfvenom, reverse shells, encoders |
| `post-exploit` | Post-exploit | LinPEAS, WinPEAS, mimikatz, secretsdump |
| `credential-attack` | Post-exploit | hashcat, john, hydra, crackmapexec |
| `active-directory` | Post-exploit | BloodHound, impacket, certipy, Kerberos attacks |
| `network-forensics` | Post-exploit | tcpdump, tshark, packet analysis |
| `wireless-recon` | Wireless | aircrack-ng, reaver, hcxdumptool (operator-only) |
| `red-team-report` | Reporting | .docx/.pdf/.md generation, attack path narratives |

### Python Modules

| Module | Purpose |
|--------|---------|
| `scope_guard.py` | Runtime scope enforcement with JSONL audit |
| `audit_logger.py` | Append-only compliance logging, stats, timeline |
| `sanitizer.py` | Prompt injection defense for tool output |
| `hexstrike_mcp.py` | FastMCP server (8 tools, shell-safe, scope-enforced) |
| `model_router.py` | GLM-4.5 ↔ Sonnet task routing with /interpret endpoint |

### JavaScript Modules

| Module | Purpose |
|--------|---------|
| `executePlaybook.js` | Wires Agent Workspace to HexStrike MCP |
| `KaliTargetPanel.jsx` | React engagement config UI |
| `generate_report.js` | Professional .docx report generator (docx-js) |

### React Artifacts

| Artifact | Purpose |
|----------|---------|
| `kali-engagement-dashboard.jsx` | Live engagement dashboard with persistent storage |
| `bloodhound-attack-path.jsx` | AD attack path SVG visualizer |

## Security Features

- **No `shell=True`** — all commands use `subprocess.run(shell=False)` with argument lists
- **Command allowlist** — 50+ approved binaries, everything else blocked
- **Blocked argument patterns** — fork bombs, pipe-to-shell, destructive ops
- **Scope enforcement** — every active tool validates target before execution
- **Prompt injection defense** — 17 patterns strip malicious content from tool output
- **Audit trail** — every action logged to append-only JSONL
- **Operator approval gates** — exploitation and lateral movement require human confirmation

## Tests

```bash
python3 test_modules.py        # 39 unit tests — scope, audit, sanitizer
python3 integration_test.py    # 74 integration tests — full playbook simulation
```

## MCP Configuration

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "hexstrike": {
      "command": "python3",
      "args": ["/home/kali/hexstrike-ai/hexstrike_mcp.py"],
      "env": { "PENTEST_BASE": "/tmp/pentest" }
    },
    "shodan": {
      "command": "mcp-shodan",
      "env": { "SHODAN_API_KEY": "your_key" }
    }
  }
}
```

## Legal

All tools are for **authorized security testing only**. Running security tools against unauthorized targets is a criminal offense. The scope-guard skill exists specifically to prevent this — do not bypass it.

## License

AutoBoros.ai — Internal tooling. Not yet published.
