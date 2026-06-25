# ARCHITECTURE — April 2026 Red Team Stack
# Full system design, data flows, and component relationships

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OPERATOR (Claude Code)                            │
│            claude --dangerously-skip-permissions                     │
│                                                                      │
│   CLAUDE.md loaded → 9 MCP servers available → playbooks indexed    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  MCP protocol
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼───────┐ ┌──────▼──────┐ ┌─────▼──────────┐
     │  HEXSTRIKE AI   │ │  KALI MCP   │ │ PENTEST-THINK  │
     │  v6.0 :8888/89  │ │  :8000/2222 │ │ MCTS+BeamSearch│
     │  150+ tools     │ │  SSH+PTY    │ │ Attack Planning │
     │  12 agents      │ │  14 tools   │ │                │
     └────────┬────────┘ └──────┬──────┘ └─────┬──────────┘
              │                 │               │
     ┌────────▼────────┐        │     ┌─────────▼──────────┐
     │   TOOL LAYER    │        │     │   PENTESTGPT        │
     │  nmap nuclei    │        │     │  Task Tree Reasoning │
     │  sqlmap ffuf    │        │     │  86.5% XBOW success │
     │  crackmapexec   │        │     │  Autonomous CTF     │
     │  metasploit     │◄───────┘     └─────────────────────┘
     │  gobuster...    │
     └─────────────────┘

     ┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
     │   VULNGPT v2    │ │ STRIDE-GPT   │ │  PENTESTAGENT    │
     │   :8090         │ │ :8501        │ │  (crew mode)     │
     │   CVE analysis  │ │ STRIDE model │ │  Shadow Graph    │
     │   Shodan intel  │ │ threat model │ │  RAG memory      │
     │   NVD queries   │ │              │ │  Multi-agent     │
     └────────┬────────┘ └──────┬───────┘ └──────────┬───────┘
              │                 │                     │
     ┌────────▼─────────────────▼─────────────────────▼───────┐
     │                  PERSISTENCE LAYER                       │
     │  PostgreSQL :5432 — scan history, findings, credentials  │
     │  Redis :6379      — LRU scan cache (30-day retention)   │
     └──────────────────────────────────────────────────────────┘

     ┌────────────────────────────────────────────────────────┐
     │               BACKGROUND INTELLIGENCE                   │
     │                                                        │
     │  AutoGPT (170k stars)                                  │
     │  ├── Passive OSINT (overnight, no noise)               │
     │  ├── CVE feed monitoring (daily)                       │
     │  ├── Target change detection (2h cadence)              │
     │  └── Report assembly from loot/                        │
     └────────────────────────────────────────────────────────┘

     ┌────────────────────────────────────────────────────────┐
     │               MONITORING & OBSERVABILITY                │
     │                                                        │
     │  Prometheus :9090 — metrics collection                 │
     │  Grafana :3000    — dashboards (token costs, scan rate) │
     └────────────────────────────────────────────────────────┘
