# SKILL: vulngpt-analyzer
# AI vulnerability analysis — nmap data + Shodan + CVE intelligence
# Triggered when: "analyze vulnerabilities", "CVE analysis", "what's exposed on Shodan"

## Trigger Phrases
- "analyze vulnerabilities on [target]"
- "run VulnGPT on [target]"
- "what CVEs affect [service/version]"
- "check Shodan for [target]"
- "give me CVE intelligence on [tech stack]"
- "analyze this nmap output"

## VulnGPT Analysis Workflows

### Workflow A — Nmap Output Analysis
**Input:** Raw nmap scan output
**Output:** AI-analyzed vulnerability report with CVE mapping

```python
# Parse nmap XML output through VulnGPT
vulngpt_prompt = f"""
Analyze this nmap scan output and identify all vulnerabilities:

{NMAP_OUTPUT}

For each open port/service:
1. Identify the service version
2. Look up known CVEs for this version
3. Assess exploitability (is PoC available?)
4. Rate severity (Critical/High/Medium/Low)
5. Recommend specific test (what tool/technique to use)

Output as structured JSON:
{{
  "host": "[IP]",
  "findings": [
    {{
      "port": 22,
      "service": "OpenSSH 7.4",
      "cves": ["CVE-2018-15473"],
      "severity": "Medium",
      "exploitability": "High - PoC available",
      "test": "Use openssl-cve script or metasploit module"
    }}
  ],
  "critical_count": 0,
  "high_count": 2,
  "next_steps": ["Prioritize testing port X because..."]
}}
"""
```

### Workflow B — Shodan Intelligence Query
**Input:** Domain or IP address
**Output:** Exposure analysis from Shodan API

```python
# VulnGPT v2 (FastAPI + Shodan) call:
import requests

def shodan_vulngpt_analysis(target):
    response = requests.post(
        "http://localhost:8080/analyze",
        json={"target": target}
    )
    return response.json()

# Returns:
# {
#   "target": "target.com",
#   "shodan_results": {
#     "ports": [80, 443, 22, 3389],
#     "services": {"22": "OpenSSH 7.4", "3389": "RDP"},
#     "vulns": ["CVE-2018-15473"],
#     "country": "AU",
#     "isp": "Telstra"
#   },
#   "ai_analysis": "The target has RDP exposed to the internet (port 3389)...",
#   "recommendations": ["Disable RDP internet exposure", "Patch OpenSSH"]
# }
```

### Workflow C — CVE Lookup and Intelligence
**Input:** CVE ID or service/version string
**Output:** Detailed CVE analysis with exploitation guidance

```python
# Using GPT_Vuln-analyzer CVE module:
from vulngpt.cve_gpt import summarize_cve

def cve_intelligence(cve_id):
    result = summarize_cve(cve_id)
    return {
        "cve": cve_id,
        "cvss": result["base_score"],
        "severity": result["severity"],
        "attack_vector": result["attack_vector"],
        "products": result["product_name"],
        "summary": result["summary"],
        "remediation": result["remediation"]
    }

# Example:
# cve_intelligence("CVE-2024-3400")
# → PAN-OS command injection, CVSS 10.0, Network attack vector
```

### Workflow D — Tech Stack CVE Sweep
**Input:** Tech stack from OSINT / HexStrike fingerprint
**Output:** All CVEs affecting confirmed technologies

```
Using vulngpt MCP, sweep all CVEs for this tech stack:

Frontend: React 18.2.0
Backend: Node.js 18.12.0, Express 4.18.2
Database: PostgreSQL 14.5
Auth: jsonwebtoken 8.5.1 (JWT)
Cloud: nginx 1.22.1

For each component:
1. Check NVD for CVEs in this version range
2. Check if CISA KEV (actively exploited)
3. Check if PoC exploit exists on GitHub/Exploit-DB
4. Output: CVSS score, patch version, exploitation likelihood

Prioritize: CISA KEV first, CVSS 9.0+ second, then 7.0+
Save to: loot/[MISSION]/vulngpt_tech_sweep.json
```

## Output Integration

VulnGPT output feeds directly into:

```
vulngpt analysis
     │
     ├── Critical/High CVEs → PentestThinkingMCP attack planning
     │                        "Plan exploitation of CVE-XXXX"
     │
     ├── Service versions → HexStrike targeted nuclei scan
     │                      "nuclei -t cves/ -target [IP]"
     │
     ├── Shodan exposure → Kali MCP specific exploitation
     │                     "MSF: use exploit/[CVE module]"
     │
     └── CVE list → Final report Section 3 (vulnerability catalog)
```

## MCP Tool Invocations

When the skill is triggered, call these in order:

```
1. kali_exec("nmap -sV -sC --open [TARGET]") → get service versions

2. vulngpt.analyze_nmap(nmap_output) → get CVE mapping

3. vulngpt.shodan_query(target) → get exposure data (if Shodan key available)

4. vulngpt.cve_lookup(cve_list) → enrich each CVE with full intelligence

5. Save structured output to loot/[MISSION]/vulngpt_report.json

6. Summarize: 
   "VulnGPT found X critical, Y high, Z medium vulnerabilities.
    Top priority: [CVE] on port [PORT] — [why it matters].
    Recommend: [specific next tool/test]"
```

## Error Handling

```python
# If Shodan API key not set:
if not SHODAN_API_KEY:
    warn("SHODAN_API_KEY not set — skipping Shodan analysis")
    warn("Add to .env: SHODAN_API_KEY=your-key")
    # Continue with nmap-only analysis

# If CVE lookup fails (NVD rate limit):
try:
    result = cve_intelligence(cve_id)
except RateLimitError:
    warn(f"NVD rate limit hit for {cve_id}")
    warn("Falling back to cached data / manual lookup")
    result = {"cve": cve_id, "note": "Manual lookup required"}
```

## Cost Notes

- Nmap analysis: ~5-10k tokens → ~$0.02-0.05 (Sonnet)
- Full tech stack sweep (10 components): ~20-30k tokens → ~$0.06-0.09
- Shodan API: $49/month for full access, free tier has basic queries
- NVD API: Free (rate limited at 5 requests/30 seconds unauthenticated)
  Get free API key at nvd.nist.gov/developers/request-an-api-key (50 req/30s)

## Environment Variables Required

```bash
# In .env:
OPENAI_API_KEY=sk-...          # For VulnGPT v2
SHODAN_API_KEY=your-key        # Optional — Shodan intelligence
NVD_API_KEY=your-key           # Free — faster NVD queries
ANTHROPIC_API_KEY=sk-ant-...   # For VulnGPT with Claude backend
```
