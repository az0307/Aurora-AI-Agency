# KALI AGENT — COMPLETE OPERATIONS GUIDE
## "You're on Kali. Now What?"

**AutoBoros.ai | Aurora AI Agency | April 2026**
**Research-backed best practices from OWASP 2025, CISA KEV, Cobalt pentest data, and AI-augmented pentest methodology**

---

## PHASE 0: FIRST 30 MINUTES ON KALI

### 0.1 — System Update & Tool Verification
```bash
# Update everything first
sudo apt update && sudo apt full-upgrade -y

# Verify core tools are installed
for tool in nmap nuclei nikto sqlmap subfinder amass whatweb ffuf gobuster \
  hydra john hashcat searchsploit metasploit-framework crackmapexec \
  enum4linux-ng wpscan feroxbuster tcpdump tshark whois dig curl socat \
  responder impacket-scripts evil-winrm certipy bloodhound; do
  which $tool &>/dev/null && echo "✓ $tool" || echo "✗ MISSING: $tool"
done

# Install anything missing
sudo apt install -y kali-tools-top10 kali-tools-web kali-tools-passwords \
  kali-tools-exploitation kali-tools-information-gathering seclists
```

### 0.2 — Deploy Kali Agent
```bash
# Extract the package
tar xzf kali-agent-full.tar.gz
cd kali-agent-repo

# Run installer (handles Python deps, dirs, optional Docker/systemd)
chmod +x install_kali_agent.sh
./install_kali_agent.sh

# Verify tests pass
python3 test_modules.py        # 39 unit tests
python3 integration_test.py    # 74 integration tests
```

### 0.3 — Install MCP Connections
```bash
# 1. Desktop Commander (gives Claude terminal access)
npx @wonderwhy-er/desktop-commander@latest setup

# 2. Shodan MCP (CVE/IP intel — free tier works)
npm install -g @burtthecoder/mcp-shodan
# Get free key: https://account.shodan.io

# 3. Configure Claude
cat > ~/.claude.json << 'EOF'
{
  "mcpServers": {
    "desktop-commander": {
      "command": "npx",
      "args": ["-y", "@wonderwhy-er/desktop-commander@latest"]
    },
    "shodan": {
      "command": "mcp-shodan",
      "env": { "SHODAN_API_KEY": "YOUR_KEY_HERE" }
    },
    "hexstrike": {
      "command": "python3",
      "args": ["/home/kali/hexstrike-ai/hexstrike_mcp.py"],
      "env": { "PENTEST_BASE": "/tmp/pentest" }
    }
  }
}
EOF
```

### 0.4 — Start HexStrike
```bash
# Option A: Direct
cd ~/hexstrike-ai && python3 hexstrike_mcp.py

# Option B: As a service
sudo cp hexstrike.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now hexstrike

# Verify
curl -s http://localhost:8888/health || echo "HexStrike not running"
```

### 0.5 — Update Tool Databases
```bash
# Nuclei templates (run weekly)
nuclei -update-templates

# SearchSploit / ExploitDB
sudo searchsploit -u

# Nmap scripts
sudo nmap --script-updatedb

# WPScan (needs free API token from wpscan.com)
wpscan --update

# Wordlists (SecLists if not installed)
sudo apt install -y seclists
ls /usr/share/seclists/
```

---

## PHASE 1: AI-AUGMENTED PENTEST WORKFLOW

### The 2026 Reality
Based on research from real pentest practitioners using AI in 2026:
- AI augmentation yields **30-40% more findings** in the same time window
- AI handles the "grunt work": output parsing, CVE correlation, report drafting
- Human testers focus on: business logic, creative exploitation, client context
- The winning formula: **AI for breadth, human for depth**

### How the Kali Agent Skill Chain Works

```
You tell Claude what to do in natural language
     ↓
Curator (AI orchestrator) generates a playbook
     ↓
Each step triggers a skill → skill calls tools → tools return results
     ↓
AI parses results, correlates with threat intel, prioritizes findings
     ↓
You make the human decisions: exploit? pivot? stop?
     ↓
AI generates the report from the audit trail
```

### Your 17 Skills (what to say to Claude)

