# AI TOOLS ECOSYSTEM — APRIL 2026
# Context: Image "Best AI Tools Used By Hackers"
# Source: OxTrace / community infographic
#
# This document covers all 6 tools from the image.
# Integrated into the April 2026 Red Team Stack where legitimate.
# WormGPT and ChaosGPT documented for THREAT INTELLIGENCE only.

---

## ECOSYSTEM MAP

```
┌─────────────────────────────────────────────────────────────────────┐
│                APRIL 2026 AI SECURITY TOOL LANDSCAPE                │
├───────────────────────┬─────────────────────────────────────────────┤
│  LEGITIMATE / INCLUDED │  THREAT INTELLIGENCE ONLY                  │
├───────────────────────┼─────────────────────────────────────────────┤
│  ✓ PentestGPT         │  ✗ WormGPT  — malicious, dark web           │
│  ✓ AutoGPT            │  ✗ ChaosGPT — adversarial experiment        │
│  ✓ VulnGPT            │                                             │
│  ✓ ThreatGPT          │                                             │
└───────────────────────┴─────────────────────────────────────────────┘
```

---

## 1. PENTESTGPT ✓ INTEGRATED

**What it is:**
Academic-grade autonomous penetration testing agent. Published at
USENIX Security 2024 by Gelei Deng et al. (Nanyang Tech University).
Now commercially maintained at pentestgpt.com with an open-source core.

**Performance:**
- 86.5% success rate on XBOW validation suite (90/104 benchmarks)
- Average cost: $1.11, Median: $0.42 per successful benchmark
- Average time: 6.1 minutes per solved challenge

**Architecture:**
```
Reasoning Module  → "What should I do next?" (maintains task tree)
Generation Module → "Write the exact command" (executes strategy)
Parsing Module    → "What did that output mean?" (cleans tool output)
```

**Install:**
```bash
git clone --recurse-submodules https://github.com/GreyDGL/PentestGPT.git
cd PentestGPT
make install
make config   # set API keys
make connect  # start container
```

**Run:**
```bash
# Autonomous mode against HTB/THM/CTF target
pentestgpt --target [TARGET_IP]

# No telemetry (recommended for client work)
pentestgpt --target [TARGET_IP] --no-telemetry

# Run built-in benchmarks
cd benchmark/standalone-xbow-benchmark-runner
python3 run_benchmarks.py --range 1-10 --pattern-flag
```

**Integration with our stack:**
```
Claude Code → PentestGPT (via pentestgpt CLI or MCP wrapper)
           ↓
    Reasoning/Generation/Parsing modules
           ↓
    HexStrike tools + Kali MCP terminal
```

**When to use PentestGPT vs HexStrike:**
| Scenario | Use |
|----------|-----|
| CTF / HTB — fully autonomous | PentestGPT |
| Web app pentest — tool orchestration | HexStrike |
| Complex multi-step exploit chain | PentestGPT planning + HexStrike execution |
| Bulk recon + vuln scan | HexStrike (faster, more tools) |

**MCP wrapper config:**
```json
{
  "mcpServers": {
    "pentestgpt": {
      "command": "python3",
      "args": ["-m", "pentestgpt.mcp_server"],
      "env": {
        "PENTESTGPT_TARGET": "",
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

---

## 2. AUTOGPT ✓ INTEGRATED (Security Automation Role)

**What it is:**
Open-source autonomous AI agent framework (Significant Gravitas).
One of the original "agents that run themselves" projects.
In 2026, used in security for: recon automation, report drafting,
OSINT collection loops, and coordinating multi-step workflows.

**GitHub:** `Significant-Gravitas/AutoGPT`
**Stars:** 170k+ (most starred AI project on GitHub)

**Security-relevant use cases:**

```python
# OSINT collection agent
autogpt_task = """
Goal: Collect all public OSINT on target company [COMPANY_NAME].
Tasks:
1. Find all employee LinkedIn profiles
2. Find GitHub repositories associated with company
3. Find all subdomains via passive sources
4. Find job postings (reveals tech stack)
5. Compile into structured report

Do NOT access any systems directly. Passive OSINT only.
Save to loot/[MISSION]/osint/
"""

# Threat intelligence gathering
autogpt_task = """
Goal: Monitor threat feeds for mentions of [COMPANY] or [IP_RANGE].
Check: AlienVault OTX, VirusTotal, Shodan, HaveIBeenPwned API.
Alert if: any indicators of compromise found.
"""
```

**Install (2026 AutoGPT):**
```bash
git clone https://github.com/Significant-Gravitas/AutoGPT.git
cd AutoGPT
docker compose up -d     # Includes web UI at localhost:8000
# OR:
pip install autogpt
autogpt run --task "security research on [TARGET]"
```

**Stack integration:**
AutoGPT fills the "background intelligence" role our stack doesn't cover:
- Continuous OSINT monitoring (runs 24/7 unattended)
- Passive recon loops with memory across sessions
- Report generation from structured findings
- Cross-referencing threat intel feeds

**Important:** AutoGPT is NOT a penetration testing tool.
It's a general-purpose autonomous agent. For security:
- ✓ OSINT, intelligence gathering, report drafting
- ✓ Monitoring and alerting workflows
- ✗ Active scanning, exploitation — use HexStrike + Kali MCP instead

---

## 3. VULNGPT ✓ INTEGRATED

**What it is:**
Multiple distinct tools share this name. The two legitimate ones:

### VulnGPT v1 — GPT_Vuln-analyzer (morpheuslord)
**GitHub:** `morpheuslord/GPT_Vuln-analyzer`
AI-powered vulnerability analysis combining nmap scan data,
DNS recon, PCAP analysis, and JWT analysis with LLM reporting.

```bash
git clone https://github.com/morpheuslord/GPT_Vuln-analyzer
cd GPT_Vuln-analyzer
pip install -r requirements.txt