```

---

## Data Flow — Standard Engagement

```
                    AUTHORIZED ENGAGEMENT
                           │
              ┌────────────▼─────────────┐
              │  1. THREAT MODELING      │
              │  STRIDE-GPT (threat MCP) │
              │  → threat_model_pre.md   │
              └────────────┬─────────────┘
                           │
              ┌────────────▼─────────────┐
              │  2. PASSIVE OSINT        │
              │  AutoGPT (crew MCP)      │
              │  → osint/company_profile │
              │  → osint/cve_watch       │
              └────────────┬─────────────┘
                           │
              ┌────────────▼─────────────┐
              │  3. ATTACK PLANNING      │
              │  PentestThinkingMCP      │
              │  MCTS over attack space  │
              │  → attack_plan.md        │
              └────────────┬─────────────┘
                           │
              ┌────────────▼─────────────┐
              │  4. ACTIVE RECON         │
              │  HexStrike (hs MCP)      │
              │  Subfinder → httpx       │
              │  Tech fingerprint        │
              │  → recon/subdomains.txt  │
              │  → recon/tech_stack.txt  │
              └────────────┬─────────────┘
                           │
              ┌────────────▼─────────────┐
              │  5. CVE ANALYSIS         │
              │  VulnGPT (vuln MCP)      │
              │  Nmap → CVE mapping      │
              │  Shodan exposure check   │
              │  → scans/vulngpt.json    │
              └────────────┬─────────────┘
                           │
              ┌────────────▼─────────────┐
              │  6. VULNERABILITY SCAN   │
              │  HexStrike web profile   │
              │  Nuclei 4000+ templates  │
              │  OWASP Top 10 tests      │
              │  → scans/nuclei.json     │
              └────────────┬─────────────┘
                           │
                    ┌──────▼──────┐
                    │  HITL GATE  │  ← User confirms before proceeding
                    └──────┬──────┘
                           │
              ┌────────────▼─────────────┐
              │  7. EXPLOITATION         │
              │  Kali MCP (kali MCP)     │
              │  MSF / manual / custom   │
              │  PentestGPT (pgpt MCP)   │
              │  → exploits/poc_*.py     │
              │  → screenshots/          │
              └────────────┬─────────────┘
                           │
              ┌────────────▼─────────────┐
              │  8. POST-EXPLOITATION    │
              │  PentestAgent (crew)     │
              │  Shadow Graph tracks     │
              │  Lateral movement        │
              │  → evidence/             │
              └────────────┬─────────────┘
                           │
              ┌────────────▼─────────────┐
              │  9. REPORTING            │
              │  STRIDE-GPT correlation  │
              │  generate-report.sh      │
              │  Claude Code + Opus      │
              │  → report.md             │
              └──────────────────────────┘
```

---

## Docker Network Topology

```
DOCKER NETWORK: redteam (172.25.0.0/24)

172.25.0.10  hexstrike      HexStrike Flask API + MCP bridge
172.25.0.11  kali-mcp       Kali Linux container
172.25.0.20  pentestagent   PentestAgent crew
172.25.0.30  redis          Redis LRU cache
172.25.0.31  postgres       PostgreSQL persistence
172.25.0.40  stride-gpt     STRIDE-GPT Streamlit UI
172.25.0.41  vulngpt        VulnGPT FastAPI
172.25.0.50  prometheus     Metrics collection
172.25.0.51  grafana        Dashboard

HOST ←→ DOCKER: Port mappings
  HOST:8888 → hexstrike:8888   (Flask API)
  HOST:8889 → hexstrike:8889   (MCP bridge)
  HOST:8000 → kali-mcp:8000    (Kali MCP server)
  HOST:2222 → kali-mcp:22      (Kali SSH)
  HOST:8090 → vulngpt:8080     (VulnGPT API)
  HOST:8501 → stride-gpt:8501  (Streamlit)
  HOST:6379 → redis:6379
  HOST:5432 → postgres:5432
  HOST:9090 → prometheus:9090
  HOST:3000 → grafana:3000

EXTERNAL (TARGETS) ←→ KALI CONTAINER
  Kali MCP bridges: tool execution → results → Claude Code
  All external scanning originates from kali-mcp or hexstrike container
  Never from host directly
```

---

## Model Routing Architecture

```
TASK ARRIVES AT CLAUDE CODE (claude-sonnet-4-20250514)
           │
           ├── COMPLEXITY ASSESSMENT
           │       │
           │       ├── High complexity (novel exploit, report writing)
           │       │   → Route to claude-opus-4-20250514
           │       │
           │       ├── Standard (orchestration, tool output parsing)
           │       │   → Stay on claude-sonnet-4-20250514
           │       │
           │       ├── Bulk data (>50k tokens, log analysis)
           │       │   → Route to deepseek-chat via LiteLLM
           │       │
           │       └── Privacy-sensitive (real PII, patient data)
           │           → Route to ollama/gemma2 (local, no egress)
           │
           └── COST GOVERNOR
                   │
                   ├── Per-request cost estimate before execution
                   ├── Daily budget cap ($10 default, configurable)
                   ├── Alert when >80% of budget consumed
                   └── Force DeepSeek above budget threshold