| To do this... | Say this... | Skill triggered |
|---|---|---|
| Start an engagement | "Initialize a pentest against example.com" | scope-guard |
| Passive recon | "Run passive recon on example.com" | recon-osint |
| Port scan | "Scan 10.0.0.1 for open ports" | recon-osint |
| CVE lookup | "What CVEs affect nginx 1.24?" | threat-intel |
| Vuln scan | "Scan example.com for vulnerabilities" | vuln-analysis |
| Web app test | "Run OWASP Top 10 tests on the web app" | web-app-security |
| Find exploits | "Search for exploits for WordPress 6.4" | exploit-dev |
| Generate payload | "Create a reverse shell for Linux x64" | payload-craft |
| Crack hashes | "Crack these NTLM hashes with rockyou" | credential-attack |
| Privesc help | "Run LinPEAS and analyze the output" | post-exploit |
| AD attacks | "Enumerate the Active Directory domain" | active-directory |
| ADCS check | "Check for vulnerable certificate templates" | active-directory |
| Packet capture | "Analyze this pcap for credentials" | network-forensics |
| WiFi commands | "Generate WiFi handshake capture commands" | wireless-recon |
| Write report | "Generate the pentest report" | red-team-report |
| Quick reference | "What's the hashcat mode for NTLM?" | pentest-cheatsheet |
| CTF writeup | "Write up this box as a walkthrough" | ctf-walkthrough |

---

## PHASE 2: ENGAGEMENT OPERATIONS

### 2.1 — External Pentest Workflow

**Step 1: Scope + Recon (Day 1)**
```
Tell Claude:
"Initialize an external pentest:
- Client: [name]
- Target: [domain]
- In scope: [*.domain.com, IP ranges]
- Excluded: [mail, prod-db]
- Authorization: [reference]
Run passive recon first."
```
What happens: scope-guard validates, recon-osint runs subfinder/theHarvester/whois/dig, results feed threat-intel for enrichment.

**Step 2: Active Scanning (Day 1-2)**
```
"Run active recon — port scan all in-scope targets, fingerprint technologies, 
then scan for vulnerabilities with nuclei and nikto."
```
What happens: nmap service detection, whatweb fingerprinting, nuclei CVE/exposure/misconfig templates, nikto web server scan.

**Step 3: Web App Deep Dive (Day 2-3)**
```
"Run OWASP Top 10 tests against https://app.example.com.
Focus on injection, access control, and authentication."
```
What happens: ffuf directory discovery, sqlmap on parameters, XSStrike on inputs, auth testing.

**AI power move** — Feed findings to Claude and ask:
```
"I found these issues on the same application:
1. Reflected XSS in search (low)
2. Missing SameSite cookie attribute (info)
3. CORS allows arbitrary origins (medium)
4. User email visible in API response (low)
How could these be chained for a more severe attack?"
```

**Step 4: Exploitation (Day 3-4, operator-gated)**
```
"Search for exploits matching [product] [version].
Prepare a Metasploit resource script for CVE-XXXX-XXXXX."
```
You review, you approve, you execute. AI prepares, human confirms.

**Step 5: Post-Exploitation (Day 4-5, if scope permits)**
```
"Run LinPEAS output through analysis.
What are the top 3 privesc paths?"
```

**Step 6: Report (Day 5)**
```
"Generate the full pentest report.
Export findings to CSV and Jira format.
Also create a CTF-style walkthrough for our internal knowledge base."
```

### 2.2 — Key AI Augmentation Prompts (Research-Backed)

These prompts are from practitioners reporting 30-40% more findings:

**Recon analysis:**
> "Analyze these nmap results. For each service: known CVEs for this version? Most likely attack vectors? What to enumerate next?"

**WAF bypass:**
> "The target WAF is blocking my SQLi payloads. Based on these error responses, suggest 5 bypass techniques specific to this behavior."

**Exploit chain discovery:**
> "Given this technology stack [list], what multi-step attack chains could lead from initial access to full compromise?"

**Privesc analysis:**
> "Here's my LinPEAS output. Identify the top 3 privilege escalation paths ranked by reliability."

**Report writing (saves 3-5 hours per engagement):**
> "Convert these raw findings into professional report sections with: executive summary, technical details, reproduction steps, CVSS justification, and remediation with code examples."

---

## PHASE 3: WHAT TO KNOW — INTEL LANDSCAPE

### OWASP Top 10 2025 — What Actually Gets Found

Based on Cobalt's 2025 data from thousands of real pentests:

| # | What OWASP says | What pentesters actually find most |
|---|---|---|
| 1 | Broken Access Control | **XSS — 18.4% of all web findings** |
| 2 | Security Misconfiguration | **Missing security headers — ~70% of sites** |
| 3 | Supply Chain Failures | **Outdated WordPress plugins** |
| 4 | Insecure Design | **IDOR in API endpoints — #1 bug bounty category** |
| 5 | Injection | **SQLi — 10.6% of web findings** |

**The gap:** OWASP looks at strategic risk. Pentest data shows tactical reality. You need both. XSS + SQLi combined = 29% of all web findings — they're still the bread and butter despite OWASP deprioritizing injection.

