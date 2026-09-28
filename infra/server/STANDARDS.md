# Aurora standards: dependencies, requirements, and what "current" means

What aurora-01 assumes, and the tools/versions we hold to. Versions move — treat the pins as
"known-good as of 2026-09", and re-check upstream before bumping. The rule everywhere is
**pin what's internet-facing or holds the Docker socket; track `latest` only for throwaways.**

## Host requirements
- **OS:** Ubuntu 24.04 LTS (what `cloud-init.yaml` provisions). 26.04 works but isn't tested with these scripts.
- **CPU/RAM/disk:** the CX33 (4 vCPU / 8 GB / 80 GB) is the floor for the core stacks **staged** (start one at a time; `aurora up`). Running Ollama or the computer-use desktop at the same time as OpenBot needs 16 GB (CX43) — the scripts warn when RAM is tight.
- **Docker Engine + Compose v2**, from get.docker.com. `aurora maintain tune` sets log rotation + live-restore and a 4 GB swap file.
- **Networking:** every service binds `127.0.0.1`; the only way in is Tailscale (`tailscale serve`, never Funnel). The provider firewall allows SSH + UDP 41641 only, and SSH is closed once Tailscale works.

## Terminal (server + phones)
- **Shell:** zsh on the phones, fish for the `aurora` user on the box (both provisioned).
- **Multiplexer:** tmux (sessions survive disconnects). On flaky mobile data use **mosh** over ssh.
- **Modern CLI set** (baked by cloud-init / `setup-tools.sh`): `fzf ripgrep fd bat eza zoxide jq btop ncdu duf`.
- **Editor:** neovim on the phones; on the box, edit in the agent or via Dockge's web editor.
- **From Android:** Termux (+ Termux:API, :Widget, :Boot) is the primary terminal; RDP (Windows App / aRDP) for the desktop. See `server/README.md`.

## Agent runtimes (the "agent OS")
| Tool | Pin / source | Notes |
|---|---|---|
| **Node.js** | 22 LTS (NodeSource) | runtime for the npm CLIs + MCP servers |
| **Claude Code** | `@anthropic-ai/claude-code` (npm, latest) | your Claude login; MCP via `~/work/.mcp.json` |
| **OpenCode** | `opencode-ai` (npm) | models via the router; config in `~/.config/opencode` |
| **n8n MCP** | `n8n-mcp@2.89.0` | authors/validates workflows; reviewed-version pin |
| **Playwright MCP** | container `mcr.microsoft.com/playwright/mcp:v0.0.82` (the shared browser at `127.0.0.1:8931/mcp`); `npx @playwright/mcp@0.0.78` in `mcp/.mcp.json.example` for an operator-side stdio fallback | bump each deliberately |
| **uv / uvx** | latest | runs Python MCP servers (e.g. docker-mcp) |

MCP config schemas differ per client (see `AGENTS.md`): Claude Code uses `.mcp.json`
(`${VAR}`), OpenCode uses `opencode.json` (`{env:VAR}`). Don't hand the same file to both.

## Container images (pinned where it matters)
| Stack | Image | Pin policy |
|---|---|---|
| router | `ghcr.io/berriai/litellm:main-stable` | vendor's stable channel (not `:latest`); versioned tags exist but this is the maintained internet-facing pin |
| n8n | `docker.n8n.io/n8nio/n8n:${N8N_IMAGE_TAG:-2.41.3}` | **pin `N8N_IMAGE_TAG`** to the running version (`docker exec n8n-n8n-1 n8n --version`); upgrades are a dump/restore when the DB major changes |
| postgres | `postgres:16-alpine` | n8n now recommends 17 — migrate deliberately (see server/README known issues) |
| hermes | `nousresearch/hermes-agent:${HERMES_TAG:-v2026.9.24}` | **pin for production**; desktop build via `HERMES_TAG=latest-desktop` |
| openbot | `ghcr.io/copilotkit/openbot:v0.0.15` | pinned |
| dashboard | `ghcr.io/gethomepage/homepage:v1.4.0` | pinned |
| admin (Dockge) | `louislam/dockge:1.4.1` | pinned; holds the Docker socket — review before bumping |
| assistant | `nginx:1.27-alpine` | static only |
| monitoring | `louislam/uptime-kuma:1`, `amir20/dozzle:v11.1.2`, `henrygd/beszel:0.20.0` (+agent), `binwiederhier/ntfy:v2.28.0` | all pinned; Kuma major-pinned |
| tailscale | `tailscale/tailscale:${TS_TAG:-v1.102.5}` | pinned; host network + `NET_ADMIN` |
| computer | `playwright/mcp:v0.0.82`, `anthropic-quickstarts:computer-use-demo-5264b72` | pinned (SHA tag = `-latest` by digest on 2026-09-28) |
| n8n proxy (opt-in) | `caddy:2.11.4-alpine` | pinned; only under `--profile public` |
| activepieces (opt-in) | `activepieces/activepieces:0.92.0` | pinned |
| ondemand / ollama | `:latest` / rolling | throwaway, on-demand profiles — acceptable per the rule above |
| agents (OpenHands) | `…/openhands:${OPENHANDS_TAG:-latest}` (+ runtime) | opt-in, **separate disposable box** — holds writable `docker.sock`; pin `OPENHANDS_TAG` on that box (release unverifiable from here) |

Bump with `aurora maintain upgrade <stack>` (it backs up first and recreates only what's running).

## Security baseline
- Secrets live in `/opt/aurora/secrets.env` (root, mode 600) and are fanned into per-stack `.env` by `stacks-up.sh` — **never printed, never committed** (only `*.example` is tracked).
- Provider API tokens (Hetzner/Hostinger) never leave the phone.
- **Client PII → paid model chains only, never a `-free` chain.** The router's `check-chains.py` keeps uncensored models out of the default chains.
- Backups nightly (`aurora maintain backup`), 7 kept on-box; copy them off-box too.
