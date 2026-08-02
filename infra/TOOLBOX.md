# The toolbox — every app, tool, CLI, MCP, skill & dashboard on the box

One index of what runs on / is installed on the VPS, and where each is documented in
detail. If a thing has its own file, this just points at it — no duplication.

## Dashboards & headless management (the control surfaces)

All bind loopback and sit behind **Cloudflare Access** — never public. Full detail +
port map in [`SERVICES.md`](./SERVICES.md).

| App | Role | Port | Notes |
|---|---|---|---|
| **Dokploy** | the control plane — deploy/rollback/logs/TLS, Git deploys | 3000 | primary headless management app |
| **Homepage** | single start-page over every service, with live widgets | 3002 | your "one link to everything" |
| **Beszel** | lightweight metrics (CPU/RAM/disk/containers) | 8090 | |
| **Uptime Kuma** | uptime checks + public status page | 3001 | |
| **Dozzle** | live container logs in the browser | 8080 | |
| **ntfy** | push alerts to your phone | 8888 | wire Beszel/Kuma → ntfy |
| **Portainer** *(optional)* | classic container manager, if you prefer it to Dokploy | — | add only if you want it; Dokploy already covers most of this |

## CLIs to keep installed

Baked by [`hetzner/cloud-init.yaml`](./hetzner/cloud-init.yaml) or added day-1. Confirm
package names at install time — they move.

| CLI | Install | For |
|---|---|---|
| **git** | `apt install git` | version control (already assumed everywhere) |
| **GitHub CLI (`gh`)** | `apt install gh` | PRs/issues/releases from the box; `gh auth login` |
| **Gemini CLI** | `npm i -g @google/gemini-cli` | Google's terminal agent — cheap fallback in the failover chain (see [`AGENTS.md`](./AGENTS.md)) |
| **Bitwarden CLI (`bw`)** | `npm i -g @bitwarden/cli` | official secrets CLI; `bw unlock` → `BW_SESSION`; pull creds into env at deploy time |
| **rbw** *(alt)* | `cargo install rbw` (or apt) | unofficial Rust Bitwarden CLI — a persistent agent so you're not re-unlocking each call; nicer for scripts |
| **cloudflared** | Cloudflare repo | the tunnel connector (no inbound ports) |
| **rclone** / **restic** | `apt install` | off-box backups → R2 / Storage Box (see [`runbooks/BACKUP.md`](./runbooks/BACKUP.md)) |
| **uv / uvx** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | runs the Python MCP servers + Python tooling |
| **node / npm** | nodesource / nvm | runs the npm MCP servers + agent CLIs |
| **docker + compose** | `get.docker.com` | the whole stack + the on-demand pool |
| **jq / yq** | `apt install jq;` yq via binary | JSON/YAML wrangling in scripts (preflight uses jq) |
| shell sugar | see [`TERMINAL.md`](./TERMINAL.md) | fish/zsh, Starship, Atuin, zoxide, Zellij, eza/bat/fzf/ripgrep, thefuck |

### Bitwarden as the secrets source
`bw`/`rbw` pairs with **Infisical** (self-hosted, in [`STACK.md`](./STACK.md)): Infisical for
services that read env at runtime, Bitwarden CLI for *interactive* pulls (fetch a token into
your shell just before a deploy, never write it to disk). Example:
```sh
export BW_SESSION="$(bw unlock --raw)"
export HETZNER_API_TOKEN="$(bw get password hetzner-aurora-hub)"
./infra/hetzner/preflight.sh          # token never touched disk
```

## MCPs (what Claude/agents drive)
Full set + per-agent config syntax in [`mcp/.mcp.json.example`](./mcp/.mcp.json.example) and
the Tier-3 table in [`SERVICES.md`](./SERVICES.md): **hetzner** (provision), **n8n** (author
workflows against real node schemas), **docker** (the on/off switch), **playwright**,
**filesystem**, **postgres**, **fetch**, **git**, **hostinger**.

## Agent CLIs
Claude Code, Agent TARS, Kimi Code, OpenCode, OpenHands, Aider, Goose, Crush, **Gemini CLI** —
installs + the Kimi-as-cheap-backend trick + the failover chain in [`AGENTS.md`](./AGENTS.md).

## Skills
Mirror your Claude skills to `/opt/aurora/skills/`, plus the **n8n skills**
([`czlonkowski/n8n-skills`](https://github.com/czlonkowski/n8n-skills)) — see
[`stacks/n8n/RESOURCES.md`](./stacks/n8n/RESOURCES.md). Any agent landing on the box then has
the playbooks + service catalogue it needs.

## Terminal
The "amazing terminal": local emulator (Wave/Warp/Ghostty) + shell sugar + a browser terminal
(ttyd) — all in [`TERMINAL.md`](./TERMINAL.md).

## Kali — container now, VM later
- **On this box (Hetzner Cloud):** a **Kali container** via the `kali` on-demand profile
  (`services.sh up kali`). Shares the host kernel — great for nmap/nikto/sqlmap/recon, but
  **not** an isolated VM and no kernel-level tooling. **Authorized engagements only**; keep it
  on the disposable box, behind Access.
- **A true Kali VM** needs **nested virtualization**, which Hetzner **Cloud** VPS does *not*
  support. That requires a **Hetzner dedicated / bare-metal** server running Proxmox (or
  libvirt/KVM), then Kali as a guest. Document that as a separate box when a real VM is needed.
- The agency already has a **dedicated-Kali** integration in `hexstrike-ai/` (SSH-over-WS +
  MCP); the container here is the *portable* option, that is the *heavy* one.

## Not installed by default (add when needed)
Activepieces, Ollama/GPU node, Gitea/Woodpecker CI, Docling/Unstructured — all documented in
[`STACK.md`](./STACK.md) / [`SERVICES.md`](./SERVICES.md) as opt-in.
