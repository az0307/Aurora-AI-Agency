# SKILL: autogpt-monitor
# Continuous background monitoring and intelligence gathering
# Triggered when: "monitor", "watch", "alert me when", "continuous"

## Trigger Phrases
- "monitor [target] continuously"
- "watch for changes on [domain]"
- "alert me when [condition]"
- "set up AutoGPT monitoring for [target]"
- "track CVEs for [tech stack]"
- "keep watching [target]"

## Overview

AutoGPT monitoring runs as a background daemon.
It handles the long-running, repetitive intelligence tasks while
HexStrike + Kali MCP handle active testing.

Think of it as: AutoGPT = always-on radar, everything else = weapons.

---

## WORKFLOW A — Target Change Detection

```bash
# Start continuous monitoring daemon
kali_exec("cd autogpt && docker compose up -d autogpt")

# Configure monitoring task
agpt_task = """
Monitor [TARGET_DOMAIN] for any changes. Check every 2 hours.

Monitors:
1. New subdomains (crt.sh + SecurityTrails delta)
2. New open ports or services (Shodan API changes)
3. New GitHub repos from [COMPANY]
4. New job postings mentioning infrastructure/security
5. New CVEs affecting confirmed tech stack: [TECH_LIST]
6. HaveIBeenPwned: new breach data for [DOMAIN]

Alert threshold: Any new finding → immediately log to:
  loot/[MISSION]/monitoring/alerts.md

Format each alert:
[TIMESTAMP] [TYPE] [DESCRIPTION] [SEVERITY]

Run continuously until stopped.
"""

kali_exec(f"agpt run --continuous --task '{agpt_task}' --log loot/[MISSION]/monitoring/autogpt.log &")
echo "AutoGPT monitoring started in background"
```

---

## WORKFLOW B — CVE Watch for Client Tech Stack

After engagement, leave monitoring running for client:

```bash
# Ongoing CVE monitoring for client infrastructure
kali_exec("agpt run --continuous --task \"\
Monitor CVE feeds for vulnerabilities affecting this tech stack:\
Frontend: React 18.x, Nginx 1.24\
Backend: Node.js 20.x, Express 4.x\
Database: PostgreSQL 15, Redis 7\
Auth: jsonwebtoken, Passport.js\
Cloud: AWS (EC2, RDS, S3, CloudFront, Lambda)\
\
Sources: NVD, CISA KEV, GitHub Security Advisories, Snyk\
\
Alert immediately if:\
- CVSS >= 8.0\
- Affects a confirmed version above\
- PoC publicly available\
- In CISA KEV (actively exploited in wild)\
\
Log all findings to /shared/cve_watch.md\
Send summary every 24 hours to /shared/daily_brief.md\
\" &")
```

---

## WORKFLOW C — Bug Bounty Opportunity Monitor

For ongoing bug bounty programs:

```bash
# Monitor program changes + scope expansions
kali_exec("agpt run --continuous --task \"\
Monitor bug bounty program for [COMPANY] on HackerOne and Bugcrowd.\
\
Track:\
1. Scope changes (new domains/assets added)\
2. Bounty payout changes (increased rewards)\
3. Program statistics (acceptance rate, avg bounty)\
4. Recent disclosed reports (find patterns in what they pay for)\
\
Alert when: new scope added → immediately create brief on how to approach new target\
\
Frequency: Check every 6 hours\
Output: loot/bugbounty/[COMPANY]/opportunities.md\
\" &")
```

---

## WORKFLOW D — Credential Breach Monitoring

Watch for compromised credentials relevant to target:

```bash
# Monitor breach databases for target email domain
kali_exec("agpt run --continuous --task \"\
Monitor breach intelligence for email domain: [TARGET_DOMAIN]\
\
Sources:\
- HaveIBeenPwned API (check for new breaches)\
- DeHashed API (search for @[TARGET_DOMAIN] in breached data)\
- WeLeakInfo (monitor for new dumps)\
- Telegram channels (security researchers post new leaks)\
\
Alert criteria:\
- Any new breach containing [TARGET_DOMAIN] emails\
- Any newly posted credentials matching @[TARGET_DOMAIN]\
- Executive email addresses found in breach data\
\
Output: loot/[MISSION]/monitoring/credential_alerts.md\
Format: email | breach_source | breach_date | data_exposed\
\" &")
```

---

## WORKFLOW E — Dark Web Mention Monitoring

For clients who need threat intelligence:

