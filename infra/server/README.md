# Operating aurora-01: menu, agents, OpenBot, Claude Code

Everything you need on the box, driven from one menu. Works over SSH from Termux (Reno/S10)
or in the RDP desktop (XFCE) with icons.

| Thing | What it is | How you open it |
|---|---|---|
| **`aurora`** | Menu (TUI): status, start/stop/restart a stack, logs, agents, health check, links, update | type `aurora` · RDP icon **Aurora Control** |
| **OpenCode** | Coding agent, models via the LiteLLM router, MCP: Playwright + n8n | `aurora` → opencode · icon **OpenCode** |
| **Claude Code** | Anthropic's agent (your Claude login), MCP: Playwright + n8n, plugins | `aurora` → claude · icon **Claude Code** |
| **Hermes** | The always-on agent (Telegram etc.) | `aurora` → hermes (chat in the terminal) · icon **Hermes dashboard** |
| **OpenBot** | CopilotKit OpenBot web app | `aurora start openbot` → `https://aurora-01.<tailnet>.ts.net:3020` |
| **n8n** | Workflows | `https://aurora-01.<tailnet>.ts.net/` (tailnet only) · icon **n8n** |

## Files here

| File | Installed to | |
|---|---|---|
| `setup-tools.sh` | — | one-time install (apt, Node 22, OpenCode, Claude Code) + everything below |
| `aurora` | `/usr/local/bin/aurora` | the menu |
| `aurora-agent` | `/usr/local/bin/aurora-agent` | runs an agent with `ROUTER_API_KEY` + `N8N_API_KEY` in **its own env only** (read from `/opt/aurora/secrets.env` via sudo; never written to disk) |
| `opencode.json` | `~/.config/opencode/opencode.json` | provider `aurora` → `http://127.0.0.1:4000/v1`, default model `aurora/code` |
| `claude-mcp.json` | `~/work/.mcp.json` | Claude Code's MCP servers when started in `~/work` (which `aurora-agent` does) |

Configs you've edited are never overwritten; a newer version lands next to them as `*.new`.

## Finish the setup (from where the box is now)

Public SSH is closed, so every step goes over Tailscale (`aurora-01`, or `100.75.44.47`).

1. **Get this code onto the box.** Pick either option:
   - *From the Reno:* `git pull`, then `AURORA_HOST=aurora-01 ./bootstrap.sh --ship-only`. This also ships `secrets.env`.
   - *On the box, straight from GitHub:*
     ```sh
     git clone -b claude/vps-hosting-strategy-0e9b5z https://github.com/az0307/Aurora-AI-Agency.git ~/Aurora-AI-Agency
     bash ~/Aurora-AI-Agency/infra/server/setup-tools.sh
     AURORA_BRANCH=claude/vps-hosting-strategy-0e9b5z aurora update
     ```
     After the PR merges, plain `aurora update` (which uses `main`) is enough. If you make the repo private, run `gh auth login` on the box first.
2. **Install the tools (first time):** `bash /opt/aurora/server/setup-tools.sh`
3. **RDP password:** `sudo passwd aurora`, then RDP to `100.75.44.47:3389` (tailnet only).
4. **n8n owner:** open `https://aurora-01.<tailnet>.ts.net/` and create the owner account. Then go to *Settings → n8n API → Create key*.
   - Put the key in `secrets.env` on the phone as `N8N_API_KEY`, then run `--ship-only`.
   - Agents pick it up next launch; nothing needs restarting.
5. **Keys for Hermes / OpenBot:** add these to `secrets.env` on the phone (from Bitwarden, using the hidden prompt), then run `--ship-only`:
   - `TELEGRAM_BOT_TOKEN` + `TELEGRAM_ALLOWED_USERS`
   - `ZAPIER_MCP_TOKEN`
   - `INTELLIGENCE_API_KEY` (the `cpk-…` key)

   Then on the box:
   ```sh
   aurora restart hermes          # or: bash /opt/aurora/stacks-up.sh hermes  (re-writes its .env)
   aurora start openbot
   ```
6. **Claude Code:** run `aurora-agent claude`.
   - Type `/login` and finish the link on your phone.
   - The first time, approve the two project MCP servers (`playwright`, `n8n`).
   - Type `/plugin` to browse and install plugins from marketplaces, `/mcp` to see server status.
   - The plugin marketplace for this repo will be `az0307/Aurora-AI-Agency` once the plugin work lands (`/plugin marketplace add az0307/Aurora-AI-Agency`).
7. **OpenCode:** run `aurora-agent opencode`.
   - `/models` lists the router chains.
   - `code` / `general` / `reason` are paid chains; `*-free` chains must **never** get client data (e.g. Y.M.I Roofing leads).

## OpenBot notes

- It listens on **127.0.0.1:3020**, because Kuma has 3001 and browserless 3010. `stacks-up.sh openbot` also publishes it on the tailnet with `tailscale serve --https=3020` (no Funnel).
- **Model:** it uses `OPENAI_API_KEY` if you've set one. Otherwise it goes through the router: `OPENAI_BASE_URL=http://litellm:4000/v1` over the router's private Docker network.
- **Auth:** single-user by default. Anyone who can reach it on your tailnet *is* you. That's fine while only your devices are on the tailnet; switch to OAuth before you share the tailnet with anyone.
- **Memory:** don't run it alongside Ollama or the computer-use desktop on the 8 GB box.

## Handing over from the Grok box

Once you're on OpenCode / OpenBot / Hermes here, remove the Grok box's access:
- Tailscale admin → remove the Grok machine (or expire its key).
- Delete its key from `~aurora/.ssh/authorized_keys` on aurora-01.
- Turn off Desktop Commander on the Grok box.

Nothing on aurora-01 depends on it.
