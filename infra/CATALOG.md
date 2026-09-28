# Catalog: repos, images and stacks worth considering

Optional add-ons for aurora-01, grouped by job. Nothing here is installed by default. Before
adding any: check it still fits the 8 GB box (start it on-demand, stop it after), pin the
version, bind it to `127.0.0.1`, and put client data only through paid model chains. Verify
each project is current at install time — this is a shortlist, not a lockfile.

## GitHub repos (skills / MCP / agent tooling)
| Repo | Why | Note |
|---|---|---|
| `github/spec-kit` | spec-driven development (`specify`) | see `infra/SPECKIT.md` |
| `anthropics/skills` | Anthropic's open skills | plugin marketplace source |
| `az0307/autoboros-skills` | your own skills SPV | reference as an external marketplace only |
| `czlonkowski/n8n-mcp` + `n8n-skills` | the n8n MCP we already pin | deep node knowledge for authoring |
| `wonderwhy-er/DesktopCommanderMCP` | shell/file MCP | **operator machine only**, never the server |
| `modelcontextprotocol/servers` | reference MCP servers (fetch, git, filesystem…) | pick per need |

## n8n tooling (author & manage workflows)
| Tool | Why |
|---|---|
| `czlonkowski/n8n-mcp` (pinned 2.89.0) | the MCP we ship: lets an agent author/validate against ~2,285 node schemas |
| `czlonkowski/n8n-skills` | companion skills for the above |
| `czlonkowski/n8n-manager-for-ai-agents` | adds *managing a live instance* (create/activate) via the API — pairs with `N8N_API_KEY` |
| n8n **community nodes** | `Settings → Community nodes` in the UI; add per need. Pin versions; only install trusted ones (they run in n8n) |
| The workflows in `stacks/n8n/workflows/aurora` | ready-made vps/agency/admin/personal + the daily runsheet |

## OpenBot: which "bots" (models) to set up
OpenBot talks to whatever OpenAI-compatible endpoint you point it at — here that's the router,
so the "bots" are the router chains. Sensible set: **general** (default), **code** for building,
**reason** for hard problems, **vision** for images. Keep client data off any `-free` chain.
Add a provider key (OpenAI/Anthropic/Google) only if you want to bypass the router for one model.

## Docker images / stacks (self-hosting)
| Stack | Image | For | RAM |
|---|---|---|---|
| **Caddy / Cloudflare Tunnel** | `caddy:2` / `cloudflare/cloudflared` | public HTTPS for the YMI webhook without opening ports | tiny |
| **Vaultwarden** | `vaultwarden/server` | self-hosted Bitwarden-compatible vault (if you ever move off hosted BW) | small |
| **Restic + rclone** | `restic/restic`, `rclone/rclone` | **off-box** encrypted backups to object storage (the missing piece today) | tiny |
| **Gitea / Forgejo** | `gitea/gitea` | a private git mirror on the box | small |
| **Ollama + Open WebUI** | `ollama/ollama`, `ghcr.io/open-webui/open-webui` | local/uncensored models | **heavy — CX43** |
| **Qdrant** | `qdrant/qdrant` | vector DB for RAG (already an on-demand profile) | medium |
| **SearXNG** | `searxng/searxng` | private meta-search for agents (on-demand profile) | small |
| **Stirling-PDF** | `stirlingtools/stirling-pdf` | PDF ops for client docs | medium |
| **Glance / Homepage** | — | Homepage is already the dashboard | — |
| **Beszel / Netdata** | `henrygd/beszel` (already optional), `netdata/netdata` | deeper host metrics than Uptime Kuma | small |
| **Watchtower** | `containrrr/watchtower` | auto-image-updates — **not recommended**; use `aurora maintain upgrade` so upgrades are deliberate + backed up | tiny |

## What to add next (opinion)
1. **Off-box backups (restic → object storage)** — the one real gap; on-box backups don't survive losing the server.
2. **Cloudflare Tunnel** — so the YMI lead webhook is reachable without a public port.
3. **Vaultwarden** only if you want to stop depending on hosted Bitwarden; otherwise skip.

Everything else is on-demand: start for a job with `stacks-up.sh` / the ondemand `services.sh`, stop it after.
