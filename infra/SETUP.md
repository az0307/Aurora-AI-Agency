# Setup — every step, in order, with the exact links

Everything is already configured in this repo. What's left is creating accounts/keys (only
you can) and pasting them into **one file**: `infra/secrets.env`.

```sh
cd infra && cp secrets.env.example secrets.env   # then fill it in as you go below
```

Tick each box as you go. Skip anything you don't want; blank keys just leave that part off.

---

## 1. The server (≈AUD $28–39/mo, capped)

- [ ] **Hetzner account + project** → <https://console.hetzner.com/> → *New project* → name it `aurora`.
- [ ] **API token** → in the project: *Security → API tokens → Generate API token* → **Read & Write**
      → paste into `HCLOUD_TOKEN=`.
- [ ] **SSH key** (on *your* computer, once):
      ```sh
      ssh-keygen -t ed25519 -C "aurora"       # press Enter through the prompts
      ```
- [ ] **Dry run** (creates nothing, shows the real monthly price vs your $39 cap):
      ```sh
      ./bootstrap.sh --dry-run
      ```
- [ ] **Create it:** `./bootstrap.sh` → type `y` at the price prompt.
      Then `ssh aurora@<the IP it prints>`.

## 2. AI model keys (the router uses whichever you set)

| Key | Get it here | Paste into | Notes |
|---|---|---|---|
| OpenRouter | <https://openrouter.ai/settings/keys> | `OPENROUTER_API_KEY` | **Most important.** Covers free models, Grok Build, Hermes 4, Perplexity, DeepSeek, Kimi, GLM, MiniMax, Qwen, uncensored models. Add $10 credit. |
| Anthropic (Claude) | <https://console.anthropic.com/settings/keys> | `ANTHROPIC_API_KEY` | The paid-only `auto` chain for client work. |
| Hugging Face | <https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained> | `HF_TOKEN` | **Pre-filled link**: the "Make calls to Inference Providers" permission is already ticked; just name it `aurora` and create. |
| Gemini | <https://aistudio.google.com/apikey> | `GEMINI_API_KEY` | For the Gemini CLI. |
| xAI (Grok) | <https://console.x.ai/> → API Keys | `XAI_API_KEY` | Optional; Grok already works through OpenRouter. A SuperGrok subscription is the chat app, **not** API credit. |
| Kimi Code | <https://www.kimi.com/code> → console → API key | `KIMI_API_KEY` | Optional (`kimi-cheap`). Kimi also works via OpenRouter. |
| Groq (voice) | <https://console.groq.com/keys> | `GROQ_API_KEY` | Optional: faster Whisper. Blank = free local Whisper. |

## 3. Chat apps (Hermes answers you in all of them)

Do Telegram first — it's 2 minutes.

### Telegram
- [ ] Open <https://t.me/BotFather> → send `/newbot`
  - name: `Aurora Assistant`
  - username: `aurora_<yourname>_bot` (must end in `bot`)
  - copy the token → `TELEGRAM_BOT_TOKEN=`
- [ ] Open <https://t.me/userinfobot> → send `/start` → copy the number → `TELEGRAM_ALLOWED_USERS=`

### Discord
- [ ] <https://discord.com/developers/applications> → **New Application** → `Aurora Assistant`
- [ ] **Bot** tab → *Reset Token* → copy → `DISCORD_BOT_TOKEN=`; on the same page turn on
      **Message Content Intent** → Save.
- [ ] **General Information** → copy *Application ID*, put it in this link and open it to add the bot
      to your server (permissions are pre-filled: read/send, threads, files, reactions, slash commands):
      ```
      https://discord.com/oauth2/authorize?client_id=PASTE_APPLICATION_ID&scope=bot+applications.commands&permissions=311385246784
      ```
- [ ] Your user id: Discord *Settings → Advanced → Developer Mode* on, then right-click your name →
      *Copy User ID* → `DISCORD_ALLOWED_USERS=`

