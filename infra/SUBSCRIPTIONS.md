# Your subscriptions — what each one unlocks, and where

You already pay for several AI plans. Most of them **do not** give you an API key: they work
through that vendor's own app or CLI, logged in with your account. This page says, for each
plan, which tool uses it, whether it works on the headless server, and the traps.

> Rule of thumb: **subscriptions run the vendors' own tools** (Claude Code, Codex, Gemini CLI,
> Cursor, Antigravity, Grok). **The router and Hermes run on API keys**, except the two
> Hermes subscription logins marked below (SuperGrok, ChatGPT).

## At a glance

| Plan you pay for | Tool it powers | On your laptop | On the server (headless) | Hermes / router? |
|---|---|---|---|---|
| **Claude Pro / Max** | **Claude Code** | ✅ `claude` → `/login` | ✅ same; the login link prints in the terminal | Router/Hermes need `ANTHROPIC_API_KEY`. Hermes OAuth works **only on Max + purchased extra-usage credits**; **Pro can't** |
| **ChatGPT Plus / Pro** | **Codex CLI** | ✅ `codex` → sign in with ChatGPT | ✅ over SSH, forward the login port: `ssh -N -L 1455:127.0.0.1:1455 aurora@aurora-01` | ✅ **Hermes: `hermes model` → "ChatGPT or Codex Subscription"** (device-code login) |
| **Google AI Pro (Gemini)** | **Gemini CLI**, **Antigravity** | ✅ `gemini` → "Login with Google" using the subscription account | ⚠️ headless needs `GEMINI_API_KEY` (separate, from AI Studio) | ❌ no subscription login; Hermes/router use the API key or OpenRouter |
| **SuperGrok** | **Grok app**, **Hermes** | ✅ grok.com / apps | ✅ Hermes login with `--no-browser` | ✅ **Hermes: `hermes auth add xai-oauth --no-browser`** → `/model supergrok` (Grok 4.6) or `/model supergrok-build` (Grok Build) |
| **Cursor** | **Cursor** editor + **Cursor CLI** | ✅ app, or `cursor-agent login` | ✅ `NO_OPEN_BROWSER=1 cursor-agent login`, or a `CURSOR_API_KEY` | ❌ |
| **Perplexity Pro** + **Comet** | Perplexity app, Comet browser | ✅ desktop/mobile apps | ❌ (desktop apps) | Perplexity models are in the router via **OpenRouter** (`/model search`), billed to OpenRouter, not your Pro plan |

## Per plan

### Claude (Pro / Max) → Claude Code
- Install (laptop or server): `npm install -g @anthropic-ai/claude-code`, then run `claude` and
  choose **Claude account** at `/login`. Uses your plan's Claude Code allowance; no API key.
- Point it at the router instead (to use the fallback chains or other models):
  see `claude-router` in [stacks/router/README.md](./stacks/router/README.md). That path bills
  the router's providers, **not** your Claude plan.
- **Trap:** Hermes' Anthropic OAuth only spends *extra-usage credits on a Max plan*. On Pro it
  doesn't work at all; give Hermes an `ANTHROPIC_API_KEY` (pay per token).

### ChatGPT (Plus / Pro) → Codex CLI, and Hermes
- Install: `npm install -g @openai/codex`, run `codex`, choose **Sign in with ChatGPT**.
- On the server over SSH the login redirects to `localhost:1455`, so open the tunnel above
  first, then complete the login in your laptop's browser.
- **Hermes on your ChatGPT plan:** on the box run `docker exec -it hermes hermes model` →
  **ChatGPT or Codex Subscription** → device code (open the URL, enter the code). Then pick it
  per chat with `/model`. Which plan tiers qualify and how usage counts against limits is not
  documented by Hermes yet; watch your Codex usage page.

### Google AI Pro → Gemini CLI + Antigravity
- **Gemini CLI:** `npm install -g @google/gemini-cli`, run `gemini`, **Login with Google** with
  the account that holds the subscription (higher limits than the free tier).
  On the headless server use `GEMINI_API_KEY` from <https://aistudio.google.com/apikey> instead.
- **Antigravity** (Google's agentic IDE, desktop app, and CLI): download from
  <https://antigravity.google/download> and sign in with the same Google account.
  For the **Antigravity CLI**, follow the **"Antigravity CLI" tab** at
  <https://antigravity.google/docs/getting-started> — Google's page is the only source for its
  install command. ⚠️ The npm packages named `antigravity` / `antigravity-cli` are
  **placeholders, not Google's**; don't install them.
- **Trap:** there's no way to sign Hermes or the router into a Gemini *subscription*; they use
  the API key or OpenRouter (`gemini-flash-or`).

### SuperGrok → Hermes (and the Grok apps)
- On the box: `docker exec -it hermes hermes auth add xai-oauth --no-browser` → open the printed
  link, approve. Then in any chat: `/model supergrok` (Grok 4.6) or `/model supergrok-build`
  (**Grok Build**, coding). The token refreshes itself.
- **Trap:** xAI restricts OAuth API access to some SuperGrok tiers. If you get `HTTP 403` after a
  successful login, it's the tier, not a bad token. Fall back to `/model grok` / `/model code`
  (Grok through OpenRouter) or add an `XAI_API_KEY`.
- The community `grok` CLI (`@vibe-kit/grok-cli`) takes an **API key**, not the subscription.

### Cursor → Cursor + Cursor CLI
- Install the CLI (laptop or server): `curl https://cursor.com/install -fsS | bash`
  (official installer; the npm package called `cursor-agent` is **not** Cursor's).
- Log in: `cursor-agent login` (on the server: `NO_OPEN_BROWSER=1 cursor-agent login` and open
  the printed URL), or create a key at <https://cursor.com/dashboard/api> and set
  `CURSOR_API_KEY`. Usage counts against your Cursor plan.

### Perplexity Pro + Comet
- Both are apps (Comet is Perplexity's browser, desktop). Nothing to install on the server.
- For Perplexity inside Hermes/agents use the router's `perplexity-*` models / `/model search`
  (via OpenRouter, pay per use), or a separate Perplexity **API** key from
  <https://www.perplexity.ai/account/api> if you'd rather bill Perplexity directly.

## Where to run what

- **Your laptop:** Claude Code, Codex, Gemini CLI, Cursor, Antigravity, Comet — the subscription
  logins are browser-based and simplest here.
- **The server:** Hermes (24/7 chat bot), the router, n8n. Put CLIs there only when you want them
  running unattended; use the headless logins above.
- **Cost control:** subscription tools stop at their plan limits (no surprise bill). API-key
  paths (router, Hermes with API keys) are pay-per-use: set a spend limit on OpenRouter
  (<https://openrouter.ai/settings/credits>) and on each provider console.
