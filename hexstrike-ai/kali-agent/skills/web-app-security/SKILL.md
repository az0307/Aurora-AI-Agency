---
name: web-app-security
description: >
  Web application security testing following OWASP methodology, including
  injection testing, authentication bypass, XSS, CSRF, SSRF, IDOR, file
  upload attacks, API security testing, and web application firewalling.
  Use this skill whenever the user mentions web app testing, OWASP top 10,
  SQL injection, XSS, cross-site scripting, CSRF, SSRF, IDOR, insecure
  deserialization, file upload vulnerability, API security, JWT testing,
  session management testing, authentication bypass, authorization testing,
  Burp Suite, ZAP, OWASP testing guide, web app pentest, application
  security assessment, or any web-focused security testing task.
  Also trigger for: ffuf, gobuster, wfuzz, sqlmap, XSStrike, commix,
  directory brute force, parameter fuzzing, web fuzzing, cookie testing,
  header injection, HTTP verb tampering, CORS misconfiguration, clickjacking,
  content security policy, or "test this web application for vulnerabilities".
  Expert tools: sqlmap (SQLi), Burp Suite (intercepting proxy),
  ZAP (open-source proxy), ffuf (web fuzzer), nuclei (template scanner),
  XSStrike (XSS), commix (command injection), jwt_tool (JWT attacks).
compatibility:
  tools: [bash, python]
  mcps: [desktop-commander, hexstrike]
  skills: [vuln-analysis, scope-guard, exploit-dev]
---

# Web Application Security Skill

## Overview

Comprehensive web application testing following OWASP Testing Guide v4.2.
Maps every OWASP Top 10 category to the best expert tool and provides
step-by-step testing procedures. Feeds findings into vuln-analysis for
CVE correlation and exploit-dev for confirmed exploitation.

## Expert Tool Map — OWASP Top 10 (2021)

| OWASP Category | Best Tool | Backup Tool | MCP Available |
|----------------|-----------|-------------|---------------|
| A01 Broken Access Control | Manual + Burp/ZAP | ffuf + auth tokens | Burp MCP (partial) |
| A02 Cryptographic Failures | testssl.sh, nmap ssl scripts | sslyze | nmap-mcp |
| A03 Injection (SQLi) | **sqlmap** | manual + Burp | sqlmap-mcp (security-hub) |
| A03 Injection (XSS) | **XSStrike** | nuclei xss templates | nuclei-mcp |
| A03 Injection (Command) | **commix** | manual testing | Desktop Commander |
| A04 Insecure Design | Manual code review | semgrep | — |
| A05 Security Misconfiguration | **nuclei** misconfiguration templates | nikto | nuclei-mcp |
| A06 Vulnerable Components | **nuclei** CVE templates + wpscan | retire.js | nuclei-mcp |
| A07 Auth Failures | hydra + manual | Burp intruder | hydra via Desktop Commander |
| A08 Software/Data Integrity | Manual + sigcheck | — | — |
| A09 Logging Failures | Manual verification | — | — |
| A10 SSRF | Manual + nuclei SSRF templates | Burp Collaborator | nuclei-mcp |

## Core Instructions

### Step 1 — Web Application Fingerprinting
```bash
# Technology stack identification
whatweb {target_url} --log-json=/tmp/pentest/{target}/whatweb.json

# HTTP headers and security analysis
curl -sI {target_url} | tee /tmp/pentest/{target}/headers.txt

# Check key security headers:
# Strict-Transport-Security, Content-Security-Policy, X-Frame-Options,
# X-Content-Type-Options, Referrer-Policy, Permissions-Policy
```

### Step 2 — Content Discovery
```bash
# Directory and file enumeration
ffuf -u {target_url}/FUZZ -w /usr/share/wordlists/dirb/common.txt \
  -mc 200,301,302,403 -o /tmp/pentest/{target}/dirs.json -of json

# API endpoint discovery
ffuf -u {target_url}/api/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/api/api-endpoints.txt \
  -mc 200,301,405 -o /tmp/pentest/{target}/api_endpoints.json -of json

# Backup and sensitive file detection
ffuf -u {target_url}/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common-and-backup.txt \
  -mc 200 -o /tmp/pentest/{target}/sensitive_files.json -of json
```

