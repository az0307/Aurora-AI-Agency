# COST OPTIMIZATION — April 2026 Red Team Stack
# How to run professional engagements for under $20

---

## The Problem at Scale

Unoptimized AI pentesting burns tokens fast:
- Full web app recon: ~800k tokens (input)
- HTB full machine: ~400k tokens
- Bug bounty session (8h): ~2M+ tokens

At Opus rates ($0.015/1k) — unoptimized = $30+ per session.
With the strategies below: $2–8 per session.

---

## Strategy 1 — Three-Tier Model Routing

```
TIER 1: Claude Opus       ~$0.015/1k   Premium reasoning only
TIER 2: Claude Sonnet     ~$0.003/1k   General orchestration (80% of calls)
TIER 3: DeepSeek          ~$0.00027/1k Bulk processing (37x cheaper than GPT-4o)
TIER 0: Ollama (local)    $0           Sensitive data, offline use
```

**Rule of thumb:**
- Anything reading tool output → Sonnet
- Anything reasoning from scratch → check if Sonnet is good enough first
- Long context (>50k tokens) → DeepSeek
- Client PII → Ollama

---

## Strategy 2 — Redis LRU Caching

HexStrike caches all tool invocations in Redis (24h TTL by default).

```bash
# What gets cached:
# - nmap scans (same IP, same flags = cache hit)
# - nuclei results (same target = cache hit)
# - Shodan/NVD queries (same CVE = instant)
# - subdomain enumeration (passive only)

# What doesn't get cached (intentionally):
# - MSF sessions (stateful)
# - Hydra brute-force (dynamic)
# - Live terminal (kali-mcp)

# Check cache hit rate:
docker exec rt-redis redis-cli info stats | grep 'keyspace_hits\|keyspace_misses'

# Typical cache hit rate after first scan: 60-80%
# This cuts repeat scan cost to near-zero
```

**Cost impact:**
```
First scan of target: $0.50 (full token cost)
Re-scan same target (24h window): $0.08 (mostly cache hits)
Re-scan after cache clear: $0.50 again
```

---

## Strategy 3 — AutoGPT with DeepSeek Backend

AutoGPT runs 24/7 for monitoring. Cost compounds fast if using premium models.

```bash
# .env — configure AutoGPT for cost efficiency:
AUTOGPT_FAST_LLM=deepseek-chat        # Simple, fast tasks
AUTOGPT_SMART_LLM=deepseek-chat       # Even complex OSINT is fine on DeepSeek

# Monthly cost comparison (continuous monitoring, 1 target):
# GPT-4o:       ~$180/month
# Claude Sonnet: ~$45/month
# DeepSeek:      ~$5/month
```

---

## Strategy 4 — Prompt Compression

Long context = expensive. Compress tool output before feeding to LLM.

```python
# HexStrike auto-compresses nuclei output:
# Full nuclei output: 500k chars
# Compressed (findings only): 8k chars
# Token reduction: ~98%

# Manual compression for large nmap:
def compress_nmap(raw_output: str) -> str:
    """Keep only open ports with services — drop everything else"""
    lines = raw_output.split('\n')
    return '\n'.join(
        line for line in lines
        if '/tcp' in line and 'open' in line
        or '/udp' in line and 'open' in line
        or line.startswith('Nmap scan report')
    )

# Before: 15,000 token nmap output
# After: 200 token compressed output
# Cost reduction: ~98%
```

---

## Strategy 5 — Batch Multiple Tasks

Instead of one LLM call per tool result, batch them:

```
# Expensive (separate calls):
[Call 1] "Analyze this nmap result"         → $0.03
[Call 2] "Analyze this gobuster result"     → $0.02
[Call 3] "Analyze this nikto result"        → $0.02
Total: $0.07

# Optimized (one batched call):
[Call 1] "Analyze all three results:
  nmap: [...]
  gobuster: [...]
  nikto: [...]
  Give me a unified attack surface summary."  → $0.04

Savings: ~43%
```

HexStrike does this automatically via the `batch_analysis` parameter.

---

## Strategy 6 — Session Cost Dashboard

Track spend in real-time via Grafana (localhost:3000):

```
Dashboard: "Red Team Stack — Operations Dashboard"
Panel: "LLM Cost Today (USD)"
Panel: "Cost by Model (pie chart)"
Panel: "Token Usage Rate (timeseries)"
```

**Budget alerts configured in litellm_config.yaml:**
```yaml
litellm_settings:
  max_budget: 10.0        # Hard cap $10/day
  budget_duration: 1d
  budget_fallback_model: deepseek-bulk  # Auto-switch at 80% ($8)
```

---

## Per-Engagement Cost Breakdown

### Easy CTF (HackTheBox)

```
Phase              Model      Tokens     Cost
──────────────────────────────────────────────
Recon + planning   Sonnet     12k        $0.04
Enum analysis      Sonnet     25k        $0.08
Exploit research   Sonnet     18k        $0.05
Privesc path       Sonnet     15k        $0.05
Shell upgrades     Sonnet     8k         $0.02
─────────────────────────────────────────────
Total                                    ~$0.24
PentestGPT bench avg:                    ~$1.11
```

### Web App Pentest (1 day)

```
Phase              Model      Tokens     Cost
──────────────────────────────────────────────
OSINT (AutoGPT)    DeepSeek   80k        $0.09
Subdomain recon    Sonnet     15k        $0.05
Nuclei scan        Sonnet     40k        $0.12
Manual web test    Sonnet     120k       $0.36
Finding docs       Sonnet     30k        $0.09
Exec report        Opus       25k out    $1.88
Tech report        Sonnet     60k out    $0.90
─────────────────────────────────────────────
Total                                    ~$3.49
```

### Bug Bounty (8h)

```
Phase              Model      Cost
──────────────────────────────────────
OSINT overnight    DeepSeek   $0.30
Morning recon      Sonnet     $0.80
Vuln testing       Sonnet     $1.10
Report (if found)  Opus       $1.20
─────────────────────────────────────
Total: ~$3.40 (not counting find value)
```

---

## ROI Calculation

If a bug bounty program pays $2,000 for a critical:

```
Cost to find: $3.40 (8h session)
Payout:       $2,000
ROI:          58,724%

Compare to manual (no AI):
Time:         2-3 days (no OSINT automation, no auto-scan)
Missed:       Patterns AI catches in nuclei/automation
```

For client engagements at $150/hr:
```
8h web app pentest:
  Human labor: $1,200
  LLM cost:    $3.49
  Total cost:  $1,203.49
  Billing:     $1,200 (standard rate)
  LLM = 0.29% of engagement cost
```

---

## Quick Cost-Cut Checklist

```
□ Set AUTOGPT_FAST_LLM=deepseek-chat in .env
□ Verify Redis caching is running: docker exec rt-redis redis-cli ping
□ Enable LiteLLM budget cap in litellm_config.yaml (max_budget: 10.0)
□ Use make clean-cache between engagements (clears stale cache)
□ Use DeepSeek for any task with >50k token context
□ Route reports through Opus — worth the premium
□ Monitor spend daily: make grafana → open dashboard
```

---

*April 2026 | Smart routing = same quality, 5-10x lower cost*
*The $0.24 CTF machine solve is not a typo*
