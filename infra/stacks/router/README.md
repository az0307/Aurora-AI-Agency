# Omni-router — one endpoint, every model, automatic fallbacks

A self-hosted **LiteLLM** proxy that fronts **OpenRouter** (and its free models),
Anthropic, Kimi, Hugging Face and Gemini behind **one** endpoint. Agents call a
single job alias (`general`, `general-free`, `code`, …); when a model rate-limits or errors, the
router **falls through a chain** to the next one instead of failing the request.

- **OpenAI-compatible:** `http://127.0.0.1:4000/v1` — OpenCode, Aider, Goose, Crush, TARS
- **Anthropic-compatible:** `http://127.0.0.1:4000/v1/messages` — Claude Code
- **Admin UI:** `http://127.0.0.1:4000/ui` (optional, needs the DB)

## Why both "open router" and "omni router"

- **OpenRouter** = a *hosted* gateway; it aggregates dozens of providers and
  publishes **free** model variants (`…:free`). One `OPENROUTER_API_KEY` unlocks
  them. It even has its own `openrouter/auto` meta-model that picks + falls back
  server-side.
- **LiteLLM** = the *self-hosted* omni-router on your box. It normalizes every
  provider to one OpenAI/Anthropic API and adds **your own** cross-provider
  fallback chains, retries, timeouts, and cooldowns — so the chain spans
  OpenRouter *and* Anthropic *and* Kimi *and* Gemini, not just one vendor.

Using both means: cheap/free first, your quality model as the safety net (or vice
versa), and a single URL every agent points at.

## Run it

```sh
cd infra/stacks/router
cp .env.example .env && $EDITOR .env          # real keys; never commit .env
cp config.yaml.example config.yaml            # edit model ids/chains to taste
docker compose up -d
curl -s http://127.0.0.1:4000/health/liveliness   # {"status":"healthy"} when ready
```

## Job aliases (what agents call)

Pick by **job**, not by vendor. Each chain is curated best → fallback: the first
model is the one to use for that job; the others only answer when it's down,
rate-limited or erroring.

| Alias | Job | Chain (edit in `config.yaml`) | Data |
|---|---|---|---|
| **`general`** | everyday default | Claude Sonnet 5 → GPT-5.6 Sol → Kimi Code → DeepSeek V4.1 Flash | **paid-only, PII-safe** |
| **`general-free`** | everyday, $0 | Nemotron 3 Ultra 550B → Inkling → Qwen3.8-27B → Gemma 4 31B → OpenRouter free router | non-sensitive only |
| `code` | coding | Claude Sonnet 5 → Grok Build → Kimi K2.7 Code → DeepSeek V4 Pro | paid-only |
| `code-free` | coding, $0 | North Mini Code → Laguna S 2.1 → Qwen3.8-27B → Nemotron 3 Ultra | non-sensitive only |
| `reason` | hard problems, plans, reviews | Claude Opus 5.5 → GPT-5.6 Sol → Kimi K3 → DeepSeek V4 Pro | paid-only |
| `fast` | cheap bulk work | DeepSeek V4.1 Flash → MiniMax M3 → Gemini 3.8 Flash → Qwen3.8 Flash | paid-only |
| `vision` | screenshots, photos, video, audio | Gemini 3.8 Flash → Claude Sonnet 5 → GPT-5.6 Sol | paid-only |
| `search` | live web answers with citations | Perplexity Sonar Pro → Sonar | paid-only |
| `research` | multi-step research report | Sonar Deep Research → Sonar Reasoning Pro → Sonar Pro | paid-only |
| `hermes` | Nous models | Hermes 4 405B → HF Hermes 3 70B → DeepSeek V4.1 Flash | paid-only; Hermes 4 has **no tool calling**, so agents end up on DeepSeek |
| `uncensored` | fewer refusals, chat only | Dolphin Venice 24B → Cydonia 24B → Euryale 70B | never client data |
| `uncensored-agent` | fewer refusals + tools (Hermes) | Euryale L3.1 70B → local Qwen3 8B abliterated | never client data |
| `uncensored-free` | fewer refusals, $0, private | local Dolphin 3 8B → local Qwen3 8B abliterated | needs `../ollama` |

