---
name: vuln-analysis
description: >
  Vulnerability scanning, CVE analysis, exploit mapping, and finding triage
  for penetration testing engagements. Use this skill whenever the user mentions
  vulnerability scanning, vuln scan, CVE lookup, Nuclei scan, Nikto scan,
  web application testing, SQL injection testing, XSS testing, security
  assessment, OWASP testing, vulnerability assessment, security audit,
  finding triage, CVE analysis, CVSS scoring, exploit availability check,
  or any request to identify vulnerabilities in a target system or application.
  Also trigger for: sqlmap, wpscan, nikto, nuclei, nessus, openvas, ffuf,
  directory brute force for vulns, CMS vulnerability scanning, API security
  testing, SSL/TLS analysis, or "scan this for vulnerabilities".
  This is the second phase of a pentest — trigger after recon-osint completes,
  or standalone when the user already knows what to scan.
compatibility:
  tools: [bash, python]
  mcps: [desktop-commander, shodan, hexstrike]
  skills: [recon-osint, exploit-dev, ai-agent-orchestration]
---

# VulnAnalysis Skill

## Overview

Executes vulnerability scanning against authorized targets using multiple tools
and techniques. Correlates findings with CVE databases, assesses exploitability,
and produces a prioritized list of vulnerabilities with CVSS scores and exploit
availability. Output feeds into the ExploitDev skill for confirmed exploitation.

## Prerequisites

- **Scope authorization confirmed** — active scanning touches the target
- Recon data available (from recon-osint or operator-provided target list)
- Kali tools installed: nuclei, nikto, sqlmap, wpscan, ffuf, nmap NSE scripts
- Nuclei templates updated: `nuclei -update-templates`

## Core Instructions

### Step 1 — Ingest Recon Data
Accept input from recon-osint output or operator:
- Target URLs/IPs to scan
- Identified technologies (WordPress, nginx version, etc.)
- Open ports and services
- Subdomains list

### Step 2 — Automated Vulnerability Scanning

**Template-based scanning (broad coverage):**
```bash
# Nuclei — CVEs, exposures, misconfigs, default creds
nuclei -l /tmp/pentest/{target}/subdomains_all.txt \
  -t cves/ -t exposures/ -t misconfiguration/ -t default-logins/ \
  -severity critical,high,medium \
  -o /tmp/pentest/{target}/nuclei_results.txt \
  -json -o /tmp/pentest/{target}/nuclei_results.json

# Nikto — web server vulnerabilities
nikto -h {target_url} -output /tmp/pentest/{target}/nikto_results.txt -Format txt
```

**Technology-specific scanning:**
```bash
# WordPress (if detected in recon)
wpscan --url {target_url} --enumerate vp,vt,u \
  --output /tmp/pentest/{target}/wpscan.json --format json

# SSL/TLS analysis
nmap --script ssl-enum-ciphers -p 443 {target} \
  -oN /tmp/pentest/{target}/ssl_audit.txt

# HTTP security headers
nmap --script http-security-headers -p 80,443 {target}
```

**Web application testing:**
```bash
# Directory and file discovery
ffuf -u {target_url}/FUZZ -w /usr/share/wordlists/dirb/common.txt \
  -mc 200,301,302,403 -o /tmp/pentest/{target}/ffuf_dirs.json -of json

# SQL injection detection (GET params)
sqlmap -u "{target_url_with_params}" --batch --level 3 --risk 2 \
  --output-dir=/tmp/pentest/{target}/sqlmap/

# XSS detection via Nuclei
nuclei -u {target_url} -t xss/ -o /tmp/pentest/{target}/xss_results.txt
```

### Step 3 — CVE Correlation and Enrichment

For each identified vulnerability:
1. Look up CVE ID in Shodan (via MCP: `shodan.get_cve({cve_id})`)
2. Check EPSS score (Exploit Prediction Scoring System)
3. Check KEV list (Known Exploited Vulnerabilities — CISA)
4. Search ExploitDB: `searchsploit {product} {version} --json`
5. Assess CVSS base score and environmental adjustments

### Step 4 — Finding Triage and Prioritization

Classify each finding:

| Priority | Criteria |
|----------|----------|
| P0 — Critical | CVSS ≥ 9.0 OR on KEV list OR active exploit in wild |
| P1 — High | CVSS 7.0–8.9 AND public exploit available |
| P2 — Medium | CVSS 4.0–6.9 OR no public exploit but high impact |
| P3 — Low | CVSS < 4.0, informational, or hardening recommendations |

For each P0/P1 finding, prepare exploitation parameters for exploit-dev skill.

### Step 5 — False Positive Validation
For high-severity findings, attempt manual validation:
```bash
# Verify SQL injection
sqlmap -u "{confirmed_url}" --batch --technique=BEUSTQ --threads 5

# Verify command injection
# Provide operator with manual test payload — DO NOT auto-execute RCE

# Verify authentication bypass
curl -v {target_url}/admin -H "Authorization: Bearer test"
```

Flag any finding that cannot be manually validated as "Unconfirmed".

## HexStrike MCP Integration

```
Tool: vuln_scan
Args: { "target": "{url}", "templates": "cves,exposures,misconfiguration" }
Returns: { findings: [{ cve, severity, title, matched_at, template }] }

Tool: port_scan
Args: { "target": "{ip}", "flags": "--script vuln -sV" }
Returns: { output: "nmap NSE script results" }
```

## Output Format

```json
{
  "target": "example.com",
  "engagement_id": "ENG-2026-001",
  "scan_timestamp": "2026-03-17T12:00:00Z",
  "tools_used": ["nuclei", "nikto", "wpscan", "sqlmap", "ffuf"],
  "summary": {
    "critical": 1,
    "high": 3,
    "medium": 7,
    "low": 12,
    "info": 5
  },
  "findings": [
    {
      "id": "VULN-001",
      "severity": "critical",
      "cvss": 9.8,
      "cve": "CVE-2024-XXXXX",
      "title": "Remote Code Execution in WordPress Plugin X",
      "affected_asset": "blog.example.com",
      "description": "Unauthenticated RCE via file upload in plugin X v2.1",
      "evidence": "Nuclei template match + sqlmap confirmation",
      "epss_score": 0.87,
      "on_kev": true,
      "exploit_available": true,
      "exploit_ref": "EDB-12345",
      "remediation": "Update plugin X to version 2.3 or remove",
      "status": "confirmed",
      "next_step": "exploit-dev"
    }
  ],
  "files": {
    "nuclei_json": "/tmp/pentest/example.com/nuclei_results.json",
    "nikto": "/tmp/pentest/example.com/nikto_results.txt",
    "wpscan": "/tmp/pentest/example.com/wpscan.json",
    "sqlmap": "/tmp/pentest/example.com/sqlmap/"
  }
}
```

## Handoff to Next Skill

For confirmed P0/P1 findings, pass to `exploit-dev`:
```json
{
  "skill": "ExploitDev",
  "params": {
    "finding_id": "VULN-001",
    "cve": "CVE-2024-XXXXX",
    "target": "blog.example.com",
    "exploit_ref": "EDB-12345",
    "vuln_data": "{path_to_vuln_json}"
  }
}
```

## Output Checklist

- [ ] All scan tools executed against authorized targets only
- [ ] Nuclei templates up to date before scanning
- [ ] CVE correlation completed (EPSS, KEV, ExploitDB)
- [ ] Findings triaged by priority (P0–P3)
- [ ] False positives flagged or validated
- [ ] Structured JSON output produced with evidence
- [ ] Remediation guidance included per finding
- [ ] Handoff data prepared for exploit-dev skill
