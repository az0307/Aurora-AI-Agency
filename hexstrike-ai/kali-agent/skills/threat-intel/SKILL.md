---
name: threat-intel
description: >
  Threat intelligence gathering, CVE enrichment, indicator of compromise (IOC)
  analysis, and attack surface intelligence for security engagements. Use this
  skill whenever the user mentions threat intelligence, threat intel, CVE
  lookup, CVE enrichment, EPSS score, KEV list, CISA KEV, exploit prediction,
  IOC analysis, indicator of compromise, threat actor profiling, malware
  intelligence, MITRE ATT&CK mapping, VirusTotal lookup, Shodan intel, attack
  surface monitoring, vulnerability intelligence, or "what's known about this CVE".
  Also trigger for: NVD lookup, ExploitDB search, Shodan CVE query, CVSS analysis,
  vulnerability prioritization, threat landscape assessment, "is there an exploit
  for this", "how critical is this CVE", "what's the EPSS score", or any request
  to enrich security findings with external intelligence.
  Expert sources: Shodan CVEDB (MCP), NVD/NIST, ExploitDB (searchsploit),
  CISA KEV, EPSS, MITRE ATT&CK, VirusTotal (MCP available).
compatibility:
  tools: [bash, python]
  mcps: [shodan, desktop-commander]
  skills: [vuln-analysis, recon-osint, red-team-report]
---

# Threat Intelligence Skill

## Overview

Enriches security findings with external threat intelligence: CVE details,
exploit availability, EPSS scores, KEV status, MITRE ATT&CK mappings, and
threat actor context. Transforms raw vulnerability data into prioritized,
actionable intelligence for decision-making and reporting.

## Expert Source Hierarchy

| Intelligence Need | Best Source | Access Method |
|-------------------|------------|---------------|
| CVE details + CVSS | **Shodan CVEDB** | MCP: `shodan.cve_lookup` |
| Exploit availability | **ExploitDB** | CLI: `searchsploit --json` |
| Exploit prediction | **EPSS** | API: `api.first.org/data/v1/epss` |
| Known exploited vulns | **CISA KEV** | via Shodan MCP (kev field) |
| CPE/product mapping | **Shodan CVEDB** | MCP: `shodan.cpe_search` |
| ATT&CK techniques | **MITRE ATT&CK** | Local: `attack-data` package |
| IP/domain reputation | **Shodan** | MCP: `shodan.search_host` |
| File/URL reputation | **VirusTotal** | MCP or API (key required) |
| Threat actor context | **MITRE ATT&CK Groups** | Web search + local data |

## Core Instructions

### Step 1 — CVE Enrichment Pipeline

For each CVE identified by vuln-analysis:

```bash
# 1. Shodan CVEDB lookup (via MCP — fastest, includes EPSS + KEV)
# MCP call: shodan.cve_lookup({ cve_id: "CVE-2024-XXXXX" })
# Returns: CVSS v2/v3, EPSS probability/percentile, KEV status, CPEs, references

# 2. ExploitDB search (local — no API needed)
searchsploit "{product} {version}" --json | python3 -m json.tool

# 3. EPSS direct query (if not via Shodan)
curl -s "https://api.first.org/data/v1/epss?cve=CVE-2024-XXXXX" | python3 -m json.tool

# 4. NVD lookup (web)
# https://nvd.nist.gov/vuln/detail/CVE-2024-XXXXX
```

### Step 2 — Vulnerability Prioritization Framework

Score each vulnerability using this composite model:

```
Priority Score = CVSS_base × EPSS_weight × Context_multiplier

Where:
  CVSS_base       = CVSS v3.1 score (0-10)
  EPSS_weight     = 1.0 + (EPSS_probability × 2)  # Boost if likely exploited
  Context_multiplier:
    On KEV list     = × 2.0  (actively exploited)
    Public exploit  = × 1.5  (ExploitDB/Metasploit/GitHub PoC)
    Internet-facing = × 1.3  (exposed to untrusted networks)
    Default         = × 1.0

Priority mapping:
  Score ≥ 15  → P0 Critical (remediate within 24-48 hours)
  Score ≥ 10  → P1 High (remediate within 1 week)
  Score ≥ 5   → P2 Medium (remediate within 1 month)
  Score < 5   → P3 Low (remediate in next cycle)
```

### Step 3 — MITRE ATT&CK Mapping

Map findings to ATT&CK techniques for report enrichment:

| Finding Type | ATT&CK Technique |
|--------------|------------------|
| RCE (web) | T1190 Exploit Public-Facing Application |
| SQLi | T1190 + T1505.003 Web Shell (if escalated) |
| Default creds | T1078 Valid Accounts |
| Phishing | T1566 Phishing |
| Privilege escalation (Linux) | T1068 Exploitation for Privilege Escalation |
| Kerberoasting | T1558.003 Kerberoasting |
| Pass-the-Hash | T1550.002 Pass the Hash |
| DCSync | T1003.006 DCSync |
| ADCS abuse | T1649 Steal or Forge Authentication Certificates |

### Step 4 — Attack Surface Intelligence

```bash
# Shodan search for exposed assets
# MCP: shodan.search_query("hostname:example.com")

# Certificate transparency monitoring
curl -s "https://crt.sh/?q=%.example.com&output=json" | \
  python3 -c "import json,sys; [print(x['name_value']) for x in json.load(sys.stdin)]" | \
  sort -u

# Technology version intelligence
# Cross-reference detected versions with CVE data
```

## Output Format

```json
{
  "cve": "CVE-2024-XXXXX",
  "title": "Remote Code Execution in Product X",
  "cvss_v3": 9.8,
  "epss_probability": 0.87,
  "epss_percentile": 0.99,
  "on_kev": true,
  "exploit_available": true,
  "exploit_sources": ["EDB-12345", "MSF exploit/unix/webapp/product_x_rce"],
  "cpes_affected": ["cpe:2.3:a:vendor:product:2.1:*:*:*:*:*:*:*"],
  "mitre_attack": ["T1190"],
  "priority_score": 29.4,
  "priority": "P0 Critical",
  "remediation": "Upgrade Product X to version 2.3+",
  "references": [
    "https://nvd.nist.gov/vuln/detail/CVE-2024-XXXXX",
    "https://vendor.com/security/advisory-2024-001"
  ]
}
```

## Output Checklist

- [ ] All CVEs enriched with CVSS, EPSS, KEV status
- [ ] Exploit availability checked (ExploitDB, Metasploit, GitHub PoC)
- [ ] Priority scores calculated using composite model
- [ ] MITRE ATT&CK techniques mapped to findings
- [ ] Attack surface intelligence gathered for exposed assets
- [ ] Enriched data ready for red-team-report consumption
