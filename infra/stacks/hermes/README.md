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

In any chat, `/model <alias>` switches the brain for that conversation:

| Alias | Router chain | Use for |
|---|---|---|
| *(default)* `auto` | Claude Sonnet 5 → Kimi → DeepSeek | anything that may contain client data (paid-only) |
| `code` | Grok Build → Kimi K2.7 Code → Claude | coding |
| `cheap` | DeepSeek V4.1 Flash → HF Qwen3.8-27B → free | bulk, non-sensitive |
| `free` | OpenRouter free router → Nemotron-3 Super → Qwen → Gemma | $0, non-sensitive only |
| `hermes` | Nous Hermes 4 405B → HF Hermes 3 70B | Hermes models |
| `search` | Perplexity Sonar Pro → Sonar | current facts, with sources |
| `grok`, `opus` | Grok 4.7, Claude Opus 5.5 | direct |
| `supergrok`, `supergrok-build` | Grok 4.6 / Grok Build **on your SuperGrok plan** | after `hermes auth add xai-oauth --no-browser` (see [SUBSCRIPTIONS.md](../../SUBSCRIPTIONS.md)) |

To change what an alias does, edit `../router/config.yaml`, not this stack.

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
