# Omni-router — one endpoint, every model, automatic fallbacks

A self-hosted **LiteLLM** proxy that fronts **OpenRouter** (and its free models),
Anthropic, Moonshot/Kimi, and Google Gemini behind **one** endpoint. Agents call a
single alias (`auto` or `auto-free`); when a model rate-limits or errors, the
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

## The two aliases (what agents call)

| Alias | Strategy | Chain (edit in `config.yaml`) |
|---|---|---|
| `auto` | **quality-first · PAID-ONLY (PII-safe)** — never drops to a free tier | claude → kimi |
| `auto-free` | **cost-first · non-sensitive only** — free first, escalate on failure | openrouter/free → free-llama-70b → free-qwen-72b → kimi |

Retries hit the *same* model first (`num_retries`), then the chain takes over.
A model that fails `allowed_fails` times is benched for `cooldown_time` seconds.

## Point the agents at it

**Claude Code** (Anthropic endpoint — one-shot wrapper, keeps your default `claude` clean):
```sh
claude-router() {
  ANTHROPIC_BASE_URL="http://127.0.0.1:4000" \
  ANTHROPIC_AUTH_TOKEN="$LITELLM_MASTER_KEY" \
  ANTHROPIC_MODEL="auto" \
    claude "$@"          # or ANTHROPIC_MODEL=auto-free for the cheap chain
}
```

**OpenAI-compatible agents** (OpenCode, Aider, Goose, Crush, TARS) — point the
base URL at the proxy, key = master key, model = `auto` / `auto-free`:
```sh
export OPENAI_BASE_URL="http://127.0.0.1:4000/v1"
export OPENAI_API_KEY="$LITELLM_MASTER_KEY"
# e.g. aider --model auto-free   ·   opencode (set provider baseURL + model in its config)
```

## Free-model caveats (read before relying on them)

- OpenRouter's `:free` models **rotate, get deprecated, and are rate-limited**.
  The ids in `config.yaml.example` are *examples* — confirm the live list at
  <https://openrouter.ai/models?max_price=0> and keep the chain a few deep so one
  disappearing model doesn't break routing.
- Free tiers may **train on your inputs** and have low daily caps — never send
  client PII (Y.M.I data, credentials) through a free model. Keep those on the
  paid `auto` chain, or exclude them at the agent layer.
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
