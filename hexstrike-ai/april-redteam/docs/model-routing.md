# MODEL ROUTING — April 2026 Red Team Stack
# When to use which model — decision tree + cost math

---

## The Core Question: Accuracy vs Cost

Every LLM call in this stack falls into one of four categories:

```
DECISION TREE

Is this task reasoning-critical?
  → Novel exploit design, complex attack chain, final report?
  YES → Claude Opus ($0.015/1k in)

Is this standard orchestration?
  → Tool output parsing, recon analysis, skill execution?
  YES → Claude Sonnet ($0.003/1k in) [80% of all calls]

Is this bulk data processing?
  → Log files, scan dumps, 50k+ token inputs?
  YES → DeepSeek ($0.00027/1k in) [37x cheaper than GPT-4o]

Is this sensitive or offline?
  → Real PII, patient data, lab without internet?
  YES → Ollama local ($0/1k in) [zero egress, free]
```

---

## Detailed Routing Table

| Task | Model | Why | Est. Cost |
|------|-------|-----|-----------|
| Attack path planning (MCTS input) | Opus | Multi-step logic chains | $0.05–0.20 |
| Novel exploit chain design | Opus | Creative reasoning | $0.10–0.50 |
| Report — executive summary | Opus | Nuanced language | $0.10–0.30 |
| Threat model (STRIDE-GPT) | Opus | Structured architecture analysis | $0.05–0.20 |
| Orchestrate MCP tool calls | Sonnet | Deterministic, fast, cheap | $0.01–0.05 |
| Parse nmap / nuclei output | Sonnet | Pattern recognition | $0.01–0.03 |
| Directory brute triage | Sonnet | Filter + prioritize | $0.01–0.02 |
| CVE analysis (VulnGPT) | Sonnet | Structured lookup | $0.02–0.08 |
| PentestGPT CTF reasoning | Sonnet | Good enough, 10x cheaper than Opus | $0.20–1.00 |
| AutoGPT OSINT monitoring | DeepSeek | 24/7 background, cost matters | $0.01–0.05/hr |
| Bulk log analysis (>50k tok) | DeepSeek | Context window + cost | $0.01–0.10 |
| Summarize large scan dumps | DeepSeek | Speed + cost | $0.005–0.02 |
| Format conversion (JSON→MD) | DeepSeek | Simple task, cheap | <$0.01 |
| Sensitive data (PII) | Ollama | Zero egress | $0 |
| Lab / offline testing | Ollama | No internet required | $0 |

---

## Tool-Specific Defaults

```yaml
# In .env / litellm_config.yaml:

HexStrike:
  default_model: claude-sonnet         # Orchestration layer
  analysis_model: claude-sonnet        # Finding analysis
  bulk_model: deepseek-bulk            # Large output parsing

PentestGPT:
  reasoning_model: claude-sonnet       # Task tree reasoning
  # Note: Opus gives marginally better results on novel CTFs
  # Switch per: PENTESTGPT_MODEL=claude-opus-4-20250514

PentestAgent (crew):
  crew_model: claude-sonnet            # Multi-agent comms
  memory_model: deepseek-bulk          # Shadow Graph ops
  report_model: claude-opus            # Final synthesis

STRIDE-GPT:
  threat_model: claude-opus            # Threat models = premium quality

VulnGPT:
  cve_model: claude-sonnet             # CVE lookup + analysis

AutoGPT:
  fast_llm: deepseek-bulk              # Quick monitoring tasks
  smart_llm: claude-sonnet             # Complex OSINT reasoning
```

---

## Context Window Strategy

Different models, different context limits:

```
MODEL                CONTEXT WINDOW   BEST FOR LARGE INPUTS
─────────────────────────────────────────────────────────────
Claude Opus          200k tokens       Full codebase analysis
Claude Sonnet        200k tokens       Full scan output
DeepSeek Chat        64k tokens        Mid-size logs
DeepSeek Reasoner    64k tokens        Complex reasoning, budget
Ollama Gemma2 9B     8k tokens         Short tasks only
Ollama Llama3.1 8B   128k tokens       Long-form local tasks
```

**Strategy for large scan outputs:**
```python
# Auto-route based on token count:
def route_model(prompt_tokens: int, task_type: str) -> str:
    if task_type == "sensitive":
        return "ollama-gemma2"
    if task_type in ["exploit_design", "report"]:
        return "claude-opus"
    if prompt_tokens > 50000:
        return "deepseek-bulk"         # Cheaper for large contexts
    return "claude-sonnet"             # Default
```

---

## Budget Enforcement

Configured in `litellm_config.yaml`:

```yaml
litellm_settings:
  max_budget: 10.0     # USD per day — hard cap
  budget_duration: 1d
  budget_fallback_model: deepseek-bulk  # Auto-switch when 80% hit
```

**Budget alerts:**

```bash
# Check today's spend:
curl -s http://localhost:4000/spend/logs | python3 -c "
import sys, json
logs = json.load(sys.stdin)
total = sum(l.get('spend', 0) for l in logs)
print(f'Today: \${total:.4f}')
"

# View by model:
curl -s http://localhost:4000/spend/logs?group_by=model | python3 -m json.tool
```

---

## Real Cost Examples (From Actual Engagements)

```
HTB machine — Easy (Sonnet throughout):
  Recon:      nmap parse + planning    = $0.02
  Enum:       gobuster + web analysis  = $0.05
  Exploit:    CVE research + attempt   = $0.08
  Privesc:    linpeas analysis + path  = $0.04
  Total:      ~$0.19

Web app pentest — 1 day (Sonnet + Opus report):
  Morning recon + OSINT (AutoGPT+DS)  = $0.40
  Afternoon scanning + analysis       = $1.20
  Manual testing (4h, Sonnet)         = $2.30
  Report writing (Opus, 45 min)       = $1.80
  Total:      ~$5.70

Bug bounty session — 3h:
  OSINT phase (AutoGPT + DeepSeek)    = $0.30
  Active recon (HexStrike + Sonnet)   = $0.80
  Vulnerability testing (Sonnet)      = $1.10
  Total:      ~$2.20
```

---

## Switching Models Mid-Session

```
"For the rest of this session, use Opus for all decisions.
 Cost is not a concern — this is a critical finding."

"Switch to DeepSeek for the next 20 tool calls —
 just parsing scan output, no reasoning needed."

"Use local Ollama for anything touching the client's
 employee PII data."
```

Claude Code respects these instructions and routes accordingly
via the LiteLLM proxy.

---

*April 2026 | Route smart — full Opus everywhere wastes money*
*Default Sonnet + Opus for reports = optimal cost/quality ratio*