### Slack
- [ ] **One-click, pre-filled app** (name, scopes, events and Socket Mode already set) —
      open, pick your workspace, **Next → Create**:
      [Create the Aurora Slack app](https://api.slack.com/apps?new_app=1&manifest_json=%7B%22_metadata%22%3A%7B%22major_version%22%3A1%2C%22minor_version%22%3A1%7D%2C%22display_information%22%3A%7B%22name%22%3A%22Aurora%20Assistant%22%2C%22description%22%3A%22Aurora%20AI%20Agency%27s%20assistant%20%5Cu2014%20ask%20it%20anything%2C%20or%20send%20a%20voice%20note.%22%2C%22background_color%22%3A%22%231a1a2e%22%7D%2C%22features%22%3A%7B%22app_home%22%3A%7B%22home_tab_enabled%22%3Afalse%2C%22messages_tab_enabled%22%3Atrue%2C%22messages_tab_read_only_enabled%22%3Afalse%7D%2C%22bot_user%22%3A%7B%22display_name%22%3A%22Aurora%20Assistant%22%2C%22always_online%22%3Atrue%7D%2C%22agent_view%22%3A%7B%22agent_description%22%3A%22Chat%20with%20Hermes%20in%20Slack%20Messages.%22%7D%7D%2C%22oauth_config%22%3A%7B%22scopes%22%3A%7B%22bot%22%3A%5B%22app_mentions%3Aread%22%2C%22assistant%3Awrite%22%2C%22channels%3Ahistory%22%2C%22channels%3Aread%22%2C%22chat%3Awrite%22%2C%22commands%22%2C%22files%3Aread%22%2C%22files%3Awrite%22%2C%22groups%3Ahistory%22%2C%22groups%3Aread%22%2C%22im%3Ahistory%22%2C%22im%3Aread%22%2C%22im%3Awrite%22%2C%22mpim%3Ahistory%22%2C%22mpim%3Aread%22%2C%22reactions%3Aread%22%2C%22users%3Aread%22%5D%7D%7D%2C%22settings%22%3A%7B%22event_subscriptions%22%3A%7B%22bot_events%22%3A%5B%22app_context_changed%22%2C%22app_home_opened%22%2C%22app_mention%22%2C%22message.channels%22%2C%22message.groups%22%2C%22message.im%22%2C%22message.mpim%22%2C%22reaction_added%22%2C%22reaction_removed%22%5D%7D%2C%22interactivity%22%3A%7B%22is_enabled%22%3Atrue%7D%2C%22org_deploy_enabled%22%3Afalse%2C%22socket_mode_enabled%22%3Atrue%2C%22token_rotation_enabled%22%3Afalse%7D%7D)
- [ ] *Basic Information → App-Level Tokens → Generate* with scope `connections:write` → copy the
      `xapp-…` token → `SLACK_APP_TOKEN=`
- [ ] *Install App → Install to Workspace* → copy the `xoxb-…` token → `SLACK_BOT_TOKEN=`
- [ ] Your member id: your profile → **⋮** → *Copy member ID* → `SLACK_ALLOWED_USERS=`
- [ ] Optional — Hermes' 50 slash commands (`/model`, `/stop`, …): *Features → App Manifest* →
      paste [`stacks/hermes/slack-manifest.json`](./stacks/hermes/slack-manifest.json) → Save → reinstall.

### WhatsApp
- [ ] Put your number (digits, country code, e.g. `61412345678`) in `WHATSAPP_ALLOWED_USERS=`,
      and set `WHATSAPP_ENABLED=true` in Hermes' `data/.env` (it's off by default).
- [ ] After the server is up (step 6): `docker exec -it hermes hermes whatsapp` → on your phone,
      WhatsApp → **Settings → Linked devices → Link a device** → scan the QR.
      Use a **spare number** — this bridge is unofficial and can get a number restricted.

## 4. App integrations

- [ ] **Composio** (1000+ apps): <https://platform.composio.dev/> → sign up → **Connect** →
      create a *consumer key* → `COMPOSIO_CONSUMER_KEY=`