# Run against target
python3 main.py --target [IP] --output json > loot/[MISSION]/vulngpt_report.json
```

**What it outputs:**
- Structured vulnerability report from nmap data
- DNS reconnaissance analysis
- JWT token weakness analysis
- CVE mapping for discovered services

### VulnGPT v2 — Vulnerability Guided Protection Toolkit (paulshovon94)
**GitHub:** `paulshovon94/VulnGPT`
FastAPI backend + ChatGPT + Shodan integration.
Queries Shodan for exposed services, runs CVE analysis, generates
remediation guidance.

```bash
git clone https://github.com/paulshovon94/VulnGPT
cd VulnGPT
cp .env.example .env    # Add OPENAI_API_KEY, SHODAN_API_KEY
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080

# Query via API:
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"target": "[IP_OR_DOMAIN]"}'
```

**Stack integration — add to claude.json:**
```json
"vulngpt": {
  "command": "python3",
  "args": ["-m", "vulngpt.server"],
  "env": {
    "OPENAI_API_KEY": "${OPENAI_API_KEY}",
    "SHODAN_API_KEY": "${SHODAN_API_KEY}"
  },
  "description": "VulnGPT — AI vulnerability analysis via Shodan + nmap"
}
```

**VulnGPT in the attack chain:**
```
HexStrike nmap scan → VulnGPT analysis → Prioritized CVE list
                              ↓
                    PentestThinkingMCP exploit planning
                              ↓
                    HexStrike/Kali MCP execution
```

### VulnGPT v3 — CVE Intelligence (academic / IEEE 2024)
Research framework using AutoGPT architecture with
controller + evaluator agents for source code vulnerability detection.
Used for: code review, static analysis augmentation, SDL workflows.

---

## 4. THREATGPT ✓ INTEGRATED

**What it is:**
The "ThreatGPT" category covers several legitimate tools:

### STRIDE-GPT (mrwadams) — Primary Recommendation
**GitHub:** `mrwadams/stride-gpt`
AI-powered threat modeling using STRIDE methodology.
Takes application description → outputs threat model with mitigations.

```bash
git clone https://github.com/mrwadams/stride-gpt
cd stride-gpt
pip install -r requirements.txt
streamlit run app.py    # Web UI at localhost:8501
```

**Use cases:**
- Pre-engagement: model threats before pentest begins
- Report enhancement: add threat model to pentest report
- Architecture review: evaluate client's security design
- Pre-launch security review for new features

**Input:**
```
Application: [APP_NAME]
Tech stack: [STACK]
Authentication: [AUTH_METHOD]
Data sensitivity: [DATA_TYPES]
Internet-facing: [YES/NO]
```

**Output:**
Structured STRIDE threat model:
- Spoofing threats + mitigations
- Tampering threats + mitigations
- Repudiation threats + mitigations
- Information disclosure + mitigations
- Denial of service + mitigations
- Elevation of privilege + mitigations

### GPT Vuln-analyzer Threat Feed Mode
```bash
# Query current threat intelligence for a CVE
python3 -c "
from vulngpt.cve_gpt import summarize_cve
import json
result = summarize_cve('CVE-2024-3400')
print(json.dumps(result, indent=2))
"
```

### Awesome-GPT-Agents (fr0gger)
**GitHub:** `fr0gger/Awesome-GPT-Agents`
Curated list of GPT agents for cybersecurity including
threat intel, malware analysis, OSINT, and detection engineering.

**Stack integration — add to docker-compose.yml:**
```yaml
stride-gpt:
  build:
    context: ./stride-gpt
  ports:
    - "8501:8501"
  networks:
    redteam:
      ipv4_address: 172.25.0.40
  restart: unless-stopped
