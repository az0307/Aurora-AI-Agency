# CHANGELOG — April 2026 Red Team Stack

All notable changes to this stack documented here.
Format: [Version] — Date — Summary

---

## [v6.0] — 2026-04-22 — Complete Documentation Pass

**Added (this release):**
- `litellm_config.yaml` — provider-neutral routing, DeepSeek + Ollama + Groq
- `grafana/` — provisioning configs + 11-panel operations dashboard
- `kali-mcp/requirements.txt` — Python deps for MCP server
- `kali-mcp/TOOLS.md` — full tool inventory of Kali container
- `scripts/init-kali.sh` — post-build tool installation (linpeas, pspy64, etc.)
- `docs/faq.md` — 25 common questions with answers
- `docs/troubleshooting.md` — error → cause → fix for all components
- `docs/changelog.md` — this file
- `docs/model-routing.md` — expanded to full routing guide + cost math
- `docs/cost-optimization.md` — 6 strategies + per-engagement cost tables
- `skills/report-generator.md` — expanded to 4 workflows with exact prompts
- `.github/workflows/ci.yml` — expanded to 8-job pipeline
- `scripts/new-mission.sh` — upgraded with type routing, notes.json seed, audit log

**72 files / 533KB / 13,771+ lines**

---

## [v5.0] — 2026-04-22 — Infrastructure & Config Pass

**Added:**
- `litellm_config.yaml` (stub, expanded in v6)
- `docs/architecture.md` — ASCII system diagrams, data flow, network topology
- `docs/quick-reference.md` — field cheat sheet (hashcat, nmap, reverse shells)
- `docs/opsec.md` — full rewrite with shell=True patch, prompt injection defense
- `scripts/scope-validator.sh` — pre-scan authorization enforcement
- `loot/mission-template/` — pre-populated sample mission and findings
- `docker-compose.override.yml.example` — dev/debug mode
- `claude.json` — full rewrite with all 9 production MCP configs
- `.env.example` — 123-line full reference covering all variables

**65 files / 481KB**

---

## [v4.0] — 2026-04-22 — Full Playbook Coverage

**Added playbooks:**
- `mobile-pentest.md` — iOS/Android, MobSF, Frida, cert pinning bypass
- `cloud-gcp-azure.md` — GCP IAM privesc, Azure AD, ROADrecon
- `cicd-pipeline.md` — GitHub Actions injection, Jenkins RCE, supply chain
- `binary-re.md` — Ghidra, GDB/pwndbg, pwntools exploit development
- `social-engineering.md` — GoPhish, vishing, physical (authorization gate)
- `web3-blockchain.md` — Slither, Foundry fork testing, flash loan analysis

**Added skills:**
- `pentestgpt-solver.md` — CTF autopilot, XBOW benchmarks, hybrid mode
- `autogpt-monitor.md` — 6 monitoring workflows, DeepSeek cost config

**Added scripts:**
- `scripts/update.sh` — update all repos + packages + Nuclei templates
- `scripts/generate-report.sh` — auto-assemble report from loot/

**Added templates:**
- `.github/ISSUE_TEMPLATE.md` — 3 issue types
- `.github/PULL_REQUEST_TEMPLATE.md` — contributor checklist

**59 files / 436KB**

---

## [v3.0] — 2026-04-21 — Core Missing Files

**Added playbooks:**
- `autogpt-osint.md` — 6 OSINT task templates
- `threatgpt-stride.md` — 4-phase threat modeling lifecycle
- `defensive-threat-intel.md` — WormGPT BEC detection, AI recon signatures
- `wireless-rf.md` — WiFi/BLE/SDR/RFID, hashcat GPU optimization

**Added skills:**
- `vulngpt-analyzer.md` — nmap analysis, Shodan, CVE lookup
- `password-attacks.md` — hashcat, hydra, AD spray, PtH/PtT
- `threat-hunt.md` — Windows/Linux log hunting, IOC cross-reference

**Added infrastructure:**
- `Makefile` — single entry point for all operations
- `docs/wordlists-resources.md` — every wordlist + threat feed + exploit DB
- `docs/notion-integration.md` — 5 workflows for Az's Notion setup
- `loot/REPORT_TEMPLATE.md` — full professional pentest report
- `loot/README.md` — structure guide + security rules
- `scripts/backup.sh` — GPG AES256 encrypted archives
- `scripts/rotate-tokens.sh` — rotate all API tokens
- `CONTRIBUTING.md`

**47 files / 350KB**

---

## [v2.0] — 2026-04-20 — Docker + AI Tools Expansion

**Added playbooks:**
- `cloud-aws.md` — S3, IAM privesc 10 paths, Pacu, Secrets Manager
- `container-k8s.md` — Docker socket escape, K8s RBAC, etcd dump

**Added docs:**
- `docs/additional-ai-tools.md` — PentAGI, CAI, Basilisk, PyRIT, ARTEMIS, XBOW
- `docs/ai-tools-ecosystem.md` — OxTrace image tools detailed breakdown

**Updated:**
- `docker-compose.yml` — added stride-gpt and vulngpt services
- `README.md` — full rewrite with OxTrace image table

**35 files / 261KB**

---

## [v1.0] — 2026-04-19 — Initial Release

**Core files:**
- Root: `README.md`, `CLAUDE.md`, `claude.json`, `docker-compose.yml`,
  `.env.example`, `.gitignore`
- `docs/`: `cost-optimization.md`, `model-routing.md`, `opsec.md`,
  `prometheus.yml`
- `playbooks/`: `web-app-full.md`, `network-pentest.md`, `ad-attack.md`,
  `bug-bounty.md`, `ctf-htb.md`, `pentestgpt-integration.md`
- `skills/`: `hexstrike-recon.md`, `kali-exploitation.md`, `report-generator.md`
- `kali-mcp/`: `Dockerfile`, `entrypoint.sh`, `mcp_server.py`
- `scripts/`: `install.sh`, `install-extended.sh`, `healthcheck.sh`,
  `new-mission.sh`, `init.sql`
- `.github/workflows/ci.yml`

**29 files**

---

## Versioning Convention

- Major version: significant new capability (new tool category, new domain)
- Minor version: new files within existing categories
- Patch: fixes, updates, expansions of existing files

---

*April 2026 | Track changes for auditability and reproducibility*
