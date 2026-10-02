# OpenBot stack (aurora-01)

CopilotKit OpenBot on aurora-01. **Transfer / Path B docs:** [`docs/`](docs/) (dossier under `docs/git-dossier/`).

**Live:** `https://aurora-01.tail9a65b0.ts.net:3020` (Tailscale Serve, no Funnel) · pin v0.0.15 · Path B AG-UI **LIVE**  
**Port:** `127.0.0.1:3020` → container `3001` (host 3001 is Uptime Kuma).  
**Branch for this pack:** `infra/openbot-transfer-dossier-2026-10-03`

## Env templates (never commit filled files)

| File | Use |
|------|-----|
| `.env.example` | Compose one-container template |
| `openbot.env.example` | Host/runpack-style OpenBot env (Google OAuth + Path B keys) |
| `agent-langgraph.env.example` | Path B LangGraph sidecar |

```sh
cd /opt/aurora/stacks/openbot
# Prefer host env files mode 600; or:
cp .env.example .env && chmod 600 .env && nano .env
docker compose up -d
curl -sS http://127.0.0.1:3020/api/capabilities
```

Filled `*.env` / `openbot.env` / `agent-langgraph.env` are gitignored. Private repo — tailnet URLs OK in docs.
