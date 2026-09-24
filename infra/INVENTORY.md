# Inventory: everything on the finished server and phones

What you'll have once [SETUP.md](./SETUP.md) is done. **✅ core** = started in SETUP;
**➕ optional** = in the repo, start it when you want it; **⏯ on demand** = start it for a
job, stop it after (to keep RAM free on the 8 GB box).

## The server: `aurora-01`

**Machine:** Hetzner CPX31 (4 vCPU, 8 GB RAM, 160 GB disk) in Singapore, Ubuntu,
≈AUD $28–39/month (`bootstrap.sh` refuses anything over the $39 cap).
**Access:** SSH as `aurora` over Tailscale. After lock-down there are zero public ports.
**Base (cloud-init):** Docker, git, ufw, fail2ban, automatic security updates, zsh/fish,
fzf, ripgrep, fd, bat, eza, zoxide, tldr, mosh, tmux. The tmux theme and plugins are
one copy step: [phones/TERMUX.md §8](./phones/TERMUX.md).
**Files:** everything lives in `/opt/aurora` (this repo's `infra/` folder), owned by
`aurora`. Keys are in `/opt/aurora/secrets.env` (root, mode 600) and each stack's `.env`.

### Stacks (Docker Compose, `/opt/aurora/stacks/…`)

| Stack | Status | What runs | Port (loopback) |
|---|---|---|---|
| `router` | ✅ core | LiteLLM "omni-router": 70+ models, curated job chains with fallbacks | 4000 |
| `n8n` | ✅ core | n8n + Postgres (Caddy optional; not needed with Tailscale) | 5678 |
| `hermes` | ✅ core | Hermes Agent gateway (Telegram, WhatsApp, Discord, Slack) + web dashboard | 9119 (dashboard) |
| `tailscale` | ✅ core | Puts the box on your private network; `tailscale serve` gives the UIs HTTPS links | — |
| `monitoring` | ✅ core | Uptime Kuma, Dozzle (logs) · ➕ Beszel, ntfy | 3001, 8080 · 8090, 8888 |
| `computer` | ✅ core / ⏯ | Playwright MCP (shared browser for agents) · ⏯ computer-use desktop | 8931 · 8501, 6080 |
| `ollama` | ⏯ | Local models: `uncensored-free`, `local-*` (+ optional Open WebUI) | 11434 (3080) |
| `dashboard` | ➕ | Homepage start page | 3002 |
| `activepieces` | ➕ | Zapier-style automation UI (alternative to n8n) | 8081 |
| `agents` | ➕ | OpenHands (needs the Docker socket: use a separate box) | 3003 |
| `ondemand` | ⏯ | Profiles: browser, docs (Gotenberg, Tika), search (SearXNG), rag (Qdrant), storage (MinIO), scratch DBs, translate, stt, kali | 3010–3015, 6333, 9000/9001, 55432/56379 |

Port map and details: [SERVICES.md](./SERVICES.md). Health of all of it:
`bash /opt/aurora/check.sh`.

### Inside Hermes

| Area | What's set up |
|---|---|
| Chat apps | Telegram, WhatsApp (quick bridge or official Cloud API), Discord, Slack. Allow-listed users only |
| Models | `/model` shortcuts: general (default), free, code, code-free, reason, fast, vision, search, research, hermes, uncensored, uncensored-free, grok, opus, supergrok, supergrok-build |
| Side jobs | vision → `vision`; compression, titles, curator → `fast`; goal judge, approvals → `general` |
| Voice | Whisper on the server (voice notes → text); spoken replies with free Edge voices (`/voice tts`) |
| Pictures / video | image_gen (Seedream 4.5 default) and video_gen (Veo 3.1 Lite default) via OpenRouter |
| MCP tools | Composio (1000+ apps), Zapier (9,000+ apps), GitHub, Context7 (docs), Hugging Face, Playwright (browser), Desktop Commander |
| Plugins | disk-cleanup, security-guidance (more: `hermes plugins search`) |
| Skills | bundled: Claude Code, Codex, OpenCode, computer-use, Google Workspace, GitHub, and more; optional: Grok, Antigravity CLI… |
| Long work | `/goal`, `/loop`, `/heartbeat`, `/cron`; background processes; 2 h inactivity timeout |
| Safety | approvals `smart` (`/yolo` per chat), container sandbox (no Docker socket), allowlists |
| Optional | Bot Screen / computer_use (`HERMES_TAG=latest-desktop`), Bitwarden Secrets Manager, SuperGrok and ChatGPT logins |

Every Hermes feature and whether it's on: [stacks/hermes/FEATURES.md](./stacks/hermes/FEATURES.md).

### Agent CLIs you can run on the server (over `server` → tmux)

Claude Code, Gemini CLI, Codex CLI, Grok CLI, OpenCode, Aider, Cursor CLI. Install
lines are in [AGENTS.md](./AGENTS.md), logins in [SUBSCRIPTIONS.md](./SUBSCRIPTIONS.md),
and MCP hookups in [mcp/README.md](./mcp/README.md).

---

## The phones

Both phones get the same Termux setup (`phones/setup/setup-reno11.sh` or
`setup-s10.sh`, which are resumable). They differ only in role and apps.

| | **Reno 11** (daily driver, Android 14) | **S10** (always-on ops phone, Android 12) |
|---|---|---|
| Job | Creates and manages the server, everyday use | Stays on the charger: alerts + backup way in |
| Apps (all listed in [phones/APPS.md](./phones/APPS.md)) | F-Droid, Obtainium, Aurora Store, Termux + API, Widget, Boot, Float, Styling, GUI, (X11), Tailscale, Bitwarden, Aegis, Telegram, ntfy, Claude, GitHub, HeliBoard, Unexpected Keyboard, Material Files, Acode, LocalSend | the same core set, minus Acode / X11 / GUI |
| Background fix | "Disable child process restrictions" toggle | one ADB command (phantom-process killer) |

### In Termux (both phones)

| Thing | What |
|---|---|
| Shell | zsh with predictions (grey text), syntax colours, typo correction, fuzzy tab completion, `z` jumps; starship prompt |
| tmux | "phone" session on open; Catppuccin bar with battery; resurrect/continuum; `Ctrl-a` prefix |
| Packages | openssh, mosh, tmux, git, gh, termux-api, android-tools (adb), jq, fzf, glow, python, nodejs, neovim, htop, ripgrep, fd, bat, eza, zoxide, starship… |
| Commands | `a` / `aurora` (menu), `server` (server tmux), `aurora-ask`, `aurora-needle`, `aurora-gen`, `aurora-models`, `aurora-secrets`, `aurora-widgets`, `aurora-kit`, `aurora-addkey`, `doctor` |
| Needle | `~/.local/share/needle/` (Android engine + needle3 weights, ~37 MB), telemetry off |
| Bitwarden CLI | `bw` (optional, `aurora-kit bitwarden`) |
| Home-screen buttons | Aurora menu · Ask Hermes · Model guide · Box check · Server · Hermes logs · Server status · Restart Hermes |
| Silent buttons | 🎤 Voice command · 🖼 Make image · Ask (as a notification) · Box status (+ any you make with `aurora-widgets new`) |
| At boot | wake-lock + tmux ready; pinned **Aurora** notification with Voice / Ask / Status buttons |
| Config files | `~/.zshrc`, `~/.tmux.conf`, `~/.termux/termux.properties` (extra-keys rows), `~/.ssh/config` (`aurora-01`), Nerd Font |

How to use all of it: [GUIDE.md](./GUIDE.md).
