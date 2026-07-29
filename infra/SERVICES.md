# Server-side services, MCPs & the on-demand pool

What lives *on* the VPS so an agent can actually do work — split into three tiers:
**always-on**, **on-demand** (rotated on/off to save RAM), and the **MCPs/CLIs** that let
Claude (or any driver — OpenCode, TARS, Kimi) reach all of it.

## Tier 1 — always-on (the base stacks)
Runs continuously; see [`stacks/`](./stacks/) and [`STACK.md`](./STACK.md):
Dokploy (control plane) · n8n · monitoring (Beszel/Uptime Kuma/Dozzle/ntfy) · Homepage ·
cloudflared (tunnel). These are the box's standing capabilities.

## Tier 2 — on-demand pool (rotate on/off per job)
Heavy or occasional services that would waste RAM if always-on. They live in
[`stacks/ondemand/`](./stacks/ondemand/) behind Docker Compose **profiles**, so **nothing
starts by default**. A driver flips one on, uses it, flips it off:

```sh
cd infra/stacks/ondemand
cp .env.example .env && $EDITOR .env
./services.sh up browser      # start; ./services.sh down browser when done
./services.sh list            # profiles available   ./services.sh status  # what's running
```
Agents can equally drive this through the **Docker MCP** (start/stop/inspect containers) —
that MCP *is* the programmatic on/off switch.

| Profile | Service | Use it for | Loopback port |
|---|---|---|---|
| `browser` | browserless/Chromium | scraping, screenshots, page→PDF, Playwright/Puppeteer CDP | 3010 |
| `docs` | Gotenberg | HTML/Office → PDF (client deliverables, invoices) | 3011 |
| `docs` | Apache Tika | parse PDFs/Office/images → text+metadata (RAG ingest) | 3012 |
| `search` | SearXNG | private meta-search API (web search without a paid key) | 3013 |
| `rag` | Qdrant | vector DB for semantic memory / RAG | 6333 |
| `storage` | MinIO | S3-compatible object store (local artifacts, dev R2) | 9000/9001 |
| `scratch` | Postgres + Redis | throwaway datastores for a single job | 55432 / 56379 |
| `translate` | LibreTranslate | offline machine translation (no paid API/egress) | 3014 |
| `stt` | whisper-asr-webservice | speech→text (faster-whisper; CPU-ok for short clips) | 3015 |
| `kali` | kalilinux/kali-rolling | **authorized** recon/testing toolbox — access via `docker exec`/Docker MCP | (no port) |

All bind to **127.0.0.1** — reach any UI via Cloudflare Access, never publicly. Tags are
readable for the template; pin version+digest for production (see [`STACK.md`](./STACK.md)).

**Good candidates to add later** (documented, not built): Docling/Unstructured (richer doc
parsing), a generic Python/Node code-sandbox image.

## Optional standalone stacks (not in the on-demand pool)
Deploy per-box only if you want them; each is its own compose stack:

| Stack | What | Port | Notes |
|---|---|---|---|
| [`stacks/activepieces/`](./stacks/activepieces/) | Activepieces — Zapier-style automation UI | 8081 | Alternative/complement to n8n |
| [`stacks/ollama/`](./stacks/ollama/) | Ollama — self-hosted open-weight models (Hermes/Qwen/etc.) | 11434 | CPU-only for small quantized models; real throughput needs a **GPU box (materially pricier tier)** — see its [README](./stacks/ollama/README.md). Optional `ui` profile (open-webui) on 3080. |

## Host port map (check before adding a service)
Every service binds loopback-only. Keep this table current — two stacks silently
fighting over one host port is the easiest mistake to make here.

| Port | Service | Stack |
|---|---|---|
| 3000 | Dokploy UI | (installed by Dokploy, not compose) |
| 3001 | Uptime Kuma | monitoring |
| 3002 | Homepage | dashboard |
| 3003 | OpenHands | agents |
| 3010–3015 | browser · gotenberg · tika · searxng · libretranslate · whisper | ondemand |
| 3080 | open-webui (`ui` profile) | ollama |
| 5678 | n8n | n8n |
| 6333 | Qdrant | ondemand |
| 8080 | Dozzle | monitoring |
| 8081 | Activepieces | activepieces |
| 8090 | Beszel | monitoring |
| 8888 | ntfy | monitoring |
| 9000 / 9001 | MinIO API / console | ondemand |
| 11434 | Ollama API | ollama |
| 55432 / 56379 | scratch Postgres / Redis | ondemand |

## Tier 3 — MCPs, CLIs & skills that make the box drivable
Configured in [`mcp/.mcp.json.example`](./mcp/.mcp.json.example). Confirm each package name
against its upstream before granting access; pin versions for anything with write access.

**MCPs to run server-side (per agent, in its own config format — see [`AGENTS.md`](./AGENTS.md)):**

| MCP | Gives the agent | Notes |
|---|---|---|
| **n8n** | author + validate workflows against real node schemas | `czlonkowski/n8n-mcp`; pairs with the staged library in [`stacks/n8n/workflows/`](./stacks/n8n/workflows/) — see [RESOURCES.md](./stacks/n8n/RESOURCES.md) |
| **Docker** | start/stop/inspect containers | the on/off switch for the Tier-2 pool |
| **Hetzner** | provision/resize/destroy servers, firewalls, snapshots | scope one token per Project; **pin the runner version** |
| **Playwright** | drive a browser | pair with the `browser` profile or run standalone |
| **Filesystem** | scoped read/write to a workspace dir | never point at `/` |
| **Postgres** | query n8n / scratch DBs | read-only DSN where possible |
| **Fetch** | HTTP/web content | pair with SearXNG for private search |
| **Git** | local repo ops | scoped to the workspace |
| **Hostinger** *(optional)* | lifecycle on a managed box | first-party, lifecycle-only |

**CLIs to keep installed** (baked by [`hetzner/cloud-init.yaml`](./hetzner/cloud-init.yaml) or added day-1):
`docker` + compose, `git`, `rclone`, `restic`, `cloudflared`, `uv`/`uvx`, `node`/`npm`,
`python3`, `jq`/`yq`, plus the terminal sugar in [`TERMINAL.md`](./TERMINAL.md) and the agent
CLIs in [`AGENTS.md`](./AGENTS.md) (Claude Code, TARS, Kimi Code, OpenCode/OpenHands, Aider/Goose/Crush).

**Skills & docs to keep on the box:** mirror your Claude skills to `/opt/aurora/skills/`, keep
this `infra/` tree checked out at `/opt/aurora/infra`, and store per-client `.mcp.json` +
`.env` in the secrets manager (Infisical) — so any agent that lands on the box has the
playbooks, service catalog, and (scoped) credentials it needs to act.

## The demand-scaling loop (how an agent uses all this)
1. Agent needs a capability (e.g. "render this HTML to PDF").
2. Turn it on: `services.sh up docs` **or** Docker MCP `start gotenberg`.
3. Use it: POST to `127.0.0.1:3011` (via the fetch/HTTP tool).
4. Turn it off: `services.sh down docs` — RAM reclaimed for the next job.

A cheap CPU box therefore punches far above its size: capabilities are *latent* until
summoned, so you pay RAM only for what's running this minute.
