# ADDITIONAL AI TOOLS — APRIL 2026 ECOSYSTEM
# Beyond the OxTrace image — community top picks
# All legitimate research/authorized testing tools

---

## ECOSYSTEM EXPANSION — 10 MORE AI TOOLS

```
TOOL              STARS    ROLE IN STACK
────────────────────────────────────────────────────────────────
PentAGI           14.7k    Multi-agent autonomous (most polished)
CAI               12.5k    DARPA ARC finalist — proven in wild
hackingBuddyGPT   1.2k     Minimal ReAct agent — great for learning
Basilisk          —        AI red teaming / LLM jailbreak framework
Nebula CLI        —        Human-in-loop AI terminal assistant
Raptor            —        Claude Code skill-based pentesting
AutoPentest-AI    1.7k     68+ tools, 109 WSTG tests, BSidesPDX 2025
PentaGI           —        Vxcontrol multi-agent (viper + msf + LLM)
ARTEMIS           —        DARPA ARC #4 — beat 9/10 human pentesters
PyRIT             3.5k     Python Risk ID Tool for generative AI
```

---

## 1. PentAGI — vxcontrol/pentagi
**GitHub:** vxcontrol/pentagi | **Stars:** 14.7k | **License:** MIT

The most polished open-source multi-agent autonomous pentesting system.
Launched early 2026, reached #1 trending on GitHub.

**Architecture:**
```
PentAGI Multi-Agent System
├── Orchestrator Agent     ← top-level strategy
├── Research Agent         ← web search + CVE intel
├── Infrastructure Agent   ← target scanning + enum
├── Coding Agent           ← exploit dev + scripting
└── Reporting Agent        ← findings → report
     │
     ├── Docker sandbox (isolated execution)
     ├── Long-term memory (vector DB)
     ├── Web search integration
     └── 20+ integrated security tools
```

**Install:**
```bash
git clone https://github.com/vxcontrol/pentagi.git
cd pentagi
cp .env.example .env
# Set: ANTHROPIC_API_KEY or OPENAI_API_KEY
docker compose up -d
# Web UI at http://localhost:8080
```

**Use in stack:**
```
PentAGI excels at: long-running autonomous assessments
                    complex multi-stage attack chains
                    tasks requiring web research + execution

PentAGI vs PentestGPT:
  PentestGPT → academic validation, CTF focus, CLI
  PentAGI    → enterprise-grade UI, multi-agent, persistent memory

When to use PentAGI:
  Long multi-day engagements → "run overnight"
  Complex environments with many moving parts
  When you want a web UI to monitor progress
```

**Claude Code integration:**
```json
"pentagi": {
  "command": "python3",
  "args": ["-m", "pentagi.mcp", "--host", "localhost", "--port", "8080"],
  "cwd": "./pentagi",
  "description": "PentAGI — 14.7k stars, multi-agent autonomous system"
}
```

---

## 2. CAI — Cybersecurity AI (Ostorlab)
**GitHub:** Ostorlab/agent-cai | **Stars:** 12.5k

CAI stands out as the most **reliably tested** tool in the ecosystem.
It was a finalist in DARPA's AI Cyber Challenge (ARC) 2025.
Tested against vulnbank.org and found: SQL injection auth bypass, 
exposed Werkzeug debugger RCE, IDOR, mass assignment, JWT issues.

**What makes CAI different:**
- Community-first research framework
- Standardized AI-driven cybersecurity tooling
- Works with multiple LLM backends
- Specifically designed to avoid false positives

**Install:**
```bash
git clone https://github.com/Ostorlab/agent-cai.git
cd agent-cai
pip install -r requirements.txt

# Configure:
export OPENAI_API_KEY=sk-...
# OR
export ANTHROPIC_API_KEY=sk-ant-...

# Run against target:
python3 cai.py --target https://target.com --report json
```

**Use in stack:**
```
After HexStrike nuclei scan finds potential vulns:
→ Run CAI for confirmation + exploitation
→ CAI provides verified PoC (not just flagging)
→ Import CAI findings into report

Particularly strong at:
  Web application logic flaws
  Authentication bypass variations
  IDOR with proof of exploitation
```

---