### CISA KEV — What's Being Exploited Right Now

Most critical active exploits as of April 2026:
- **F5 BIG-IP APM** (CVE-2025-53521) — Pre-auth RCE, CVSS 9.3, ransomware target
- **Cisco FMC** (CVE-2026-20131) — Deserialization RCE as root, unauth
- **Citrix NetScaler** (CVE-2026-3055) — SAML memory corruption
- **Zimbra** (CVE-2025-68645) — Pre-auth file inclusion, active since Jan 2026
- **Versa SD-WAN** (CVE-2025-34026) — Auth bypass to admin endpoints
- **Langflow AI** (CVE-2026-33017) — AI platform code execution

### Top CWEs in CISA KEV 2025
1. **CWE-78** OS Command Injection (18 entries)
2. **CWE-502** Deserialization (14)
3. **CWE-22** Path Traversal (13)
4. **CWE-416** Use After Free (11)
5. **CWE-787** Out-of-bounds Write (10)

### AI Pentest Tools Landscape 2026

The competition and what you can learn from them:
- **PentAGI** — Open-source, multi-agent, Docker sandbox, 20+ tools. Similar architecture to Kali Agent.
- **BlacksmithAI** — Hierarchical multi-agent (orchestrator + specialists). Uses MCP for tool integration.
- **Penligent** — Commercial, "autonomous hacker", goal-directed exploitation with feedback loops
- **XBOW** — Autonomous web pentest, matches top HackerOne hunters on web vulns
- **NodeZero** — Autonomous network pentest, chains exploits to show real attack paths
- **Burp Suite + Burp AI** — MCP integration with Claude, agentic assistant for web testing

**Your competitive advantage with Kali Agent:** You own the infrastructure, the skills are customizable, the audit trail is yours, and you can combine AI breadth with human depth on every engagement.

---

## PHASE 4: ONGOING OPERATIONS

### Weekly Maintenance
```bash
# Update tools
sudo apt update && sudo apt upgrade -y
nuclei -update-templates
sudo searchsploit -u

# Check HexStrike health
systemctl status hexstrike

# Review audit logs from recent engagements
cat /tmp/pentest/*/audit.jsonl | python3 -c "
import json, sys
for line in sys.stdin:
    e = json.loads(line)
    print(f'{e.get(\"timestamp\",\"?\")[:16]} | {e.get(\"tool\",\"?\"):15} | {e.get(\"target\",\"?\")}')
" | tail -20
```

### After Each Engagement
```bash
# Export findings to all formats
python3 -c "from findings_exporter import export_all; export_all(findings, '/tmp/exports', 'ENG-XXXX')"

# Secure cleanup (archives audit log, shreds tool output)
./cleanup_engagement.sh ENG-XXXX --confirm

# Update knowledge base with new findings
# (Add unique discoveries to vuln-knowledge-base artifact)
```

### Monthly
```bash
# Review CISA KEV for new entries
# https://www.cisa.gov/known-exploited-vulnerabilities-catalog

# Update Kali Agent repo
cd ~/hexstrike-ai && git pull

# Run full test suite
python3 test_modules.py && python3 integration_test.py
```

---

## QUICK REFERENCE: TOOL → SKILL MAP

| Tool | Skill | When to use |
|---|---|---|
| nmap | recon-osint | Port scanning, service detection |
| subfinder / amass | recon-osint | Subdomain enumeration |
| nuclei | vuln-analysis | Template-based vuln scanning |
| sqlmap | web-app-security | SQL injection testing |
| ffuf / gobuster | web-app-security | Directory brute force |
| Burp Suite | web-app-security | Intercepting proxy (manual) |
| searchsploit | exploit-dev | ExploitDB local search |
| msfconsole | exploit-dev | Metasploit framework |
| msfvenom | payload-craft | Payload generation |
| hashcat / john | credential-attack | Hash cracking |
| hydra | credential-attack | Online brute force |
| BloodHound | active-directory | AD attack path mapping |
| impacket | active-directory | Windows protocol attacks |
| certipy | active-directory | ADCS certificate attacks |
| crackmapexec | active-directory | Multi-protocol cred testing |
| LinPEAS / WinPEAS | post-exploit | Privilege escalation enum |
| aircrack-ng | wireless-recon | WiFi security testing |
| tcpdump / tshark | network-forensics | Packet capture/analysis |

---

*AutoBoros.ai | Kali Agent Operations Guide | April 2026*
*Built from: OWASP Top 10 2025, CISA KEV, Cobalt pentest data, AI pentest practitioner research*
