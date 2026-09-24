# Hermes: every feature, and what's switched on here

From Hermes Agent's own docs (v0.21, September 2026). **On** = configured in
`config.yaml.example` or on by default. **Ready** = works once you add a key or run one
command. **Off** = available, not set up here (reason given).
`h` below means `docker exec -it hermes hermes`.

## Talking to it

| Feature | Here | How |
|---|---|---|
| Telegram, Discord, Slack, WhatsApp gateways | **On** (fill tokens) | `data/.env`; see README |
| Allowlists per platform | **On** | `*_ALLOWED_USERS`; `GATEWAY_ALLOW_ALL_USERS=false` |
| Voice notes → text (Whisper) | **On**, local | free, on the server; Groq optional |
| Spoken replies (TTS) | **Ready** | `/voice tts` in Telegram; Edge voice `en-AU-NatashaNeural` |
| Voice mode (live talk in Discord voice / CLI) | Ready | `/voice on` |
| Wake word ("Hey Hermes") | Off | desktop app feature |
| Web dashboard (settings, keys, MCP, cron, memory) | **On** | loopback :9119, over Tailscale |
| Terminal UI | **On** | `h`, or `a` → 🤖 Hermes terminal UI |
| API server (OpenAI-compatible endpoint) | Off | not needed: the phone uses SSH one-shots (`aurora-ask`) |
| ACP (use Hermes inside editors) | Off | for a laptop editor |
| Desktop app + Bot Mode (named bots, group chats) | Off | needs a computer; connects to this gateway over Tailscale |

## Models

| Feature | Here | How |
|---|---|---|
| Custom endpoint (the LiteLLM router) | **On** | default `general`; `/model <job>` |
| Model aliases | **On** | general, free, code, code-free, reason, fast, vision, search, research, hermes, uncensored, uncensored-free, grok, opus, supergrok… |
| Fallback providers (if the router is down) | **On** | OpenRouter → Hugging Face (paid only) |
| Auxiliary models for side jobs | **On** | vision, compression, titles, curator, goal judge, approvals |
| Subscription logins | Ready | SuperGrok: `h auth add xai-oauth --no-browser`; ChatGPT: `h model` |
| Credential pools (rotate several keys) | Off | one key per provider is enough here |
| Provider routing (OpenRouter price/speed prefs) | Off | the router does this |
| Mixture of Agents presets | Off | costly; try `h model` → Mixture of Agents if curious |
| Subscription proxy / Nous Tool Gateway | Off | uses a Nous Portal subscription you don't have |

## Tools

| Feature | Here | How |
|---|---|---|
| Shell, files, code execution | **On** | inside the container only (no Docker socket) |
| Web search + page extract | **On**, keyless | add `TAVILY_API_KEY` or `FIRECRAWL_API_KEY` for no throttling |
| Browser (built-in, headless) | **On** | automatic |
| Playwright MCP (shared, logged-in browser) | **On** | `stacks/computer` |
| Computer use + Bot Screen (the bot's own desktop) | Ready | `HERMES_TAG=latest-desktop`, then `h computer-use install` |
| Vision (read photos, screenshots) | **On** | send a photo; `vision` chain |
| Image generation | **On** | OpenRouter, Seedream 4.5 default |
| Video generation | **On** | OpenRouter, Veo 3.1 Lite default |
| Document extraction (PDF, Office → text) | **On** | automatic in `read_file` |
| Deliverables (charts, PDFs, sheets sent as files in chat) | **On** | automatic |
| MCP servers | **On** | Composio, Zapier, GitHub, Context7, Hugging Face, Playwright, Desktop Commander |
| Tool search (for very large tool sets) | Automatic | kicks in when many MCP tools are loaded |
| X (Twitter) search | Ready | needs `XAI_API_KEY` or the SuperGrok login |
| Passwords & logins vault (agent fills logins without seeing them) | Off | we keep passwords in Bitwarden, off the server |
| LSP diagnostics after code edits | Automatic | when language servers are present |
| Spotify, Google Meet, Teams plugins | Off | `h plugins enable spotify` etc. if wanted |

## Working on its own

| Feature | Here | How |
|---|---|---|
| Long tasks | **On** | 500 tool steps; only stops after 2 h with no activity |
| Background processes | **On** | the agent starts long commands in the background and polls them |
| `/goal` (keep going until done) | **On** | `/goal <outcome>`; a judge model checks each step |
| `/loop` (repeat on an interval) | **On** | `/loop 30m <task>` |
| `/heartbeat` (nudge an idle chat) | **On** | `/heartbeat every 10m <task>` |
| Scheduled jobs (cron) | **On** | `/cron add "0 21 * * *" "<task>" --deliver telegram`; catches up after reboots |
| Subagents (parallel helpers) | **On** | automatic (`delegate_task`) |
| Kanban board (several agents share tasks) | Off | for multi-profile setups |
| Hooks (run code on events) | Off | e.g. a Telegram alert after 10 tool steps; see the docs |
| Batch processing | Off | research / dataset tool |

## Memory, skills, personality

| Feature | Here | How |
|---|---|---|
| Memory (notes + your profile) | **On** | automatic |
| Session search (find old chats) | **On** | "what did we decide about…" |
| Context files (AGENTS.md, CLAUDE.md, SOUL.md) | **On** | put them in `data/workspace` |
| Skills (bundled + agent-written) | **On** | `h skills browse` |
| Curator (tidies agent-written skills weekly) | **On**, with consolidation | `/curator status`, `h curator rollback` |
| External memory (Honcho, Mem0, Supermemory…) | Off | `h memory` to pick one |
| Personality / SOUL.md | Default | edit `data/SOUL.md` to change its voice |
| Skins, pets | Off | cosmetic |

## Security and secrets

| Feature | Here | How |
|---|---|---|
| Approvals for risky commands | **On**, `smart` | `/yolo` for one chat; `approvals.mode: off` for always |
| security-guidance plugin | **On** | warns on risky code |
| disk-cleanup plugin | **On** | removes temp files |
| Bitwarden Secrets Manager | Ready | `h secrets bitwarden setup` (a separate machine-account project, not your personal vault) |
| Observability (Langfuse traces) | Off | `h plugins enable observability/langfuse` + keys |

To see the live state on the box: `h doctor`, `h plugins list`, `h mcp list`,
`h tools`, `h cron list`, `h curator status`.