**Older names keep working** and run the same chain: `auto` = `general`,
`auto-free` = `general-free`, `auto-code` = `code`, `auto-cheap` = `fast`,
`auto-search` = `search`. They are full entries, not LiteLLM `model_group_alias`
shortcuts, because an alias does **not** carry its target's fallback chain (tested:
the request fails on the first error instead of falling back).

Every free model in a chain supports tool calling, so agents like Hermes can use them.

**Check the chains after any edit** (offline, no keys needed):

```sh
python3 -m venv /tmp/ll && /tmp/ll/bin/pip install -q litellm pyyaml
/tmp/ll/bin/python check-chains.py config.yaml 2>/dev/null
# static checks: OK, then one PASS line per job alias
```

Every entry is also callable by name:

| Family | Via OpenRouter | Via Hugging Face (`HF_TOKEN`) |
|---|---|---|
| Perplexity | `perplexity-sonar`, `perplexity-sonar-pro`, `perplexity-reasoning`, `perplexity-research` | — |
| DeepSeek | `deepseek-flash`, `deepseek-pro` | `hf-deepseek`, `hf-deepseek-r1` |
| Kimi (Moonshot) | `kimi-k3`, `kimi-code-or` (+ `kimi-cheap` direct) | `hf-kimi`, `hf-kimi-k3` |
| GLM (Zhipu) | `glm`, `glm-flash`, `free-glm` | `hf-glm` |
| MiniMax | `minimax` | `hf-minimax` |
| Qwen | `qwen-max`, `qwen-flash`, `free-qwen` | `hf-qwen`, `hf-qwen-coder` |
| Grok / Claude / GPT / Gemini / Hermes | `grok`, `grok-build`, `claude-opus`, `gpt`, `gemini-flash`, `hermes-405b` | `hf-hermes`, `hf-gpt-oss` |
| **Uncensored** (paid) | `dolphin`, `cydonia`, `skyfall`, `unslopnemo`, `euryale`, `magnum`, `lunaris`, `mythomax` | `hf-stheno`, `hf-lunaris` |
| **Uncensored, free** (local, needs `../ollama`) | `local-dolphin`, `local-dolphin-mistral`, `local-qwen3-abliterated`, `local-gemma3-abliterated` | — |

**Uncensored models are call-by-name only.** None of them is in any fallback chain, so no
request ever falls through to one by accident. Cheapest paid: `lunaris` (~$0.04/M in) and
`mythomax`. Provider terms still apply: legal adult/creative content is fine, illegal
content is not, anywhere.

**Free = local.** OpenRouter currently has no free uncensored model, so the `$0` ones run
on this box's CPU through Ollama. They're slow (a few tokens/sec), and only one is loaded
at a time. Start this router first (it creates the shared `aurora-llm` network), then
`../ollama`, then pull what you want:

```sh
docker compose -f ../ollama/docker-compose.yml exec ollama ollama pull dolphin3:8b
# also: dolphin-mistral:7b · huihui_ai/qwen3-abliterated:8b · huihui_ai/gemma3-abliterated:4b
```
Hugging Face models go through `router.huggingface.co/v1` with one `HF_TOKEN`.

Retries hit the *same* model first (`num_retries`), then the chain takes over.
### Uncensored models by price (OpenRouter, per 1M tokens in/out, 2026-09-24)

None of these is free on OpenRouter right now; the $0 options run on your own box.
Only three support tool calling (marked 🛠), which matters for agents like Hermes.