### Step 3 — Injection Testing

**SQL Injection (Expert: sqlmap):**
```bash
# Auto-detect and exploit SQLi
sqlmap -u "{url_with_params}" --batch --level 3 --risk 2 \
  --threads 5 --output-dir=/tmp/pentest/{target}/sqlmap/

# Test POST parameters
sqlmap -u "{target_url}" --data="user=test&pass=test" --batch \
  --level 3 --risk 2 --output-dir=/tmp/pentest/{target}/sqlmap/

# With authentication cookie
sqlmap -u "{url}" --cookie="session=abc123" --batch --dbs
```

**XSS (Expert: XSStrike):**
```bash
# Reflected XSS detection
python3 xsstrike.py -u "{url_with_params}" --crawl -l 3

# DOM-based XSS via nuclei
nuclei -u {target_url} -t xss/ -o /tmp/pentest/{target}/xss.txt
```

**Command Injection (Expert: commix):**
```bash
# Auto-detect OS command injection
commix -u "{url_with_params}" --batch --output-dir=/tmp/pentest/{target}/commix/
```

### Step 4 — Authentication Testing
```bash
# Default credentials check
nuclei -u {target_url} -t default-logins/ -o /tmp/pentest/{target}/default_creds.txt

# Brute force login (use credential-attack skill for wordlists)
hydra -L users.txt -P passwords.txt {target} http-post-form \
  "/login:username=^USER^&password=^PASS^:F=Invalid" -t 4

# JWT analysis (if JWT auth detected)
# jwt_tool {token} -T  # Tamper mode
# jwt_tool {token} -C -d wordlist.txt  # Crack secret
```

### Step 5 — SSL/TLS Analysis
```bash
# Comprehensive SSL test
testssl.sh --json-pretty /tmp/pentest/{target}/ssl.json {target_url}

# Quick nmap SSL check
nmap --script ssl-enum-ciphers,ssl-cert,ssl-known-key -p 443 {target}
```

### Step 6 — API Security Testing
```bash
# If OpenAPI/Swagger spec available
nuclei -u {target_url} -t exposed-panels/ -t apis/

# Parameter fuzzing
ffuf -u {target_url}/api/users/FUZZ -w /usr/share/wordlists/seclists/Fuzzing/LFI/LFI-Jhaddix.txt \
  -mc 200 -fw 0

# CORS misconfiguration check
curl -sI -H "Origin: https://evil.com" {target_url} | grep -i "access-control"
```

## Output Format

```json
{
  "target": "https://app.example.com",
  "methodology": "OWASP Testing Guide v4.2",
  "technologies": ["nginx 1.24", "PHP 8.1", "Laravel 10", "MySQL 8.0"],
  "findings": [
    {
      "owasp_category": "A03:2021 Injection",
      "type": "SQL Injection",
      "severity": "critical",
      "url": "https://app.example.com/search?q=test",
      "parameter": "q",
      "tool": "sqlmap",
      "evidence": "Boolean-based blind SQLi confirmed — database: app_production",
      "cwe": "CWE-89",
      "remediation": "Use parameterized queries / prepared statements"
    }
  ]
}
```

## Output Checklist

- [ ] Technology fingerprinting completed
- [ ] Content discovery run (dirs, files, API endpoints)
- [ ] All OWASP Top 10 categories tested where applicable
- [ ] SQLi tested on all input parameters (GET/POST/cookies/headers)
- [ ] XSS tested (reflected, stored, DOM-based)
- [ ] Authentication and session management reviewed
- [ ] SSL/TLS configuration audited
- [ ] Security headers analyzed
- [ ] Findings mapped to OWASP category and CWE
