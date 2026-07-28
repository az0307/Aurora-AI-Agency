# AI-agent CLIs

Decision: **hosted-API model backends** — so every agent below runs fine on a cheap **CPU**
VPS (Hetzner CX/CAX or the Oracle lab). No GPU node needed.

**Never commit API keys.** Put them in `~/.config/<agent>` or a shell-sourced `.env` that is
git-ignored (Infisical or Docker secrets for anything shared). See the repo's `.env.example`
convention.

## The lineup (your names → the real tools)

| You said | Tool | What it is | Install |
|---|---|---|---|
| Claude Code | **Claude Code** (Anthropic) | Primary agent CLI | `npm i -g @anthropic-ai/claude-code` |
| TARS | **Agent TARS** (ByteDance) | Multimodal agent, MCP-native, CLI + web UI | `npm i -g @agent-tars/cli` then `agent-tars` |
| kimiclaw | **Kimi Code CLI** (Moonshot) | Apache-2.0 Claude-Code-style agent; ~10× cheaper | per Kimi Code docs (npm/installer) |
| OpenClaw | **OpenCode** | Top open-source CLI agent | `npm i -g opencode` (per project docs) |
| OpenClaw | **OpenHands** | Most autonomous; runs **sandboxed in Docker** | see `stacks/agents/docker-compose.yml` |
| — | **Aider** | Git-native pair-programmer | `pipx install aider-chat` |
| — | **Goose** (Block) | Extensible local agent | per Goose installer |
| — | **Crush** (Charm) | Lightweight terminal agent | per Charm install |

> Exact package names/commands move fast — confirm against each project's README at install
> time. The install lines above are the current-as-of-2026-07 shape, not a promise.

## The money-saver: Kimi as a backend *inside* Claude Code

Kimi K2 is API-compatible enough to back Claude Code for cheap/bulk work by overriding the
base URL + key (keep your real Anthropic creds for high-stakes runs):

```sh
# cheap lane — point Claude Code at Kimi's Anthropic-compatible endpoint
export ANTHROPIC_BASE_URL="https://api.moonshot.ai/anthropic"   # confirm current URL in Kimi docs
export ANTHROPIC_AUTH_TOKEN="$KIMI_API_KEY"
claude   # now runs on Kimi K2

# unset (or use a separate shell/profile) to return to Anthropic
unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN
```

A tidy pattern: a `claude-kimi` shell function that sets those vars for one invocation, so
your default `claude` stays on Anthropic.

## Where each runs

- **Interactive** (Claude Code, TARS, Kimi, Aider, Goose, Crush): inside the terminal
  cockpit ([`TERMINAL.md`](./TERMINAL.md)) — ideally a Zellij pane, reachable via ttyd +
  Cloudflare Access from anywhere.
- **Autonomous / long-running** (OpenHands): its own **sandboxed Docker** stack
  (`stacks/agents/docker-compose.yml`) so an agent that browses/executes can't touch the
  host. Front it with Cloudflare Access; give it a scoped workspace volume only.

## MCP for the agents

TARS, Kimi Code, OpenCode, and Claude Code are all MCP clients — point them at the same
`mcp/.mcp.json.example` entries (Hetzner, etc.) so any agent can help manage the fleet.
Keep provisioning tokens scoped per Hetzner Project to bound blast radius.

## Future: self-hosted models (Hermes / Ollama)

**Hermes** = Nous Research open-weights *models*, not a CLI. Running them locally needs a
GPU (or a big-RAM box + quantized models via **Ollama**/**vLLM**) — out of scope under the
hosted-API decision, but the drop-in path later is: add an Ollama node, then point any agent
above at `http://<ollama>:11434`.