| Tier | Name | Model | Price | Context | Notes |
|---|---|---|---|---|---|
| $0 | `local-dolphin`, `local-qwen3-abliterated` 🛠, `local-gemma3-abliterated`, `local-dolphin-mistral` | Ollama on the server | $0 | 8–32k | Slow on CPU (a few words/s); private; needs ~3–5 GB RAM free |
| Near-free | `lunaris` | Sao10K Lunaris 8B | $0.04 / $0.05 | 8k | Short chats |
| Near-free | `mythomax` | MythoMax 13B | $0.08 / $0.11 | 8k | Old but cheap storytelling |
| **Best value** | `dolphin` | Dolphin Mistral 24B **Venice (uncensored)** | $0.20 / $0.90 | 128k | Best general "no refusals" assistant |
| Cheap | `cydonia` | Cydonia 24B v4.1 (uncensored) | $0.30 / $0.50 | 128k | Fiction, roleplay |
| Mid | `unslopnemo` | UnslopNemo 12B | $0.40 / $0.40 | 1M | Very long inputs |
| Mid | `skyfall` | Skyfall 36B | $0.55 / $0.80 | 32k | Smarter storytelling |
| Mid | `euryale` | Euryale L3.3 70B | $0.65 / $0.75 | 128k | Long-form creative |
| Mid 🛠 | `euryale-agent` | Euryale L3.1 70B | $0.85 / $0.85 | 128k | The only paid one here that can use tools |
| Premium | `magnum` | Magnum v4 72B | $2.50 / $5.00 | 32k | Best prose, pricey |
| HF credits | `hf-stheno`, `hf-lunaris` | via Hugging Face | from your HF credits | 8k | Uses `HF_TOKEN` |

"Uncensored" means fewer refusals, not no rules: provider terms still apply, and the
PII rule is absolute — none of these ever sees client data.

A model that fails `allowed_fails` times is benched for `cooldown_time` seconds.

## Point the agents at it

**Claude Code** (Anthropic endpoint — one-shot wrapper, keeps your default `claude` clean):
```sh
claude-router() {
  ANTHROPIC_BASE_URL="http://127.0.0.1:4000" \
  ANTHROPIC_AUTH_TOKEN="$LITELLM_MASTER_KEY" \
  ANTHROPIC_MODEL="code" \
    claude "$@"          # or general / reason / code-free
}
```

**OpenAI-compatible agents** (OpenCode, Aider, Goose, Crush, TARS) — point the
base URL at the proxy, key = master key, model = a job alias (`general`, `code`, `general-free`, …):
```sh
export OPENAI_BASE_URL="http://127.0.0.1:4000/v1"
export OPENAI_API_KEY="$LITELLM_MASTER_KEY"
# e.g. aider --model code-free   ·   opencode (set provider baseURL + model in its config)
```

## Free-model caveats (read before relying on them)

- OpenRouter's `:free` models **rotate, get deprecated, and are rate-limited**.
  The ids in `config.yaml.example` are *examples* — confirm the live list at
  <https://openrouter.ai/models?max_price=0> and keep the chain a few deep so one
  disappearing model doesn't break routing.
- Free tiers may **train on your inputs** and have low daily caps — never send
  client PII (Y.M.I data, credentials) through a free model. Keep those on the
  paid chains (anything without `-free`), or exclude them at the agent layer.
- Gemini's free tier comes from an **AI Studio** key (`GEMINI_API_KEY`), separate
  from OpenRouter.

## Security

- Binds **127.0.0.1** only — expose the UI/API through **Cloudflare Access**, never
  publicly. The `master_key` is the one credential that reaches every provider, so
  treat it like a root token (rotate it, keep it in Infisical/Bitwarden).
- Pin the image to a **digest** for production (`main-stable` moves).
- The optional DB (virtual keys, per-key budgets, spend logs) lets you hand
  agents *scoped* keys instead of the master key — enable it once more than one
  caller shares the box.

See [`../../AGENTS.md`](../../AGENTS.md) for how this fits the agent failover chain,
and [`../../SERVICES.md`](../../SERVICES.md) for the host port map.
