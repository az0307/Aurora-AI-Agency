# 🔴 APRIL 2026 BEST-COMBO RED TEAM STACK

**69 files · 14,000+ lines · 9 AI systems · 18 playbooks · 8 skills**
Built by [@0x4m4](https://github.com/0x4m4) — April 2026

---

## 9-Tool AI Arsenal

```
Claude Code (Opus/Sonnet) — Orchestrator Brain
     │
     ├── HexStrike AI v6.0  (:8888/:8889)    [Kali official: apt install hexstrike-ai]
     │   150+ tools · 12 agents · Nuclei 4000+ templates
     │
     ├── PentestGPT          (docker)         [USENIX Security 2024]
     │   86.5% XBOW success rate · Task tree reasoning · Autonomous CTF
     │
     ├── Kali MCP            (:8000)          [Kali 2025.3 official]
     │   Live Kali SSH+PTY+tmux · nmap/msfconsole/sqlmap/hydra
     │
     ├── PentestThinkingMCP  (:8890)          [MCTS + Beam Search]
     │   Attack path planning · 2x HTB/CTF speed
     │
     ├── PentestAgent        (crew mode)      [Shadow Graph memory]
     │   Multi-agent crew · RAG · Cross-session loot persistence
     │
     ├── VulnGPT             (:8090)          [CVE intelligence]
     │   Nmap analysis · Shodan exposure · NVD queries
     │
     ├── STRIDE-GPT          (:8501)          [AI threat modeling]
     │   Pre/post engagement STRIDE analysis · Client deliverables
     │
     └── AutoGPT             (background)     [170k stars — OSINT]
           Passive recon · Continuous monitoring · CVE watch
```

---

## Quick Start

```bash
git clone https://github.com/0x4m4/april-redteam-2026
cd april-redteam-2026
cp .env.example .env && $EDITOR .env

make install-all    # Installs everything
make start          # Start 9 Docker services
make health         # Verify all services up

claude --dangerously-skip-permissions  # Launch Claude Code

# New engagement:
make new-mission NAME=client TARGET=target.com TYPE=web
```

**Kali native (no Docker needed for HexStrike):**
```bash
sudo apt install hexstrike-ai    # Kali 2025.4+
make install-all                 # Gets PentestGPT, VulnGPT, STRIDE-GPT, AutoGPT
```

---

## AI Tools from "Best AI Tools Used By Hackers" Image

| Tool | Status | Role |
|------|--------|------|
| **WormGPT** | ✗ Threat intel only | Dark web BEC tool → defensive brief only |
| **PentestGPT** | ✓ Integrated | Autonomous agent, 86.5% XBOW, CTF autopilot |
| **ChaosGPT** | ✗ Documented | Adversarial experiment → informs HITL design |
| **AutoGPT** | ✓ Integrated | OSINT, monitoring, background intelligence |
| **VulnGPT** | ✓ Integrated | CVE analysis, Shodan exposure, NVD queries |
| **ThreatGPT** | ✓ Integrated | STRIDE-GPT threat modeling, client deliverables |

*See docs/ai-tools-ecosystem.md and docs/additional-ai-tools.md for 20+ tools total.*

---

## 18 Playbooks — Full Coverage

```
DOMAIN                  PLAYBOOK FILE
────────────────────────────────────────────────────────────
Web application         playbooks/web-app-full.md
Network perimeter       playbooks/network-pentest.md
Active Directory        playbooks/ad-attack.md
Bug bounty              playbooks/bug-bounty.md
CTF / HackTheBox        playbooks/ctf-htb.md
Mobile (iOS/Android)    playbooks/mobile-pentest.md
Cloud — AWS             playbooks/cloud-aws.md
Cloud — GCP/Azure       playbooks/cloud-gcp-azure.md
Container/Kubernetes    playbooks/container-k8s.md
CI/CD pipeline          playbooks/cicd-pipeline.md
Wireless/RF/BLE         playbooks/wireless-rf.md
Social engineering      playbooks/social-engineering.md
Binary RE + pwn         playbooks/binary-re.md
Web3/blockchain         playbooks/web3-blockchain.md
OSINT + intelligence    playbooks/autogpt-osint.md
Threat modeling         playbooks/threatgpt-stride.md
Defensive intel brief   playbooks/defensive-threat-intel.md
PentestGPT patterns     playbooks/pentestgpt-integration.md
```

---

## 8 Claude Code Skills

```
TRIGGER                         SKILL FILE
────────────────────────────────────────────────────────────
"scan", "recon", "enumerate"    skills/hexstrike-recon.md
"exploit", "get shell"          skills/kali-exploitation.md
"CVE analysis", "Shodan"        skills/vulngpt-analyzer.md
"crack", "brute force", "spray" skills/password-attacks.md
"generate report", "write up"   skills/report-generator.md
"CTF autopilot", "solve"        skills/pentestgpt-solver.md
"monitor", "watch", "alert"     skills/autogpt-monitor.md
"hunt", "IOC", "threat hunt"    skills/threat-hunt.md
```

---

## File Structure (69 files)

```
april-redteam-2026/
├── README.md              CLAUDE.md              CONTRIBUTING.md
├── Makefile               claude.json            docker-compose.yml
├── docker-compose.override.yml.example           .env.example
│
├── docs/
│   ├── architecture.md         quick-reference.md      opsec.md
│   ├── ai-tools-ecosystem.md   additional-ai-tools.md  notion-integration.md
│   ├── cost-optimization.md    model-routing.md        wordlists-resources.md
│   └── prometheus.yml
│
├── playbooks/ (18 files)       skills/ (8 files)
├── scripts/ (9 files)          kali-mcp/ (3 files)
├── loot/ (5 files)             .github/ (3 files)
```

---

## Make Commands

```
make start              Start all 9 Docker services
make stop/restart       Manage services
make health             Check all services
make kali-shell         Interactive Kali shell

make new-mission        NAME= TARGET= TYPE=
make report             MISSION=
make ctf                IP= NAME=
make osint              TARGET= MISSION=

make backup             MISSION= (GPG AES256 encrypted)
make rotate-tokens      Rotate all API tokens + passwords
make update             Pull latest for all repos + packages
make clean-loot         MISSION= (secure shred)
```

---

## Cost Reference

| Engagement | Est. LLM Cost |
|-----------|---------------|
| CTF machine | $0.50–$5 |
| Bug bounty session | $2–$8 |
| Web app pentest | $5–$15 |
| Network pentest | $15–$40 |
| Red team week | $40–$100 |

HexStrike Redis caching reduces repeat scan cost to near-zero.

---

## Legal

For authorized penetration testing and security research only.
All targets must be owned or have explicit written authorization.

---

*April 2026 · 0x4m4/april-redteam-2026*
*HexStrike AI: `sudo apt install hexstrike-ai` on Kali Linux 2025.4+*