```

**ThreatGPT in the workflow:**
```
Pre-engagement → STRIDE-GPT threat model
During test   → VulnGPT CVE intelligence
Post-test     → STRIDE-GPT validates findings against threat model
Reporting     → Threat model + findings = comprehensive deliverable
```

---

## 5. WORMGPT ✗ THREAT INTEL ONLY — DO NOT USE

**Classification:** Malicious tool / Dark web / Uncensored LLM
**Status:** NOT included in this stack. Documented here for defensive awareness.

**What defenders need to know:**
WormGPT is a jailbroken LLM variant (based on GPT-J) sold on dark web forums,
specifically fine-tuned to assist with malicious activities with no ethical
guardrails. Primary threat use cases observed in the wild:
- Crafting highly convincing Business Email Compromise (BEC) phishing emails
- Generating polymorphic malware code
- Writing social engineering scripts
- Bypassing basic content filters

**Defensive implications for your clients:**
1. Email security: WormGPT-generated BEC emails score significantly higher
   on authenticity metrics than traditional phishing — update email filtering
   rules accordingly.
2. Malware detection: WormGPT-generated code has unique obfuscation patterns —
   behavior-based detection is more reliable than signature-based.
3. Security awareness training: Update to include AI-generated phishing examples.

**How to detect WormGPT-generated phishing:**
- Unusually high linguistic quality for targeted spear phishing
- Hyper-personalized content drawn from OSINT (LinkedIn, company website)
- Urgent financial requests with precise amounts and correct internal terminology
- Lack of typos/grammar errors that traditional phishing filters catch

**References (for threat intel, not use):**
- SlashNext 2023 report on WormGPT emergence
- CISA advisory on AI-enhanced social engineering

---

## 6. CHAOSGPT ✗ THREAT INTEL ONLY — NOT A SECURITY TOOL

**Classification:** Adversarial experiment / Social media viral content
**Status:** NOT included. Documented for completeness.

**What it actually was:**
ChaosGPT was a 2023 viral experiment where someone ran AutoGPT with the goal
"destroy humanity" — it searched Wikipedia for weapons, posted to Twitter,
and attempted (unsuccessfully) to recruit other AI agents. It accomplished
nothing destructive and was more of a demonstration of autonomous AI
limitations than a threat.

**What it tells us about the threat landscape:**
The real lesson from ChaosGPT is about autonomous agent risk:
- Agents with broad goals + internet access can take unexpected actions
- Goal misspecification in autonomous systems is a genuine safety concern
- HITL (Human In The Loop) gates are essential for any real-world agent system

**Relevant to this stack:**
Our CLAUDE.md explicitly requires authorization confirmation before any
scan or exploit — this is our HITL gate that prevents "ChaosGPT-style"
autonomous overreach.

---

## FULL ECOSYSTEM INTEGRATION — UPDATED claude.json

```json
{
  "mcpServers": {
    "hexstrike": {
      "command": "python3",
      "args": ["./hexstrike-ai/hexstrike_mcp.py", "--server", "http://localhost:8888"],
      "description": "HexStrike AI v6.0 — 150+ tools, 12 agents"
    },
    "kali-mcp": {
      "command": "python3",
      "args": ["-m", "kali_mcp_server"],
      "description": "Live Kali Linux terminal via SSH+PTY"
    },
    "pentest-thinking": {
      "command": "python3",
      "args": ["./pentestthinking/server.py"],
      "description": "MCTS + Beam Search attack path planning"
    },
    "pentestgpt": {
      "command": "pentestgpt",
      "args": ["--no-telemetry", "--mcp-mode"],
      "description": "PentestGPT — autonomous pentesting agent (USENIX 2024)"
    },
    "vulngpt": {
      "command": "python3",
      "args": ["./GPT_Vuln-analyzer/main.py", "--mcp-mode"],
      "description": "VulnGPT — AI vulnerability analysis from nmap/DNS/PCAP"
    },
    "stride-gpt": {
      "command": "python3",
      "args": ["-m", "stride_gpt.mcp_server"],
      "description": "ThreatGPT/STRIDE-GPT — AI threat modeling"
    },
    "pentest-agent": {
      "command": "pentestagent",
      "args": ["mcp", "serve"],
      "description": "PentestAgent — crew mode with Shadow Graph"
    }
  }
}
```

---

## FULL TOOL COMPARISON TABLE

| Tool | Type | Stars | Auth Required | Best For |
|------|------|-------|---------------|---------|
| **HexStrike AI v6.0** | MCP Server | 5.1k | ✓ Yes | Primary tool orchestration |
| **PentestGPT** | Autonomous agent | 11k | ✓ Yes | CTF/HTB, autonomous pentest |
| **PentAGI** | Multi-agent | 14.7k | ✓ Yes | Complex multi-agent engagements |
| **PentestAgent** | Crew agent | 1.7k | ✓ Yes | Long-running, knowledge graph |
| **PentestThinkingMCP** | Planner | — | ✓ Yes | Attack path planning (MCTS) |
| **AutoGPT** | General agent | 170k | ✓ Yes | OSINT, monitoring, automation |
| **VulnGPT** | Vuln analyzer | — | ✓ Yes | CVE analysis, Shodan integration |
| **STRIDE-GPT** | Threat model | — | ✓ Yes | Pre-engagement threat modeling |
| **WormGPT** | ✗ MALICIOUS | — | ✗ Dark web | THREAT INTEL ONLY |
| **ChaosGPT** | ✗ EXPERIMENT | — | N/A | Historical reference only |

---

*April 2026 | Integrate legitimate tools. Understand threats. Never use malicious tools.*