- [ ] **Zapier** (9,000+ apps, reuses your existing Zapier app logins): <https://mcp.zapier.com/> →
      **+ New MCP Server** → client **Other** → name `Aurora Hermes` → **Connect** tab →
      **Generate token** (shown once) → `ZAPIER_MCP_TOKEN=`. Then add the actions you want
      (e.g. Gmail *Send Email*, Google Sheets *Create Row*) on the same page.
  - (Your *Claude* Zapier server is separate — manage it at
    <https://mcp.zapier.com/mcp/servers/96cad99a-e273-412b-a97a-1aa5a2d4f86b/config>.)

- [ ] **GitHub** (optional, lets Hermes/Claude work on your repos):
      <https://github.com/settings/personal-access-tokens/new> → fine-grained, only the repos you
      want → `GITHUB_PAT=`
- [ ] **More MCP tools** (Desktop Commander on your laptop, Context7, Hugging Face, Notion, …):
      see [mcp/README.md](./mcp/README.md).

## 5. Private access (Tailscale)

- [ ] Install Tailscale on your phone + laptop: <https://tailscale.com/download> → sign in.
- [ ] <https://login.tailscale.com/admin/settings/keys> → **Generate auth key** → tick
      **Pre-approved** → copy → `TS_AUTHKEY=`
- [ ] <https://login.tailscale.com/admin/dns> → enable **MagicDNS** and **HTTPS Certificates**.

## 6. Ship the keys and start everything

From your computer (re-running is safe — it reuses the same server):
```sh
./bootstrap.sh          # copies secrets.env to the box
ssh aurora@<IP>
```
On the box, start the stacks **in this order** (each folder's README has details):
```sh
cd /opt/aurora/stacks
# a) router (creates the shared network the others use)
cd router && cp config.yaml.example config.yaml && cp .env.example .env && nano .env && docker compose up -d && cd ..
# b) n8n — first uncomment the two `ports:` / `127.0.0.1:5678:5678` lines in docker-compose.yml
#    (so Tailscale can reach it). In .env set N8N_HOST=aurora-01.<your-tailnet>.ts.net,
#    N8N_PROTOCOL=https, WEBHOOK_URL=https://aurora-01.<your-tailnet>.ts.net/  (your tailnet
#    name is on https://login.tailscale.com/admin/dns). Only the `postgres n8n` services start;
#    Caddy isn't needed with Tailscale.
cd n8n && cp .env.example .env && nano .env && docker compose -f docker-compose.yml up -d postgres n8n && cd ..
# c) Hermes (the bot)
cd hermes && mkdir -p data/workspace && cp config.yaml.example data/config.yaml \
  && cp .env.example data/.env && chmod 600 data/.env && nano data/.env && docker compose up -d && cd ..
# d) Tailscale
cd tailscale && cp .env.example .env && nano .env && docker compose up -d && cd ..
# e) monitoring (Uptime Kuma + log viewer only; Beszel needs its own key first)
cd monitoring && docker compose up -d uptime-kuma dozzle && cd ..
```
In each `nano`, copy the matching values from `/opt/aurora/secrets.env`
(`sudo cat /opt/aurora/secrets.env`). For Hermes, `ROUTER_API_KEY` = the router's
`LITELLM_MASTER_KEY` — make one with:
`python3 -c "import secrets;print('sk-'+secrets.token_urlsafe(32))"`

## 6b. Plug in the subscriptions you already pay for

Claude, ChatGPT, Google AI Pro, SuperGrok and Cursor each work through their own tool/login,
not an API key. [SUBSCRIPTIONS.md](./SUBSCRIPTIONS.md) has the exact steps and the traps:
- **SuperGrok in Hermes:** `docker exec -it hermes hermes auth add xai-oauth --no-browser` →
  then `/model supergrok` or `/model supergrok-build` in any chat.
- **ChatGPT in Hermes:** `docker exec -it hermes hermes model` → "ChatGPT or Codex Subscription".
- **Claude Code / Codex / Gemini CLI / Cursor CLI / Antigravity:** on your laptop, logged in with
  each plan's account.

## 6c. Your phones

App lists per phone (F-Droid/GitHub), the Android background-kill fixes, Termux + tmux with
plugins, and home-screen buttons: **[phones/README.md](./phones/README.md)**.

## 7. Check it works

- [ ] Message your Telegram bot "hi" → it answers.
- [ ] Send it a **voice note** → it transcribes and acts on it (voice commands).
- [ ] Send `/model search` then "what's the weather in Melbourne?" → Perplexity answer with sources.
- [ ] "Add a row to my Leads sheet with name Test" → Composio/Zapier asks you to authorize once.
- [ ] Open `https://aurora-01.<your-tailnet>.ts.net` on your phone (after the `tailscale serve`
      lines in [stacks/tailscale/README.md](./stacks/tailscale/README.md)).

## 8. Lock it down (after it works)

- [ ] SSH in over Tailscale (`ssh aurora@aurora-01`) from a second terminal, then in Hetzner
      delete the SSH rule from firewall `aurora-01-fw` → zero public ports.
- [ ] Hetzner → *Billing* → set a **usage alert**.
- [ ] Revoke the Hetzner token you used for bootstrap if you won't re-run it.

---

**In your `/model` menu:** `auto` (default, paid, safe for client data) · `code` (Grok Build) ·
`cheap` · `free` · `hermes` · `search` (Perplexity) · `grok` · `opus`. Uncensored models are
call-by-name only — see [stacks/router/README.md](./stacks/router/README.md).