## 3. hackingBuddyGPT — andreashappe
**GitHub:** andreashappe/hackingBuddyGPT

The original minimal LLM pentesting agent. ~50 lines of Python.
Academically validated. Great for understanding how agents work
before using more complex systems.

**Install:**
```bash
git clone https://github.com/andreashappe/hackingBuddyGPT.git
cd hackingBuddyGPT
pip install -r requirements.txt

# Run against SSH target (CTF/lab only):
python3 main.py --target [IP] --model claude-sonnet-4-20250514
```

**Use in stack:**
```
Learning tool — understand ReAct loop before using PentestGPT/PentAGI
Lightweight SSH brute-force + privilege escalation agent
Educational: trace every step, understand what LLM decides and why
Cost: very low (~$0.10-0.30 per attempt)
```

---

## 4. Basilisk — Open Source AI Red Teaming
**GitHub:** search "basilisk llm red team genetic"

AI red teaming framework with genetic prompt evolution.
Automated LLM security testing — probe language models for jailbreaks,
prompt injection, data extraction, guardrail bypasses.

**32 attack modules covering OWASP LLM Top 10:**
```
- Direct prompt injection
- Indirect prompt injection  
- Jailbreak via roleplay
- Context window manipulation
- Training data extraction
- Model inversion attacks
- Supply chain / plugin attacks
- Insecure output handling
```

**Install:**
```bash
pip install basilisk-ai

# Test an LLM for vulnerabilities:
basilisk scan --target gpt-4o --modules all --output report.json

# Test your own LLM deployment:
basilisk scan --target http://localhost:8080/v1/chat --api-key [KEY]
```

