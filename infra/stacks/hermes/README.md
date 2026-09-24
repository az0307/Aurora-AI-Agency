# Hermes Agent — one agent in Telegram, Discord, Slack and WhatsApp

[Hermes Agent](https://github.com/NousResearch/hermes-agent) (Nous Research) is a
self-hosted agent with built-in chat gateways. Here it's wired so that:

- **Brain** = the LiteLLM router on this box (`../router`). Model choice, fallbacks,
  free models, Grok, Hermes and Hugging Face models are all picked there.
- **Tools** = its own shell/web/file tools **plus Composio** (1000+ apps over MCP).
- **Reach** = Telegram, Discord, Slack, WhatsApp. All four connect *outbound*, so the
  box needs **no open ports and no public URL**.

## Start

Needs the router running first (`../router`).

```sh
cd /opt/aurora/stacks/hermes
mkdir -p data/workspace
cp config.yaml.example data/config.yaml
cp .env.example data/.env && chmod 600 data/.env
$EDITOR data/.env          # ROUTER_API_KEY + the platforms you want (below)
docker compose up -d
docker compose logs -f gateway
```

`ROUTER_API_KEY` is the router's `LITELLM_MASTER_KEY`.

## Platforms (fill only the ones you want)

**Always set the `*_ALLOWED_USERS` line for each platform** and leave
`GATEWAY_ALLOW_ALL_USERS=false`. The bot can run commands, so an open bot means anyone
who finds it can use your API credits and your tools.

| Platform | Get the token | Your user id | Notes |
|---|---|---|---|
| **Telegram** | @BotFather → `/newbot` | message @userinfobot | Easiest; start here. |
| **Discord** | [Developer Portal](https://discord.com/developers/applications) → New App → Bot → token; turn on **Message Content Intent**; invite with the OAuth2 URL (`bot` + `applications.commands`) | Developer Mode → right-click yourself → Copy ID | `DISCORD_REQUIRE_MENTION=true` so it only answers when @mentioned in servers. |
| **Slack** | `docker exec -it hermes hermes gateway setup` → pick Slack → it prints an **app manifest**; create the app from it, install, copy `xoxb-` bot token and `xapp-` app token | profile → ⋮ → Copy member ID | Socket Mode: no public URL. |
| **WhatsApp (quick)** | set `WHATSAPP_ENABLED=true`, then `docker exec -it hermes hermes whatsapp` and scan the QR in WhatsApp → **Linked devices** | your number, digits only (`61412345678`) | Unofficial WhatsApp Web bridge → small risk of the number being restricted. **Use a spare number, never a client's.** |
| **WhatsApp (official)** | WhatsApp Business **Cloud API** via a Meta app | — | Stable and allowed, but needs a **public webhook URL** → expose only that path with Tailscale Funnel or a Cloudflare Tunnel. Use this for anything client-facing. |

After editing `data/.env`: `docker compose restart gateway`.

## Models

In any chat, `/model <alias>` switches the brain for that conversation. Each alias is a
chain in `../router/config.yaml`, **curated by job: best model first**, then fallbacks
that only answer if the one before is down or erroring.

| Alias | Job | Chain (best → fallback) | Data |
|---|---|---|---|
| *(default)* `general` | everyday | Claude Sonnet 5 → GPT-5.6 Sol → Kimi Code → DeepSeek V4.1 Flash | paid-only, safe for client details |
| `free` | everyday, $0 | Nemotron 3 Ultra → Inkling → Qwen3.8-27B → Gemma 4 → OpenRouter free | **non-sensitive only** |
| `code` | coding | Claude Sonnet 5 → Grok Build → Kimi K2.7 Code → DeepSeek V4 Pro | paid-only |
| `code-free` | coding, $0 | North Mini Code → Laguna S 2.1 → Qwen3.8-27B → Nemotron | **non-sensitive only** |
| `reason` | hard problems, plans, reviews | Claude Opus 5.5 → GPT-5.6 Sol → Kimi K3 → DeepSeek V4 Pro | paid-only |
| `fast` | cheap bulk work | DeepSeek V4.1 Flash → MiniMax M3 → Gemini 3.8 Flash → Qwen Flash | paid-only |
| `vision` | photos, screenshots, video | Gemini 3.8 Flash → Claude Sonnet 5 → GPT-5.6 Sol | paid-only |
| `search` | current facts, with sources | Perplexity Sonar Pro → Sonar | paid-only |
| `research` | a researched report (slow) | Sonar Deep Research → Sonar Reasoning Pro → Sonar Pro | paid-only |
| `hermes` | Nous models | Hermes 4 405B → HF Hermes 3 70B | paid-only |
| `grok`, `opus` | direct | Grok 4.7, Claude Opus 5.5 | paid-only |
| `supergrok`, `supergrok-build` | on your SuperGrok plan | Grok 4.6 / Grok Build | after `hermes auth add xai-oauth --no-browser` (see [SUBSCRIPTIONS.md](../../SUBSCRIPTIONS.md)) |

Hermes' own side jobs also use the router (`auxiliary:` in the config): pictures go to
`vision`, and context compression, chat titles and the **curator** go to `fast`, so they
don't burn the main model.

**Curator** = Hermes' built-in librarian for the skills the agent writes for itself.
Weekly, when the bot is idle, it archives skills nobody used for 30 days and (with
`consolidate: true`, set here) merges near-duplicates. It never deletes; `/curator status`,
`hermes curator rollback` undoes a run.

To change a chain, edit `../router/config.yaml` and run `check-chains.py` there.

## Plugins and skills (expansions)

Turned on in the config: **disk-cleanup** (removes the agent's temp files after each
session) and **security-guidance** (warns when the agent writes risky code). Add more
from a phone over SSH:

```sh
h() { docker exec -it hermes hermes "$@"; }
h plugins list                     # installed / enabled
h plugins search memory            # the reviewed plugin catalog
h plugins install <name> --enable
h skills browse --source official  # optional skills from Nous
h skills install <identifier>
docker compose restart gateway     # pick up changes
```

Worth adding here:

| What | Command | Gives the bot |
|---|---|---|
| Claude Code skill *(bundled)* | already on | hand coding jobs to Claude Code on the box |
| Codex / OpenCode skills *(bundled)* | already on | same, for those CLIs |
| Google Workspace skill *(bundled)* | already on; first use walks you through Google sign-in | Gmail, Calendar, Drive, Docs, Sheets |
| Grok skill | `h skills install official/autonomous-ai-agents/grok` | Grok CLI as a sub-agent |
| Antigravity CLI skill | `h skills install official/autonomous-ai-agents/antigravity-cli` | Google's Antigravity CLI as a sub-agent |
| Memory provider | `h memory` (Honcho, Mem0, Supermemory…) | long-term memory beyond the built-in notes |
| Langfuse | `h plugins enable observability/langfuse` + keys | a trace of every model call and tool, with cost |

## Browser and computer use

- **Built-in browser** (headless, always there): the bot can browse, click and extract.
- **Playwright MCP** (`../computer`, wired in as `mcp_servers.playwright`): a shared
  Chromium whose logins persist. Start that stack first.
- **Desktop Commander MCP**: file editing, search and long-running terminal sessions
  inside this container. First use downloads it with `npx` (~20 s).
- **The bot's own desktop** (`computer_use`, "Bot Screen"): a Linux desktop + visible
  browser the bot drives by screenshot. Needs the bigger image:
  ```sh
  printf 'HERMES_TAG=latest-desktop\nHERMES_MEM=3g\n' >> .env   # ./.env here, not data/.env
  docker compose up -d
  docker exec -it hermes hermes computer-use install   # once: the cua driver
  docker exec -it hermes hermes computer-use doctor
  ```
  It starts on first use and stops after 30 idle minutes. Watching it live needs the
  Hermes Desktop app on a computer; from a phone, use the `../computer` desktop instead.

## Long-running and background work

The bot doesn't stop after one reply. It keeps going on a task while it's making progress
(up to 500 tool steps; it only gives up after **2 hours with no activity**,
`agent.gateway_timeout`). Long commands run as background processes that it checks on.

| You want | Send in chat |
|---|---|
| keep working until something is done (a judge model checks after each step; 20-step budget) | `/goal get the Y.M.I site passing Lighthouse ≥ 90` |
| repeat a check every N minutes in this chat | `/loop 30m check the n8n executions for errors` |
| nudge an idle chat on a timer | `/heartbeat every 10m check the deployment` |
| a scheduled job that reports back | `/cron add "0 7 * * *" "summarise yesterday's new leads" --name "Lead digest" --deliver telegram` |
| see / stop scheduled jobs | `/cron list` · `/cron remove <id>` |

Set `TELEGRAM_HOME_CHANNEL` in `data/.env` so scheduled results have somewhere to go.
Cron times use the container clock (UTC by default): 7 am Brisbane is `0 21 * * *`, or
add `TZ=Australia/Brisbane` to `data/.env`.
Jobs survive reboots; missed runs catch up (`cron.catch_up_missed`).

## Unrestricted mode

By default approvals are `smart`: a model auto-approves harmless commands, blocks clearly
dangerous ones, and asks you (a yes/no button in the chat) only when unsure.

- **This chat only:** send `/yolo` (send it again to turn it off). No prompts at all.
- **Always:** `approvals.mode: off` in `data/config.yaml`, then restart.

Either way the bot is still fenced inside its container: no Docker socket, no host
files outside `./data`. What it *can* reach is everything in `data/.env` (your API keys)
and the internet, so a web page with hidden instructions could try to make it misuse
them. Keep the chat allowlist tight, and prefer `/yolo` per task over `off` forever.

## Composio

1. [composio.dev](https://composio.dev) → **Connect** → create a **consumer key** →
   `COMPOSIO_CONSUMER_KEY` in `data/.env`.
2. Restart the gateway. Ask for something in an app ("add a row to my Leads sheet"). The
   first time, Composio replies with a link to authorize that app; open it on your phone.

## Dashboard

Loopback-only on port 9119 (it holds API keys). Over Tailscale:
`tailscale serve --bg --https=9119 http://127.0.0.1:9119`, or over SSH:
`ssh -L 9119:127.0.0.1:9119 aurora@<box>`.

## Ports it uses (host networking)

Hermes shares the host's network, so these must stay free on the box:

| Port | What | Clash to avoid |
|---|---|---|
| 9119 | dashboard (loopback) | — |
| 3000 | WhatsApp Web bridge (loopback, only when `WHATSAPP_ENABLED=true`) | **Dokploy and OpenBot also want 3000** — don't run them on this box with WhatsApp on. The bridge tries to take the port back if something holds it. |
| 8095 | WhatsApp **Cloud** webhook, if used (set `WHATSAPP_CLOUD_WEBHOOK_PORT=8095`) | default 8090 = Beszel |

## Resource use

About 0.5–1.5 GB RAM (capped at 1.5 GB + 0.5 GB for the dashboard in the compose file).
Pin `HERMES_TAG` to a release instead of `latest` once it works.
