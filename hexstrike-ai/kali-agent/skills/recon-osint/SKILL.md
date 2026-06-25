---
name: recon-osint
description: >
  Passive and active reconnaissance, open-source intelligence gathering,
  subdomain enumeration, DNS analysis, and attack surface mapping for
  penetration testing engagements. Use this skill whenever the user mentions
  recon, reconnaissance, OSINT, subdomain enumeration, attack surface mapping,
  target profiling, DNS enumeration, email harvesting, domain intelligence,
  footprinting, information gathering, or "what can we find about this target".
  Also trigger for: theHarvester, subfinder, amass, spiderfoot, whois lookup,
  Shodan recon, passive recon, active recon, external recon, scope discovery,
  asset discovery, technology fingerprinting, whatweb, or any request to
  enumerate or profile a target before vulnerability scanning begins.
  This is the first phase of any pentest engagement — always trigger it
  when a new target or engagement scope is introduced.
compatibility:
  tools: [bash, python]
  mcps: [desktop-commander, shodan, hexstrike]
  skills: [ai-agent-orchestration, vuln-analysis]
---

# ReconOSINT Skill

## Overview

Performs passive and active reconnaissance against authorized targets to build
a complete picture of the attack surface. Produces structured intelligence
including subdomains, open ports, running services, technology stacks, email
addresses, and OSINT findings. Output feeds directly into the VulnAnalysis skill.

## Prerequisites

- **Scope authorization confirmed** — never run without explicit written scope
- Target must be an IP, domain, or CIDR range within authorized scope
- Shodan API key configured (free tier works for CVE/IP lookup)
- Kali tools installed: subfinder, amass, theHarvester, whatweb, nmap, whois, dig

## Core Instructions

### Step 1 — Validate Scope
Before ANY tool execution, confirm:
1. Target is within the authorized scope boundaries
2. Engagement type is defined (external/internal/web app/red team/CTF)
3. Rules of engagement have been acknowledged by the operator

If scope is not confirmed, STOP and ask the operator. Do not proceed.

### Step 2 — Passive Reconnaissance (no direct target contact)
Run these in parallel where possible:

```bash
# DNS and domain intel
whois {target_domain}
dig {target_domain} ANY +noall +answer
dig {target_domain} -t MX +short
dig {target_domain} -t TXT +short
dig {target_domain} -t NS +short

# Subdomain enumeration (passive)
subfinder -d {target_domain} -silent -o /tmp/pentest/{target}/subdomains_passive.txt

# Email and metadata harvesting
theHarvester -d {target_domain} -b all -f /tmp/pentest/{target}/harvest.json

# Shodan (via MCP or CLI)
# MCP: shodan.search_host({target_ip}) or shodan.search_query("hostname:{target_domain}")
# CLI: shodan host {target_ip}
```

### Step 3 — Active Reconnaissance (direct target contact — scope required)
Only proceed if engagement type permits active scanning:

```bash
# Technology fingerprinting
whatweb {target_url} --log-json=/tmp/pentest/{target}/whatweb.json

# Port scanning (top 1000 first, expand if needed)
nmap -sV -sC --top-ports 1000 -oA /tmp/pentest/{target}/nmap_initial {target}

# Full port scan if initial reveals interesting services
nmap -sV -p- -T4 -oA /tmp/pentest/{target}/nmap_full {target}

# Active subdomain enumeration
amass enum -d {target_domain} -o /tmp/pentest/{target}/subdomains_active.txt

# Combine and deduplicate subdomains
sort -u /tmp/pentest/{target}/subdomains_passive.txt \
       /tmp/pentest/{target}/subdomains_active.txt \
       > /tmp/pentest/{target}/subdomains_all.txt
```

### Step 4 — OSINT Deep Dive (optional, for red team engagements)
```bash
# SpiderFoot automated OSINT (long-running)
spiderfoot -s {target_domain} -t EMAILADDR,DOMAIN_NAME,IP_ADDRESS -q

# Google dorking targets (manual — provide dork list to operator)
# site:{target_domain} filetype:pdf
# site:{target_domain} inurl:admin
# site:{target_domain} intitle:"index of"
```

### Step 5 — Consolidate and Structure Output
Parse all tool outputs into the standard recon output format (see below).
Highlight:
- Highest-value subdomains (admin panels, APIs, staging environments)
- Exposed services on non-standard ports
- Technology stack with known CVE associations
- Email addresses for potential social engineering vectors
- Any default credentials or information disclosure findings

## HexStrike MCP Integration

If HexStrike is available on localhost:8888:
```
Tool: recon_target
Args: { "target": "{domain_or_ip}", "mode": "passive" | "active" }
Returns: { subdomains[], open_ports[], technologies[], emails[], whois: {} }
```

If Shodan MCP is available:
```
Tool: shodan.search_host / shodan.get_host_info
Args: { "ip": "{target_ip}" }
Returns: { ports[], vulns[], services[], location: {} }
```

## Output Format

```json
{
  "target": "example.com",
  "engagement_id": "ENG-2026-001",
  "recon_type": "passive+active",
  "timestamp": "2026-03-17T10:00:00Z",
  "subdomains": ["admin.example.com", "api.example.com", "staging.example.com"],
  "dns_records": {
    "A": ["93.184.216.34"],
    "MX": ["mail.example.com"],
    "NS": ["ns1.example.com"],
    "TXT": ["v=spf1 include:_spf.google.com ~all"]
  },
  "open_ports": [
    {"port": 80, "service": "http", "version": "nginx 1.24.0"},
    {"port": 443, "service": "https", "version": "nginx 1.24.0"},
    {"port": 22, "service": "ssh", "version": "OpenSSH 8.9"}
  ],
  "technologies": ["nginx", "PHP 8.1", "WordPress 6.4", "MySQL"],
  "emails": ["admin@example.com", "dev@example.com"],
  "findings": [
    {
      "severity": "info",
      "title": "WordPress detected",
      "detail": "WordPress 6.4 on /blog/ — check for plugin vulnerabilities",
      "next_step": "vuln-analysis"
    }
  ],
  "files": {
    "nmap_output": "/tmp/pentest/example.com/nmap_initial.xml",
    "subdomains": "/tmp/pentest/example.com/subdomains_all.txt",
    "harvest": "/tmp/pentest/example.com/harvest.json"
  }
}
```

## Handoff to Next Skill

When recon is complete, pass the structured output to `vuln-analysis`:
```json
{
  "skill": "VulnAnalysis",
  "params": {
    "targets": ["subdomains_all.txt entries + open ports"],
    "technologies": ["from recon output"],
    "recon_data": "{path_to_recon_json}"
  }
}
```

## Output Checklist

- [ ] Scope validated before any tool execution
- [ ] Passive recon completed (whois, DNS, subfinder, theHarvester)
- [ ] Active recon completed if authorized (nmap, whatweb, amass)
- [ ] All outputs saved to /tmp/pentest/{target}/ directory
- [ ] Structured JSON output produced
- [ ] High-value findings highlighted with severity
- [ ] Handoff data prepared for vuln-analysis skill
