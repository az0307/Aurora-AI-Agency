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

## GUIs

| GUI | Where | What for |
|---|---|---|
| **Aurora Assistant** | `https://aurora-01.<tailnet>.ts.net:8600` (desktop icon **Aurora Assistant**) | the go-to panel: a "send a task" box wired to n8n, plus one-tap into OpenBot, Hermes, n8n, OpenCode, router |
| **Start page (Homepage)** | `https://aurora-01.<tailnet>.ts.net:3002`: bookmark it on both phones | every link in one place, with a green dot per running container, plus CPU/RAM/disk |
| **Stacks GUI (Dockge)** | `https://aurora-01.<tailnet>.ts.net:5001` | start/stop/restart stacks, live logs, edit compose and `.env`, a shell in a container |
| **Desktop (XFCE over RDP)** | `100.75.44.47:3389` | the full desktop with the icons above: Firefox, terminal, file manager |
| **Docker TUI (lazydocker)** | `aurora` → docker | the same as Dockge, in the terminal (installed by `aurora maintain tune`) |

Start them with `aurora start dashboard` and `aurora start admin`. Each one also publishes
itself on the tailnet (`tailscale serve`, never Funnel). **Open Dockge straight away and create
its admin login.** Whoever opens it first becomes admin, and it holds the Docker socket, which
is root on this box.

## Android apps (what to use from the Reno / S10)

| Job | Best app | Why |
|---|---|---|
| Terminal / SSH | **Termux** (already set up) + `ssh aurora-01` or `mosh aurora-01` | full Linux tools, tmux, the phone kit, scripts; mosh survives flaky mobile data |
| Terminal, point-and-tap | **ConnectBot** (F-Droid, open source) | simple and free, if you don't want Termux for a quick look |
| Desktop (RDP) | **Windows App** (Microsoft, Play Store) | the smoothest RDP client for xrdp; add PC `100.75.44.47` |
| Desktop, open source | **aRDP** (F-Droid) | an RDP client without a Microsoft account |
| Web GUIs | any browser, with the start page bookmarked | n8n, OpenBot, Dockge, Uptime, router |

About **Haven**: I haven't verified an Android SSH client by that name, so I can't recommend it.
Termux + Tailscale does everything an SSH app does, plus the scripts in `phones/kit`.

## Maintenance (`aurora maintain …` = `server/maintain.sh`)

| Command | What it does |
|---|---|
| `tune` (once) | Docker log rotation (10 MB × 3) + live-restore · 4 GB swap, swappiness 10 · more inotify watches · journald capped at 300 MB · nightly backup timer (03:30) + weekly prune timer (Sun 04:15) · btop, ncdu, duf, lazydocker |
| `backup` | n8n Postgres dump (restore-tested) + every stack volume (each stack paused for a few seconds) + all `.env` files, `secrets.env`, Hermes data and Tailscale state → `/var/backups/aurora/<date>`, root-only, 7 kept |
| `prune` | removes images and build cache unused for 7+ days. **Never volumes.** |
| `upgrade <stack>` / `upgrade all` | backup, then pull + recreate **only the services that are running** (so n8n's Caddy or the on-demand desktop don't start by surprise) |
| `report` | `check.sh` + upkeep status (Docker tuning, swap, timers, last backup, tool versions, disk, anything listening off loopback). Safe to paste to Claude: no secret values |

Backups stay **on the box**, which protects against mistakes, not against losing the server.
Also copy them off: `scp -r aurora-01:/var/backups/aurora/<date> .` to the phone, or turn on
Hetzner's backup option (+20% of the server price). Off-box restic to object storage is on the to-do list.

## Tested (2026-09-27, staging copy of /opt/aurora on Docker 29.3)

Everything was started through `stacks-up.sh` exactly as on aurora-01:
- **Stacks:** router (74 models listed through `aurora-agent`), n8n + Postgres, Hermes + dashboard, Kuma + Dozzle, Playwright MCP, OpenBot, Homepage, Dockge. All healthy, all ports on `127.0.0.1` only.
- **OpenBot:** reaches the router over the `aurora-llm` network.
- **Backups:** the dump restored into a fresh Postgres (142 tables). No container is left paused after a backup.
- **`upgrade monitoring`:** recreated only Dozzle + Kuma.
- **`aurora` actions:** status, start, stop, restart, prune and links all work.
- **`tune`'s `daemon.json` merge:** keeps existing settings, and running it twice changes nothing.

Bugs found and fixed by this test:
- n8n crash-looped where Docker has no IPv6; it now listens on `0.0.0.0` (still loopback-published).
- OpenBot's healthcheck used a `wget` that isn't in the image, so it would never pass. It now uses `curl`.
- The report stopped at the first failed probe.
- `check.sh` wrongly failed when Tailscale runs on the host rather than as a container. It now also flags Funnel.
- The backup archived Hermes files twice and missed Dockge's data.

Not tested here:
- `tune` on a real systemd host.
- `tailscale serve` (no tailnet in the test).
- The XFCE icons.

## Known issues / to do

- **n8n on Postgres 16:** current n8n logs "Postgres 16 … compatibility support only. Upgrade to 17". That's a major-version change, so do it deliberately: `aurora maintain backup`, stop n8n, start a Postgres 17 container on a new volume, restore `n8n-postgres.sql.gz`, then switch. Don't just change the image tag, because 17 can't read 16's data files.
- **`N8N_IMAGE_TAG=latest`:** pin it to the version you're running (`docker exec n8n-n8n-1 n8n --version`) so an upgrade is a choice, not a surprise.
- **Hermes logs `Authorization … whitespace` warnings** for Zapier, Hugging Face and GitHub. The token is simply empty, and those MCP servers are `lazy`, so this is harmless until you add the keys.
- **During the 03:30 backup** a healthcheck can fail once while a stack is paused (Kuma may show a blip).

## Files here

| File | Installed to | |
|---|---|---|
| `setup-tools.sh` | — | one-time install (apt, adb, Node 22, OpenCode, Claude Code) + everything below |
| `maintain.sh` | — | `aurora maintain …`: tune, backup, prune, upgrade, report |
| `aurora` | `/usr/local/bin/aurora` | the menu |
| `aurora-agent` | `/usr/local/bin/aurora-agent` | runs an agent with `ROUTER_API_KEY` + `N8N_API_KEY` in **its own env only** (read from `/opt/aurora/secrets.env` via sudo; never written to disk) |
| `opencode.json` | `~/.config/opencode/opencode.json` | provider `aurora` → `http://127.0.0.1:4000/v1`, default model `aurora/code`. **v1 schema** (matches opencode.ai/docs). If `opencode --version` is v2, its schema differs (`providers`/`package: "aisdk:…"`/`settings`/`mcp.servers`) — or just run `opencode mcp add …`. Checked via Context7 2026-09-27. |
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
   aurora start hermes            # = stacks-up.sh hermes: re-writes its .env and recreates it
   aurora start openbot           # (not `aurora restart` — a plain restart keeps the old .env)
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