**Use in stack (Az's interest — AI security research):**
```
If scope includes AI systems → run Basilisk
Bug bounty on AI company → Basilisk finds jailbreaks + injection
Red team against AI chatbot → full OWASP LLM Top 10 coverage
Research: test prompt injection resistance of new models
```

---

## 5. Nebula — AI Terminal Assistant
**GitHub:** search "nebula ai penetration testing CLI"

AI-assisted CLI tool for recon, note-taking, and vulnerability
analysis guidance. Human-driven — AI suggests, human executes.
Supports OpenAI, Llama, Mistral, DeepSeek.

**Philosophy:** Human expertise + AI speed. Not fully autonomous.
Perfect for: learning, assisted manual testing, structured note-taking.

**Install:**
```bash
pip install nebula-pentest

# Configure model:
nebula config --model deepseek-chat --api-key [KEY]
# OR local: nebula config --model ollama/llama3.1

# Start assisted session:
nebula start --target [IP] --mission [NAME]
```

**Commands:**
```
nebula recon     → guide next recon step
nebula analyze   → analyze pasted tool output
nebula suggest   → suggest next attack vector
nebula note      → save structured finding
nebula report    → generate session summary
```

---

## 6. Raptor — Claude Code Skill-Based Pentesting

Raptor uses Claude Code's native skill/agent infrastructure
rather than MCP servers. Define attack patterns as `.md` skill files,
chain them together, let Claude Code execute autonomously.

**GitHub:** search "raptor claude code pentesting skills"

**Skill file format:**
```markdown
# skill: raptor-recon
Trigger: "raptor recon [target]"

Steps:
1. Run nmap -sV --open [TARGET]
2. Identify all web services
3. For each web service: run nikto + gobuster
4. Run nuclei critical templates
5. Compile findings into structured report
```

**Why Raptor matters for this stack:**
```
This is the "skills" equivalent of what Az has been building.
Raptor = using CLAUDE.md skills + playbooks to orchestrate everything.
Our stack IS a Raptor-style setup.

Add Raptor skill files to skills/ directory:
  skills/raptor-recon.md
  skills/raptor-web.md
  skills/raptor-exploit.md
  
Claude Code loads them automatically → instant skill-based automation.
```

---

## 7. AutoPentest-AI — bhavsec
**GitHub:** bhavsec/autopentest-ai | **Stars:** 1.7k
**Presented at:** BSidesPDX 2025

68+ tools exposed as MCP endpoints, 109 WSTG tests,
31 PortSwigger technique guides. Tested with o3 and Gemini 2.5 Flash.

**Unique features:**
- OWASP Web Security Testing Guide coverage (109 tests)
- PortSwigger web security techniques integration
- Automated report generation aligned to OWASP

**Install:**
```bash
git clone https://github.com/bhavsec/autopentest-ai.git
cd autopentest-ai
pip install -e .

# Start MCP server:
autopentest-mcp --port 8891
```

**claude.json addition:**
```json
"autopentest": {
  "command": "python3",
  "args": ["-m", "autopentest.mcp", "--port", "8891"],
  "cwd": "./autopentest-ai",
  "description": "AutoPentest-AI — 68+ tools, 109 WSTG tests (BSidesPDX 2025)"
}
```

---

## 8. PyRIT — Python Risk Identification Tool for Generative AI
**GitHub:** Azure/PyRIT | **Stars:** 3.5k | **Author:** Microsoft/Azure

Open-source framework for identifying risks in generative AI systems.
Used by security professionals and AI red teamers at Microsoft.

**Use cases:**
```
Testing your own AI deployment for vulnerabilities
Bug bounty on AI products
Red team against LLM-powered applications
Compliance testing for AI safety requirements
```

**Install:**
```bash
pip install pyrit

# Run AI red team assessment:
python3 -c "
from pyrit.orchestrator import RedTeamingOrchestrator
from pyrit.prompt_target import AzureOpenAIChatTarget

target = AzureOpenAIChatTarget(...)  # target AI system
orchestrator = RedTeamingOrchestrator(
    attack_strategy='prompt_injection',
    prompt_target=target,
    verbose=True
)
orchestrator.apply_attack_strategy_until_completion(max_turns=10)
"
```

---

## 9. ARTEMIS — DARPA ARC Finalist
Academic system. December 2025: beat 9 out of 10 human pentesters
on a live 8,000-host enterprise network. Cost: $18/hour.

**Not publicly available but informs our architecture:**
```
ARTEMIS proved: AI agents are now competitive with
junior/mid human pentesters on structured assessments.
Cost advantage is ~10x over human-only teams.
Speed advantage is ~5-20x.

The architecture (similar to what we've built):
  Multi-agent team with specialized roles
  Real-time knowledge graph of the environment
  Adaptive reasoning loop (not just checklists)
  HITL gates at critical decision points
```

---

## 10. XBOW — Commercial, Top HackerOne
XBOW's autonomous agent became #1 on HackerOne in June 2025,
later publishing 1,060+ valid submissions.

**Lessons for our stack:**
```
XBOW proved: AI can find real bugs at production scale.
Their approach: deep tool integration + persistent memory.
This validates our HexStrike + PentestAgent + loot architecture.
```

---

## Extended claude.json with All Tools

```json
{
  "mcpServers": {
    "pentagi":      { "command": "python3", "args": ["-m", "pentagi.mcp"], "cwd": "./pentagi" },
    "cai":          { "command": "python3", "args": ["-m", "cai.mcp"], "cwd": "./agent-cai" },
    "autopentest":  { "command": "python3", "args": ["-m", "autopentest.mcp", "--port", "8891"], "cwd": "./autopentest-ai" },
    "pyrit":        { "command": "python3", "args": ["-m", "pyrit.mcp"], "description": "AI red teaming framework" }
  }
}
```

---

## Tool Selection Guide — Full Ecosystem

```
WANT                           USE
─────────────────────────────────────────────────────────────────
Best web app automation        HexStrike web profile
Best autonomous CTF solving    PentestGPT
Best for long engagements      PentAGI (web UI, memory)
Most verified findings         CAI (Ostorlab, DARPA tested)
Learning how agents work       hackingBuddyGPT (~50 lines)
Testing AI systems             Basilisk + PyRIT
Assisted (not autonomous)      Nebula CLI
WSTG/PortSwigger coverage      AutoPentest-AI
Multi-agent crew               PentestAgent
MCTS attack planning           PentestThinkingMCP
OSINT + monitoring             AutoGPT
CVE intelligence               VulnGPT
Threat modeling                STRIDE-GPT
Live Kali terminal             Kali MCP
150+ tools one endpoint        HexStrike
```

---

*April 2026 | 39+ open-source AI pentesting tools exist — this doc covers the best 20+*
