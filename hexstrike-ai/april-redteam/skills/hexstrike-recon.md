# SKILL: hexstrike-recon
# Claude Code skill file — drop in project root or CLAUDE.md skills section
# Invoked when: user asks to "run recon", "enumerate", "scan" a target

## Trigger Phrases
- "run recon on [target]"
- "enumerate [target]"
- "find subdomains of [target]"
- "what's running on [target]"
- "scan [target] with hexstrike"

## Skill Definition

When triggered, execute the following recon pipeline using hexstrike-ai MCP tools.

### Step 1 — Authorization Check
ALWAYS confirm before scanning:
```
Before running: confirm [TARGET] is authorized.
User must state: ownership or program scope.
If not confirmed → DO NOT PROCEED.
```

### Step 2 — Target Classification
Determine target type from URL/IP:
- Domain/subdomain → run web recon pipeline
- IP address → run network recon pipeline
- CIDR range → run network discovery pipeline

### Step 3 — Web Recon Pipeline (for domains)
```python
# Invoke in order via hexstrike MCP:
tools_sequence = [
    # Subdomain discovery
    ("subfinder", {"target": TARGET_DOMAIN}),
    ("amass", {"domain": TARGET_DOMAIN, "mode": "passive"}),
    
    # Resolve and probe all discovered subdomains
    ("dnsx", {"input": "subdomains.txt", "a": True, "cname": True}),
    ("httpx", {"input": "resolved.txt", "ports": "80,443,8080,8443,3000,5000,8888"}),
    
    # Technology fingerprint on live hosts
    ("whatweb", {"target": LIVE_HOSTS}),
    
    # Directory discovery on main target
    ("ffuf", {"url": TARGET_URL, "wordlist": "raft-large-directories.txt"}),
    
    # Historical URLs
    ("gau", {"domain": TARGET_DOMAIN}),
    ("waybackurls", {"domain": TARGET_DOMAIN}),
    
    # Vulnerability scan — critical/high only
    ("nuclei", {"targets": LIVE_HOSTS, "severity": "critical,high"}),
]
```

### Step 4 — Network Recon Pipeline (for IPs)
```python
tools_sequence = [
    # Host discovery
    ("nmap_discovery", {"target": TARGET, "flags": "-sn --min-rate 3000"}),
    
    # Service scan on live hosts
    ("nmap_services", {"target": LIVE_HOSTS, "flags": "-sV -sC --open"}),
    
    # Full port scan (background)
    ("nmap_fullscan", {"target": LIVE_HOSTS, "flags": "-p- --min-rate 5000 -T4"}),
    
    # Vuln scripts on discovered services
    ("nmap_vuln", {"target": LIVE_HOSTS, "flags": "--script vuln"}),
]
```

### Step 5 — Output Structure
```
Save all results to:
  loot/[ENGAGEMENT]/recon/
    ├── subdomains.txt          # All discovered subdomains
    ├── live_hosts.txt          # Responding HTTP/HTTPS hosts
    ├── live_hosts_full.json    # Full httpx JSON output
    ├── tech_stack.txt          # whatweb / wappalyzer results
    ├── directories.txt         # ffuf / gobuster results
    ├── historical_urls.txt     # waybackurls + gau
    ├── vuln_scan.json          # nuclei JSON output
    └── nmap_services.xml       # nmap XML (full scan)

Present summary:
  - Total hosts discovered: N
  - Live web hosts: N
  - Tech stack identified: [list]
  - Interesting findings: [admin panels, unusual ports, old software]
  - Critical/High vulns from nuclei: N
  - Recommended next step: [specific action]
```

### Step 6 — Auto-Flag Interesting Findings
Automatically highlight if found:
- Admin panels (`/admin`, `/manager`, `/console`, `/dashboard`, `/.git`)
- Exposed services: Jenkins, Grafana, Kibana, Jupyter, Portainer
- S3 buckets / cloud storage references
- API documentation (`/swagger`, `/api-docs`, `/graphql`)
- Development/staging hosts (`dev.`, `staging.`, `test.`, `qa.`, `uat.`)
- Old software versions (check against NVD for recent CVEs)
- Unusual/high ports with services

## Example Invocation

```
User: "Run full recon on example.com — I'm an authorized security researcher"

Claude: Running HexStrike recon pipeline on example.com...
[Invokes hexstrike MCP tools in sequence]
[Saves all output to loot/]
[Returns structured summary with interesting findings]
```

## Cost Notes
- This skill uses ~50-200k tokens depending on target size
- HexStrike caches scan results — same target scanned twice costs near-zero
- Use Sonnet model for this skill (no need for Opus — deterministic execution)
