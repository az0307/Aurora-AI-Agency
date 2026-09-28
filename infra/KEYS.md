# Keys & configs — your reference sheet

Every credential and config file the Aurora box uses: what it is, where you get it, whether
you need it, and where it ends up. **This file holds names only, never values.**

> ⚠️ **Never type a real key into this file, or any file in this repo.** The repo may be public
> (making it private is still on the to-do list, T015). Real values live in exactly two places:
> **Bitwarden** (the master copy) and **`secrets.env`** (on your phone, git-ignored, mode 600).

## How a key travels

```
Bitwarden folder "Aurora"          one item per key, item name = the variable name
   │  (e.g. item "OPENROUTER_API_KEY")
   ▼  aurora-secrets fill            on the phone: pulls the folder into secrets.env
infra/secrets.env  (phone, 600)    the ONE credentials file; template: secrets.env.example
   │
   ▼  ./bootstrap.sh --ship-only     copies it to the box (an allowlist: provider tokens never leave the phone)
/opt/aurora/secrets.env (box, 600)
   │
   ▼  stacks-up.sh <stack>           fills that stack's .env from it; values never printed
stacks/<stack>/.env                 (hermes: stacks/hermes/data/.env)
```

Change a key → update Bitwarden → `aurora-secrets fill` → `./bootstrap.sh --ship-only` →
`aurora start <stack>` on the box (re-writes that stack's `.env` and recreates it).
**Not** `aurora restart` — that's a plain `docker compose restart`, which keeps the *old* key.

**Required?** column: **Yes** = the stack refuses to start without it · **Needed** = starts, but
the feature doesn't work · **Optional** = extra, skip freely · **Auto** = made for you, don't set.

---

## 1. Provider tokens — stay on your phone, never shipped to the box

| Key | For | Required? | Get it | Lands in |
|---|---|---|---|---|
| `HCLOUD_TOKEN` | creating/managing the Hetzner server (`bootstrap.sh`) | Yes (Hetzner) | console.hetzner.com → your project → Security → API tokens → **Read & Write** | phone `secrets.env` only |
| `HETZNER_API_TOKEN` | same token, name the Hetzner MCP reads | Auto | set to `${HCLOUD_TOKEN}` in the template | phone only |
| `HOSTINGER_API_TOKEN` | only if `VPS_PROVIDER=hostinger` | Yes (Hostinger) | hpanel.hostinger.com/profile/api | phone only |

Non-secret box settings in the same file: `VPS_PROVIDER` (hetzner/hostinger), `HOSTINGER_PLAN`,
`HOSTINGER_TERM`, `TZ` (Australia/Melbourne), `N8N_DOMAIN` (blank = tailnet/tunnel only).

## 2. Infra secrets — you generate these once, then keep them forever

Generate each once, save to Bitwarden, **never reuse** them anywhere else.

| Key | For | Required? | Make it with | Lands in |
|---|---|---|---|---|
| `LITELLM_MASTER_KEY` | the router's password; every agent/app uses it to call the router. **Must start with `sk-`** | Yes (router, hermes) | `python3 -c "import secrets; print('sk-' + secrets.token_urlsafe(32))"` | router `.env`; Hermes as `ROUTER_API_KEY`; OpenBot as `OPENAI_API_KEY`; agents' env via `aurora-agent` |
| `POSTGRES_PASSWORD` | n8n's database | Yes (n8n) | `openssl rand -hex 32` | n8n `.env` |
| `N8N_ENCRYPTION_KEY` | encrypts every credential saved inside n8n. **Lose it = all saved n8n credentials become unreadable.** Back it up | Yes (n8n) | `openssl rand -hex 32` | n8n `.env` |

## 3. Model providers — feed the router and the CLI agents

| Key | For | Required? | Get it | Lands in |
|---|---|---|---|---|
| `OPENROUTER_API_KEY` | almost every router chain (and all `-free` models) | **Needed** — without it nearly every chain fails | openrouter.ai/keys | router, hermes |
| `ANTHROPIC_API_KEY` | Claude hops in `general`/`code`/`reason`; computer-use desktop | Optional (chains skip to their 2nd model) | console.anthropic.com → API keys | router, computer |
| `KIMI_API_KEY` | router `kimi-cheap` hop | Optional | Kimi Code console | router |
| `GEMINI_API_KEY` | Gemini CLI (router reaches Gemini via OpenRouter anyway) | Optional | aistudio.google.com → API key | router |
| `HF_TOKEN` | Hugging Face router models + Hermes fallback | Optional | huggingface.co/settings/tokens | router, hermes |
| `XAI_API_KEY` | Grok CLI direct to xAI | Optional | console.x.ai | CLI agents |
| `OPENAI_API_KEY` | Codex CLI; OpenBot *only if* you want it to skip the router | Optional | platform.openai.com/api-keys | CLI agents (OpenBot uses the router key instead when blank) |
| `CURSOR_API_KEY` | Cursor CLI on the server | Optional | cursor.com/dashboard → API | CLI agents |

Subscriptions (Claude Pro/Max, ChatGPT, Google AI Pro, SuperGrok) mostly *log in* instead of
using a key — see `SUBSCRIPTIONS.md`. Claude Code on the box: `aurora-agent claude` → `/login`.

> 🔒 **Client data (e.g. Y.M.I Roofing leads) only ever on paid chains** (`general`, `code`,
> `reason`, …) — never a `-free` chain.

## 4. Hermes — chat apps and tools (`stacks/hermes`)

Hermes **starts without any of these**, but with no chat token nobody can talk to it. Each chat
platform needs **both** its token **and** its `*_ALLOWED_USERS`, or the bot ignores everyone.

| Key | For | Required? | Get it |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot | **Needed** (pick at least one chat app) | Telegram → @BotFather → `/newbot` |
| `TELEGRAM_ALLOWED_USERS` | who may talk to it | **Needed** with the token | your numeric id: message @userinfobot |
| `DISCORD_BOT_TOKEN` / `DISCORD_ALLOWED_USERS` | Discord bot | Optional | discord.com/developers → New app → Bot |
| `SLACK_BOT_TOKEN` (`xoxb-…`) / `SLACK_APP_TOKEN` (`xapp-…`) / `SLACK_ALLOWED_USERS` | Slack (Socket Mode) | Optional | api.slack.com/apps → from `stacks/hermes/slack-manifest.json` |
| `WHATSAPP_ALLOWED_USERS` | WhatsApp (digits with country code, e.g. `61412345678`) | Optional | pair in Hermes; its bridge uses port 3000 |
| `COMPOSIO_CONSUMER_KEY` | 1,000+ app tools via MCP | Optional | composio.dev → Connect → consumer key |
| `ZAPIER_MCP_TOKEN` | 9,000+ apps via Zapier MCP | Optional | mcp.zapier.com → server for "Other" → Generate token |
| `GITHUB_PAT` | GitHub MCP (Hermes + Claude Code) | Optional | github.com/settings/tokens → **fine-grained**, least privilege |
| `CONTEXT7_API_KEY` | docs MCP, higher limits | Optional | context7.com |
| `GROQ_API_KEY` | faster cloud Whisper for voice notes (blank = free local Whisper) | Optional | console.groq.com/keys |

Set automatically for Hermes: `ROUTER_API_KEY` (= `LITELLM_MASTER_KEY`). Hermes-only knobs in
`stacks/hermes/.env.example`: `GATEWAY_ALLOW_ALL_USERS` (keep false), `TELEGRAM_HOME_CHANNEL`,
`DISCORD_REQUIRE_MENTION`, `WHATSAPP_ENABLED`. Empty Zapier/HF/GitHub tokens make Hermes log an
`Authorization … whitespace` warning — harmless until you add them.

## 5. Apps and network

| Key | For | Required? | Get it | Lands in |
|---|---|---|---|---|
| `INTELLIGENCE_API_KEY` | OpenBot (the `cpk-…` key) | **Yes** (openbot) | `npx copilotkit@latest project select` | openbot `.env` |
| `KEY_ENCRYPTION_KEY` | OpenBot's local encryption key | Auto — generated on first `stacks-up.sh openbot`; **back up `stacks/openbot/.env`** (the nightly backup does) | — | openbot `.env` |
| `N8N_API_KEY` | lets OpenCode / Claude Code manage n8n workflows (n8n MCP) | Needed for agent→n8n | n8n → Settings → n8n API → Create key (after the owner account exists) | agents' env via `aurora-agent` |
| `TS_AUTHKEY` | Tailscale container (only if you use the `tailscale` stack instead of host Tailscale) | Yes (that stack) | login.tailscale.com → Settings → Keys → pre-approved | tailscale `.env` |

OpenBot routing is set for you: with `OPENAI_API_KEY` blank, `stacks-up.sh openbot` writes
`OPENAI_API_KEY=<router key>` and `OPENAI_BASE_URL=http://litellm:4000/v1` (router over the
`aurora-llm` Docker network). CopilotKit usage telemetry is **off** by default
(`COPILOTKIT_TELEMETRY_DISABLED=true`); set it to `false` in OpenBot's `.env` to opt in.

## 6. Per-stack keys you set by hand (not in `secrets.env`)

Opt-in stacks keep their own secrets in their own `.env` (copy the `.env.example`). Generate
passwords with `openssl rand -hex 32` and store them in Bitwarden too.

| Stack | Keys |
|---|---|
| `activepieces` | `AP_ENCRYPTION_KEY`, `AP_JWT_SECRET`, `AP_POSTGRES_PASSWORD` (+ `AP_FRONTEND_URL`, `AP_POSTGRES_DATABASE`, `AP_POSTGRES_USERNAME`) |
| `ondemand` | `BROWSER_TOKEN`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `SCRATCH_PG_PASSWORD` (+ `LT_LOAD_ONLY`) |
| `agents` (OpenHands, separate box) | `LLM_API_KEY`; pin `OPENHANDS_TAG` + `SANDBOX_IMAGE` |
| `ollama` | none secret (`WEBUI_AUTH` — keep true) |

## 7. Config files (settings, not secrets)

| In the repo | On the box | What it controls |
|---|---|---|
| `secrets.env.example` | `/opt/aurora/secrets.env` | the credentials list above |
| `stacks/router/config.yaml.example` | `/opt/aurora/stacks/router/config.yaml` | model chains/fallbacks. Run `stacks/router/check-chains.py` after editing |
| `stacks/hermes/config.yaml.example` | `/opt/aurora/stacks/hermes/data/config.yaml` | Hermes model, MCP servers, plugins, features (`FEATURES.md`) |
| `stacks/hermes/.env.example` | `/opt/aurora/stacks/hermes/data/.env` | Hermes secrets (filled by `stacks-up.sh`) |
| `stacks/openbot/.env.example` | `/opt/aurora/stacks/openbot/.env` | OpenBot image/port/URLs/keys |
| `stacks/n8n/.env.example` | `/opt/aurora/stacks/n8n/.env` | n8n version (`N8N_IMAGE_TAG`), DB, timezone, CORS |
| `stacks/dashboard/…` | `/opt/aurora/stacks/dashboard/` | Homepage start-page tiles |
| `server/opencode.json` | `~/.config/opencode/opencode.json` | OpenCode → router (`aurora/code`) + Playwright/n8n MCP |
| `server/claude-mcp.json` | `~/work/.mcp.json` | Claude Code's MCP servers (Playwright, n8n) |
| `mcp/.mcp.json.example` | (template) | all MCP servers, incl. **server-only** Docker MCP |
| `server/aurora`, `server/aurora-agent` | `/usr/local/bin/` | the menu, and the agent launcher that holds keys in the child env only |

Configs you've edited are never overwritten by an update — the new version lands next to them as `*.new`.

## 8. Where things are (all tailnet-only; everything binds `127.0.0.1`)

`https://aurora-01.<tailnet>.ts.net` + port:

| Port | What | Port | What |
|---|---|---|---|
| `/` (443) | n8n | 3020 | OpenBot |
| 8600 | Aurora Assistant panel | 9119 | Hermes dashboard |
| 3002 | Homepage start page | 5001 | Dockge (stacks GUI) |
| 3001 | Uptime Kuma | 4000 | LLM router (loopback only) |
| RDP | `100.75.44.47:3389` desktop | SSH | `ssh aurora-01` (tailnet) |

Full map: `SERVICES.md`.

## 9. Bring up Hermes + OpenBot on the box

Minimum keys: `LITELLM_MASTER_KEY`, `OPENROUTER_API_KEY`, `TELEGRAM_BOT_TOKEN` +
`TELEGRAM_ALLOWED_USERS`, `INTELLIGENCE_API_KEY`. Add them to Bitwarden, then:

```sh
# on the phone (Termux)
aurora-secrets fill && AURORA_HOST=aurora-01 ./bootstrap.sh --ship-only
# on the box (ssh aurora-01), in this order — the router first, both depend on it
aurora start router
aurora start hermes      # then message your bot on Telegram
aurora start openbot     # then open https://aurora-01.<tailnet>.ts.net:3020
bash /opt/aurora/check.sh
```

Memory: don't run OpenBot alongside Ollama or the computer-use desktop on the 8 GB box.

## 10. If a key leaks

1. Revoke it at the provider first (links above) and make a new one.
2. Update the Bitwarden item → `aurora-secrets fill` → `./bootstrap.sh --ship-only` → `aurora start <stack>`.
3. For `LITELLM_MASTER_KEY`: `aurora start` router, hermes and openbot, and relaunch any agent session.
4. **Don't rotate `N8N_ENCRYPTION_KEY`** casually — n8n can't read credentials saved under the
   old one. If it leaked: export workflows, rotate, then re-enter every n8n credential.
