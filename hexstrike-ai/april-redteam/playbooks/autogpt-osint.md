# PLAYBOOK: AutoGPT — OSINT & Intelligence Automation
# April 2026 Red Team Stack
# Role: Background intelligence, passive recon, monitoring loops
# NOT for active scanning — use HexStrike + Kali MCP for that

---

## AutoGPT's Role in This Stack

```
┌─────────────────────────────────────────────────────────┐
│  AUTOGPT HANDLES                                         │
│                                                          │
│  ◉ Passive OSINT (runs overnight, no noise)             │
│  ◉ Continuous monitoring (24/7 threat feed watching)    │
│  ◉ Intelligence aggregation (LinkedIn, GitHub, Shodan)  │
│  ◉ Report drafting from structured findings             │
│  ◉ Cross-referencing threat databases                   │
│                                                          │
│  LEAVE TO HEXSTRIKE / KALI                              │
│                                                          │
│  ✗ Active port scanning                                 │
│  ✗ Vulnerability scanning                               │
│  ✗ Exploitation / shells                                │
└─────────────────────────────────────────────────────────┘
```

---

## Setup

```bash
cd autogpt

# Docker method (recommended)
cp .env.template .env
# Set: OPENAI_API_KEY or ANTHROPIC_API_KEY
docker compose up -d
# Web UI at http://localhost:8000

# CLI method
pip install agpt
agpt run
```

---

## TASK 1 — Full Company OSINT Profile

**Use before any engagement to build target intelligence.**

```yaml
# autogpt_task.yaml
ai_name: OSINT_Analyst
ai_role: >
  You are a passive OSINT intelligence analyst.
  Collect and correlate public information about target companies.
  Do NOT access any systems directly. Passive sources only.

goals:
  - "Search LinkedIn for employees of [COMPANY_NAME]. Find: names, titles, emails format, tech stack mentions."
  - "Search GitHub for repositories from [COMPANY_NAME] or [COMPANY_DOMAIN]. Note: languages, frameworks, exposed configs."
  - "Query Shodan API for [COMPANY_DOMAIN] and IP ranges. Find: open ports, exposed services, geolocation."
  - "Search job postings on LinkedIn/Indeed for [COMPANY_NAME]. Extract: tech stack, security tools, cloud providers."
  - "Find all subdomains via crt.sh, SecurityTrails, and DNS dumpster for [COMPANY_DOMAIN]."
  - "Compile all findings into structured markdown report. Save to loot/[MISSION]/osint/company_profile.md"
```

**Manual trigger via CLI:**
```bash
agpt run --task "
Company OSINT on [COMPANY_NAME] ([COMPANY_DOMAIN]).
Passive sources only. Collect:
1. Employee names/roles/emails via LinkedIn
2. GitHub repos + code for [COMPANY_NAME]
3. Shodan exposure for [COMPANY_DOMAIN]
4. Job postings revealing tech stack
5. Subdomain enumeration via crt.sh
Save report to: loot/[MISSION]/osint/company_profile.md
"
```

**Expected output:**
```
loot/[MISSION]/osint/
├── company_profile.md        # Full OSINT summary
├── employees.csv             # Name, title, LinkedIn URL
├── github_repos.txt          # Repos + interesting findings
├── shodan_exposure.json      # Open ports / services
├── tech_stack.md             # Inferred from jobs + code
└── subdomains_passive.txt    # crt.sh + SecurityTrails results
```

---

## TASK 2 — Continuous Target Monitoring

**Run as background daemon — alerts when target changes.**

```bash
agpt run --continuous --task "
Monitor [TARGET_DOMAIN] for changes every 4 hours.
Check:
1. New subdomains appearing (crt.sh)
2. New GitHub repos or commits from [COMPANY]
3. New job postings mentioning security/infrastructure
4. HaveIBeenPwned: any new breach data for [COMPANY_DOMAIN]
5. Shodan: any newly exposed ports or services

Alert if: anything new found. Append to loot/[MISSION]/osint/changes_log.md
Run until stopped.
"
```

**Alert conditions to configure:**
- New subdomain appears → could be new attack surface
- New exposed port on Shodan → potential new entry point
- Breach data found → credential stuffing opportunity
- New engineer hire in security → suggests upcoming changes
- New cloud infrastructure job → AWS/GCP/Azure migration likely

---

## TASK 3 — GitHub Secret Hunting

**Find exposed credentials and configs in public repos.**