```bash
# Monitor public dark web-adjacent intelligence (Tor indices, paste sites)
kali_exec("agpt run --continuous --task \"\
Monitor threat intelligence sources for mentions of [COMPANY_NAME] or [DOMAIN].\
PASSIVE OSINT ONLY — no active dark web access.\
\
Sources to check:\
- IntelX.io (paste sites, dark web indexed content — public API)\
- BreachForums mentions (indexed by search engines)\
- Paste sites: pastebin.com, rentry.co (public)\
- GitHub: any new repos mentioning [COMPANY] + breach/dump/leak\
- Twitter/X: mentions of [COMPANY] + data/breach/leaked\
\
Alert if: any mention of company + data/credentials/breach\
Priority: HIGH if appears to be real data, MEDIUM if speculation\
\
Output: loot/[MISSION]/monitoring/darkweb_intel.md\
\" &")
```

---

## WORKFLOW F — Reconnaissance Delta

Run periodic recon and compare against baseline:

```python
# Compare current attack surface to baseline
import subprocess, json, datetime

def run_recon_delta(target, mission, baseline_file):
    """Run recon and compare to previous results — flag changes"""
    
    # Current scan
    current = {
        "timestamp": datetime.datetime.now().isoformat(),
        "subdomains": run_subfinder(target),
        "open_ports": run_nmap_quick(target),
        "tech_stack": run_httpx_tech(target),
    }
    
    # Load baseline
    try:
        with open(baseline_file) as f:
            baseline = json.load(f)
    except FileNotFoundError:
        # First run — save as baseline
        with open(baseline_file, 'w') as f:
            json.dump(current, f, indent=2)
        return "Baseline established"
    
    # Delta detection
    new_subdomains = set(current["subdomains"]) - set(baseline["subdomains"])
    new_ports = set(current["open_ports"]) - set(baseline["open_ports"])
    
    if new_subdomains or new_ports:
        alert = f"\n## CHANGE DETECTED — {current['timestamp']}\n"
        if new_subdomains:
            alert += f"NEW SUBDOMAINS: {', '.join(new_subdomains)}\n"
        if new_ports:
            alert += f"NEW OPEN PORTS: {', '.join(str(p) for p in new_ports)}\n"
        
        with open(f"loot/{mission}/monitoring/changes.md", 'a') as f:
            f.write(alert)
        
        return alert
    
    return "No changes detected"
```

---

## Monitoring Dashboard (via AutoGPT)

```bash
# Generate daily monitoring summary
kali_exec("agpt run --task \"\
Read all files in loot/[MISSION]/monitoring/.\
Generate a monitoring summary dashboard:\
\
# MONITORING SUMMARY — $(date +%Y-%m-%d)\
\
## New Findings (last 24h)\
[List any alerts from alerts.md]\
\
## CVE Watch\
[List any new CVEs from cve_watch.md]\
\
## Attack Surface Changes\
[Any new subdomains, ports, services]\
\
## Threat Intelligence\
[Any dark web or credential mentions]\
\
## Status\
Monitors active: [LIST]\
Last check: [TIMESTAMP]\
Next check: [TIMESTAMP]\
\
Save to loot/[MISSION]/monitoring/dashboard_$(date +%Y%m%d).md\
\"")
```

---

## Management Commands

```bash
# List active AutoGPT monitoring jobs
kali_exec("ps aux | grep autogpt")
kali_exec("docker exec autogpt_container agpt status")

# Stop a specific monitor
kali_exec("kill [PID]")
kali_exec("docker exec autogpt_container agpt stop [JOB_ID]")

# View monitoring log
kali_exec("tail -f loot/[MISSION]/monitoring/autogpt.log")
kali_exec("tail -f loot/[MISSION]/monitoring/alerts.md")

# Stop ALL monitoring (end of engagement)
kali_exec("pkill -f autogpt")
kali_exec("docker compose stop autogpt")
```

---

## Cost Notes

AutoGPT monitoring with various models:
- DeepSeek backend: ~$0.20-0.80/day (37x cheaper than GPT-4o)
- GPT-4o Mini: ~$0.50-2.00/day
- Claude Sonnet: ~$1.00-4.00/day

Configure model in `.env`:
```bash
AUTOGPT_LLM_PROVIDER=deepseek
AUTOGPT_FAST_LLM=deepseek-chat
AUTOGPT_SMART_LLM=deepseek-chat
```

For cost-effective 24/7 monitoring, use DeepSeek.
For high-stakes targets (bug bounty with big payouts), use Sonnet.
