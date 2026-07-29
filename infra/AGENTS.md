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
| OpenClaw | **OpenCode** | Top open-source CLI agent | `npm i -g opencode-ai` (the `opencode` npm name is an unrelated package) |
| OpenClaw | **OpenHands** | Most autonomous; runs **sandboxed in Docker** | see `stacks/agents/docker-compose.yml` |
| — | **Aider** | Git-native pair-programmer | `pipx install aider-chat` |
| — | **Goose** (Block) | Extensible local agent | per Goose installer |
| — | **Crush** (Charm) | Lightweight terminal agent | per Charm install |

> Exact package names/commands move fast — confirm against each project's README at install
> time. The install lines above are the current-as-of-2026-07 shape, not a promise.

## The money-saver: Kimi as a backend *inside* Claude Code

Kimi K2 exposes an Anthropic-compatible endpoint, so it can back Claude Code for cheap/bulk
work by overriding the base URL, key, and model (keep your real Anthropic creds for
high-stakes runs). Use a **one-shot, fail-closed wrapper** so the Kimi settings apply to a
single invocation only and never clobber your default Anthropic credentials:

```sh
# Add to ~/.config/fish/functions/claude-kimi.fish (or a bash function).
# Fails BEFORE touching anything if the key is missing; scopes vars to one run.
claude-kimi() {
  if [ -z "${KIMI_API_KEY:-}" ]; then
    echo "KIMI_API_KEY is not set" >&2
    return 1
  fi
  # base URL points at the /anthropic root (the SDK appends /v1/messages itself)
  ANTHROPIC_BASE_URL="https://api.moonshot.ai/anthropic" \
  ANTHROPIC_AUTH_TOKEN="$KIMI_API_KEY" \
  ANTHROPIC_MODEL="kimi-k2.7-code" \
    claude "$@"          # runs on Kimi K2 for this call only; your default `claude` is untouched
}
```

Confirm the current base URL and model id in Kimi's docs before use. Because the vars are set
inline on the `claude` command, nothing leaks into the rest of your shell — no `unset` needed.

## Where each runs

- **Interactive** (Claude Code, TARS, Kimi, Aider, Goose, Crush): inside the terminal
  cockpit ([`TERMINAL.md`](./TERMINAL.md)) — ideally a Zellij pane, reachable via ttyd +
  Cloudflare Access from anywhere.
- **Autonomous / long-running** (OpenHands): its own **sandboxed Docker** stack
  (`stacks/agents/docker-compose.yml`) so an agent that browses/executes can't touch the
  host. Front it with Cloudflare Access; give it a scoped workspace volume only.

## MCP for the agents

TARS, Kimi Code, OpenCode, and Claude Code are all MCP clients, but their config **schemas
and secret-injection syntax differ** — `mcp/.mcp.json.example` uses Claude Code's `${VAR}`
expansion. Don't assume one file works everywhere:
- **Claude Code:** `.mcp.json` with `${VAR}` / `${VAR:-default}` expansion (the template).
- **OpenCode:** `opencode.json` under a top-level `mcp` key, using `{env:VAR}` (not `${VAR}`).
- **Kimi Code:** `mcp.json` with `env` for stdio servers / `bearerTokenEnvVar` for HTTP/SSE.
- **Agent TARS:** follow its own MCP config docs; no shared expansion guarantee.

Translate the Hetzner entry into each client's format rather than symlinking one file. Keep
provisioning tokens scoped per Hetzner Project to bound blast radius.

## Future: self-hosted models (Hermes / Ollama)

**Hermes** = Nous Research open-weights *models*, not a CLI. Running them locally needs a
GPU (or a big-RAM box + quantized models via **Ollama**/**vLLM**) — out of scope under the
hosted-API decision, but the drop-in path later is: add an Ollama node, then point any agent
above at `http://<ollama>:11434`.