```bash
agpt run --task "
Search GitHub for exposed secrets from [COMPANY_NAME] / [COMPANY_DOMAIN].

Search for:
1. Files: .env, config.yml, application.properties, docker-compose.yml
2. Terms: [COMPANY_DOMAIN] password, [COMPANY_DOMAIN] api_key, [COMPANY_DOMAIN] secret
3. AWS keys: AKIA in repos mentioning [COMPANY_NAME]
4. Private keys: 'BEGIN RSA PRIVATE KEY' in [COMPANY] repos
5. Database strings: postgresql://, mongodb:// in [COMPANY] code
6. Slack webhooks: hooks.slack.com in [COMPANY] repos
7. Hardcoded IPs: internal IP ranges [10., 172., 192.168.] in public repos

For each finding: note repo URL, file path, line number, date committed.
Save to loot/[MISSION]/osint/github_secrets.md — mark severity (Critical/High/Medium).
DO NOT CLONE or store actual secret values — document existence only.
"
```

**High-value GitHub dork patterns:**
```
# Use GitHub search API (rate limited — 30 searches/min authenticated)
org:[COMPANY] filename:.env
org:[COMPANY] api_key
org:[COMPANY] "-----BEGIN"
org:[COMPANY] password NOT test NOT example
user:[DEVELOPER_NAME] filename:.env
```

---

## TASK 4 — Social Engineering Intelligence

**Build target dossier for phishing simulation / social engineering tests.**

```bash
agpt run --task "
Build social engineering intelligence profile for [COMPANY_NAME].
Authorized red team — social engineering phase.

Collect:
1. Key decision makers: CEO, CTO, CFO, CISO — names, LinkedIn, public email format
2. Email format: determine [first.last]@[domain] vs [flast]@[domain] etc.
3. Recent company announcements: mergers, layoffs, new products (pretext material)
4. Vendors and partners mentioned publicly (third-party pretext)
5. Internal tools visible in job posts: Slack, Jira, Confluence, Salesforce
6. Company events, conferences, trade shows mentioned

Save profile to loot/[MISSION]/osint/social_eng_profile.md
Include: suggested pretexts based on public info.
"
```

---

## TASK 5 — CVE Intelligence Monitoring

**Stay current on vulnerabilities affecting discovered tech stack.**

```bash
agpt run --continuous --task "
Monitor CVE feeds for vulnerabilities affecting:
Tech stack: [TECH_STACK from company_profile.md]

Sources to check daily:
- NVD (nvd.nist.gov/feeds)
- CISA KEV (cisa.gov/known-exploited-vulnerabilities-catalog)
- Exploit-DB new entries
- GitHub Security Advisories
- Vendor security bulletins for: [VENDORS]

Alert criteria:
- CVSS >= 8.0
- PoC exploit available
- Affects confirmed version in use by target

Log to loot/[MISSION]/osint/cve_watch.md — include: CVE, CVSS, affected version, PoC available (Y/N)
"
```

---

## TASK 6 — Post-Engagement Intelligence Report

**AutoGPT assembles final intelligence brief from all loot.**

```bash
agpt run --task "
Read all files in loot/[MISSION]/osint/.
Synthesize into an Intelligence Brief document.

Structure:
1. Executive Summary (200 words — business risk language)
2. Attack Surface Map (all discovered subdomains, exposed services)
3. Employee Intelligence (org chart, key targets for social eng)
4. Technology Exposure (stack, versions, cloud providers)
5. Historical Exposure (breaches, leaked data, old CVEs)
6. Recommended Attack Vectors (top 5 based on OSINT only)
7. Blind Spots (what we couldn't find — gaps in intelligence)

Save to loot/[MISSION]/INTELLIGENCE_BRIEF.md
Format: professional, client-deliverable quality.
"
```

---

## Integration with Red Team Stack

```
WORKFLOW: Intelligence-Led Penetration Test

1. AutoGPT OSINT (overnight)
   → company_profile.md, tech_stack.md, subdomains_passive.txt

2. PentestThinkingMCP (attack planning using OSINT)
   → plan_attack_path(context=company_profile.md)

3. HexStrike active recon (informed by OSINT)
   → target known subdomains, confirmed tech stack

4. PentestGPT / Kali MCP (exploitation)
   → use OSINT-derived pretexts, known tech stack

5. AutoGPT report assembly (post-engagement)
   → compile all loot into intelligence brief
```

---

## Cost Notes

AutoGPT with Claude Sonnet costs roughly:
- Single OSINT run (1-3 hours): ~$0.50-2.00
- Continuous monitoring (24h): ~$3-8/day
- GitHub secret hunting: ~$1-3 per company

Use DeepSeek API as backend for cost reduction (~37x cheaper):
```bash
# In .env
OPENAI_API_KEY=your-deepseek-key
OPENAI_API_BASE=https://api.deepseek.com/v1
SMART_LLM_MODEL=deepseek-chat
FAST_LLM_MODEL=deepseek-chat
```

---

*April 2026 | Passive OSINT only — never touch systems directly via AutoGPT*