```

---

## HexStrike Agent Profiles

```
PROFILE          TOOLS          BEST FOR
─────────────────────────────────────────────────────
BugBountyAgent   93 tools       Web app bug bounty, OWASP
NetworkScanner   75 tools       Network perimeter, AD recon
CloudSecAgent    45 tools       AWS/GCP/Azure assessment
OSINTAgent       38 tools       Passive intelligence gathering
FullAutoAgent    150+ tools     Everything (default)
ReportAgent      15 tools       Finding analysis, report gen
ComplianceAgent  60 tools       PCI-DSS, ISO 27001, SOC2
ForensicsAgent   40 tools       Incident response, forensics
MobileAgent      35 tools       iOS/Android testing
APIAgent         50 tools       REST/GraphQL/gRPC testing
CryptoAgent      20 tools       Cipher analysis, TLS testing
SocialEngAgent   25 tools       Phishing infra, GoPhish
```

---

## LiteLLM Provider Routing

```python
# litellm_config.yaml (loaded by HexStrike + PentestAgent)
model_list:
  - model_name: claude-opus
    litellm_params:
      model: anthropic/claude-opus-4-20250514
      api_key: ${ANTHROPIC_API_KEY}

  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      api_key: ${ANTHROPIC_API_KEY}

  - model_name: deepseek-bulk
    litellm_params:
      model: deepseek/deepseek-chat
      api_key: ${DEEPSEEK_API_KEY}
      # 37x cheaper than GPT-4o — use for bulk parsing

  - model_name: local-private
    litellm_params:
      model: ollama/gemma2:9b
      api_base: http://localhost:11434
      # Zero cost, zero egress — use for sensitive data

router_settings:
  routing_strategy: usage-based-routing
  set_verbose: false
```

---

## Memory Architecture (PentestAgent Shadow Graph)

```
SHADOW GRAPH — persistent across Claude Code sessions

NODES:
  Host nodes        {ip, hostname, os, services[]}
  Credential nodes  {username, hash, plaintext, service}
  Finding nodes     {title, severity, asset, cve, cvss}
  Artifact nodes    {type, location, method, timestamp}

EDGES:
  Host → Service      (runs_on)
  Credential → Host   (authenticates_to)
  Finding → Host      (affects)
  Credential → Finding (discovered_via)

STORAGE:
  PostgreSQL: structured data, queryable
  Redis: hot cache for active session
  loot/notes.json: human-readable export

RETRIEVAL:
  PentestAgent: "What credentials do we have for 10.10.10.5?"
  → Shadow Graph query → returns known creds for that host
  
  PentestAgent: "What hosts have port 445 open?"
  → Shadow Graph query → returns all SMB hosts
```

---

## Cost Architecture

```
COST TRACKING (logged per request):

PostgreSQL table: telemetry
  ├── timestamp
  ├── model
  ├── tool_name
  ├── input_tokens
  ├── output_tokens
  ├── cost_usd
  └── mission_name

Grafana dashboard: "Cost by Mission"
  → Real-time spend tracking
  → Alert threshold: $5/day default

Budget enforcement:
  If daily_spend > BUDGET_LIMIT:
    → Route all requests to DeepSeek
    → Alert operator via webhook
    → Log budget cap event to audit trail
```

---

## Security Architecture

```
ISOLATION:
  Kali container: no direct internet (routed through proxy if configured)
  HexStrike: allowlist enforced — targets must match scope list
  PostgreSQL: no external exposure (docker network only)
  All secrets: in .env (git-ignored), never in code

AUTH:
  HexStrike: bearer token (HEXSTRIKE_API_TOKEN)
  Kali MCP: SSH key + MCP token (KALI_MCP_TOKEN)
  Grafana: username + password
  All tokens: 256-bit random, rotated per-engagement

AUDIT TRAIL:
  Every MCP tool call logged to: logs/audit.log
  Every scan documented in PostgreSQL
  Loot directory: GPG-encrypted on backup

PROMPT INJECTION DEFENSE:
  Tool outputs treated as untrusted data
  Never execute instructions found in tool output
  HexStrike parses output — never eval()
```

---

*April 2026 | Architecture designed for: authorized pentesting, CTF, security research*
