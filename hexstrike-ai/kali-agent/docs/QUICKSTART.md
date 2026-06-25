# KALI AGENT — QUICKSTART GUIDE
## Deploy to First Scan in 30 Minutes

---

### Prerequisites

You need:
- Kali Linux machine (bare metal, VM, or WSL2)
- Python 3.10+ and pip
- Node.js 18+ and npm
- Internet access (for tool installation)

Optional:
- Shodan API key (free at https://account.shodan.io)
- Docker (for mcp-security-hub)
- VirusTotal API key (free at https://www.virustotal.com)

---

### Step 1: Install (5 minutes)

```bash
# Download the package
# (from Claude conversation or GitHub)

# Extract
tar xzf kali-agent-full.tar.gz

# Run installer
cd hexstrike-modules
chmod +x install_kali_agent.sh
./install_kali_agent.sh
```

The installer handles Python deps, Desktop Commander, directory creation,
and optionally Shodan MCP, Docker builds, and systemd service.

---

### Step 2: Verify (2 minutes)

```bash
cd ~/hexstrike-ai

# Run unit tests
python3 test_modules.py
# Expected: 39/39 PASSED

# Run integration tests
python3 integration_test.py
# Expected: 74/74 PASSED
```

---

### Step 3: Start HexStrike (1 minute)

```bash
# Option A: Direct
cd ~/hexstrike-ai
python3 hexstrike_mcp.py

# Option B: systemd (if installed)
sudo systemctl start hexstrike
```

HexStrike MCP server is now listening on stdio for Claude connections.

---

### Step 4: Configure Claude (3 minutes)

Add to `~/.claude.json` (or `claude_desktop_config.json`):

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
      "env": { "SHODAN_API_KEY": "YOUR_KEY" }
    }
  }
}
```

Restart Claude Desktop/Code after editing.

---

### Step 5: Your First CTF Engagement (15 minutes)

Open Claude and try this:

```
I want to run a penetration test against a HackTheBox machine.
Target: 10.10.10.5
It's a CTF lab environment.
```

The Curator will:
1. Initialize scope-guard in CTF mode
2. Run passive + active recon (nmap, subfinder, whatweb)
3. Scan for vulnerabilities (nuclei, nikto)
4. Research exploits (searchsploit)
5. Generate findings report

**Or use the structured approach:**

```
Initialize a CTF engagement:
- Target: 10.10.10.5
- Platform: HackTheBox
- Type: CTF
- Run full recon + vuln scan
```

---

### Step 6: Your First Real Engagement

**⚠️ REQUIRES WRITTEN AUTHORIZATION**

```
Initialize an external penetration test:
- Client: Example Corp
- Target: example.com
- In scope: *.example.com, 203.0.113.0/24
- Excluded: mail.example.com, production-db.example.com
- Authorization: Written auth signed 2026-04-01, ref ECORP-2026
- Methodology: PTES
- Run passive recon first
```

Scope-guard will validate every tool call. Audit logger will record everything.

---

### Available Commands (Natural Language)

Once configured, you can ask Claude:

**Recon:**
- "Run passive recon on example.com"
- "What subdomains exist for example.com?"
- "Port scan 10.0.0.1 with service detection"
- "Look up 203.0.113.10 on Shodan"

**Vulnerability Scanning:**
- "Scan example.com for vulnerabilities"
- "Run OWASP Top 10 tests against https://app.example.com"
- "Check for SQL injection on the search page"
- "What CVEs affect nginx 1.24?"

**Exploitation (operator-gated):**
- "Search for exploits matching WordPress 6.4"
- "Generate a reverse shell payload for Linux x64"
- "Prepare a Metasploit resource script for CVE-2024-12345"

**Post-Exploitation (operator-gated):**
- "Run LinPEAS on the compromised host"
- "Enumerate the Active Directory domain"
- "Check for Kerberoastable accounts"
- "What ADCS templates are vulnerable?"

**Reporting:**
- "Generate a pentest report from the findings"
- "Export findings to CSV"
- "Export findings to Jira format"
- "Create the executive summary"

---

### Troubleshooting

| Problem | Fix |
|---------|-----|
| "No engagement initialized" | Run `init_engagement()` first or tell Claude the scope |
| "SCOPE VIOLATION" | Target is outside authorized scope — check your config |
| "HexStrike unreachable" | Start with `python3 hexstrike_mcp.py` or `systemctl start hexstrike` |
| "Command not found: nuclei" | Install missing tool: `sudo apt install nuclei` |
| "SHODAN_API_KEY not set" | Export: `export SHODAN_API_KEY=your_key` |
| Tests fail | Ensure you're in the hexstrike-ai directory with all .py files |

---

### File Locations

```
~/hexstrike-ai/              ← HexStrike modules + MCP server
/tmp/pentest/                ← Engagement working directories
  └── ENG-2026-001/
      ├── audit.jsonl        ← Master audit trail
      ├── scope_audit.jsonl  ← Scope check log
      ├── nmap_scan.txt      ← Tool output
      ├── nuclei_results.json
      └── reports/
          └── pentest_report.docx
/var/log/hexstrike/          ← Service logs (if using systemd)
~/.claude.json               ← MCP server configuration
```

---

### Architecture Summary

```
You (Claude) → skill triggered → SKILL.md loaded → tools called

Skills chain:
  scope-guard → recon-osint → threat-intel → vuln-analysis
  → web-app-security → exploit-dev → payload-craft
  → post-exploit → credential-attack → active-directory
  → network-forensics → red-team-report

Every tool call goes through:
  1. scope-guard.validate(target)     ← Is this authorized?
  2. _validate_command(cmd)           ← Is this command safe?
  3. subprocess.run(shell=False)      ← Execute safely
  4. sanitize_tool_output(result)     ← Strip injection attempts
  5. audit_logger.log_tool_execution  ← Record everything
```
