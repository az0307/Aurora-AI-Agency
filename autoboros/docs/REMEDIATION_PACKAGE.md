# AutoBoros — Complete Remediation Package

Generated: 2026-06-20
Scope: All remaining items from audit changelog + secondary review + deployment infrastructure

---

## 📦 Deliverables (all in `/mnt/agents/output/autoboros-infra/`)

### Infrastructure & Deployment
| File | Purpose |
|------|---------|
| `fly.toml` | Fly.io app config with healthchecks, volumes, env injection |
| `Dockerfile.fly` | Multi-stage build: Node SPA → Python FastAPI + staticfiles |
| `deploy.yml` | GitHub Actions: Fly deploy API → build SPA → Pages deploy |
| `DEPLOYMENT_GUIDE.md` | Fly.io / VPS / Railway / Render step-by-step |
| `Makefile` | One-command `make dev`, `make test`, `make security-check` |

### Environment & Onboarding
| File | Purpose |
|------|---------|
| `.env.example.backend` | Required + optional vars with descriptions |
| `.env.example.frontend` | Vite build-time vars |

### Code Patches (drop-in replacements)
| File | Replaces | Fixes |
|------|----------|-------|
| `app_schemas.py` | `app/schemas.py` | Pydantic v2 `ConfigDict` (removes deprecation warnings) |
| `app_config.py` | `app/config.py` | `SettingsConfigDict`, CORS split validator, prod secret guard |
| `app_main.py` | `app/main.py` | CSP middleware, security headers, prod boot guard, `/health` |
| `app_routers_websocket.py` | `app/routers/websocket.py` | Mandatory WS auth (4001 close), broadcast backpressure (2s timeout) |
| `app_services_n8n_bridge.py` | `app/services/n8n_bridge.py` | `httpx` bounded timeout (10s/5s connect) |
| `mcp_mcp_server.py` | `mcp/mcp_server.py` | 10KB query limit, read-only `db_query`, path sandboxing |

### CI / Security Gates
| File | Purpose |
|------|---------|
| `security.yml` | GitHub Actions: `shell=True` hard ban + default secret detection |

### Documentation
| File | Purpose |
|------|---------|
| `PYDANTIC_V2_MIGRATION.md` | Before/after examples for `Config` → `ConfigDict` |
| `SECONDARY_REVIEW.md` | 13 new findings (P0–P3) with fixes — distributed systems + frontend prod gaps |

---

## 🔴 Secondary Review — Key New Findings

| ID | Sev | Finding | Fix Location |
|----|-----|---------|--------------|
| S1 | P0 | Missing `__all__` in `app/__init__.py` | Add `__all__ = []` |
| S2 | P0 | n8n bridge no timeout → event loop block | `n8n_bridge.py` — `httpx.Timeout(10, connect=5)` |
| S3 | P0 | WS broadcast no backpressure → memory bloat | `websocket.py` — `asyncio.wait_for(..., 2.0)` + drop |
| S4 | P1 | MCP `db_query` no length limit → DoS | `mcp_server.py` — `MAX_QUERY_LEN = 10_000` |
| S5 | P1 | JWT no `jti`/revocation → stolen token lives 30d | Add Redis-backed `jti` blacklist or short-lived tokens |
| S6 | P1 | Rate limit not distributed → bypass across VMs | Use Redis (`slowapi`) or sticky sessions |
| S7 | P1 | `localStorage` token → XSS exfiltration | Switch to `httpOnly` cookie or `sessionStorage` |
| S8 | P2 | Alembic async `target_metadata` may be wrong | Verify `env.py` sets `target_metadata = Base.metadata` |
| S9 | P2 | `useWebSocket` leaks connections on token change | Cleanup `ws.close()` in `useEffect` return |
| S10 | P2 | `Feed.jsx` recalculates relative time on every render | `useMemo` around mapped activities |
| S11 | P3 | No frontend structured logging | Add `window.onerror` → POST `/api/v1/log` |
| S12 | P3 | Docker compose no n8n memory limit | Add `deploy.resources.limits.memory: 1g` |
| S13 | P3 | No CSP headers | `main.py` middleware — delivered in patch |

**Verdict:** First audit caught "won't boot" + RCE. Secondary review catches distributed-systems blind spots (S5, S6) and production frontend gaps (S7, S11, S13). S5–S7 are mandatory before internet-facing deployment.

---

## 🚀 Deployment Quick Start (Fly.io)

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh
fly auth login

# 2. Create app + volume
fly apps create autoboros
fly volumes create autoboros_data --region iad --size 1

# 3. Set secrets
fly secrets set SECRET_KEY=$(openssl rand -base64 32)
fly secrets set AB_PASSWORD=$(openssl rand -base64 24)
fly secrets set DATABASE_URL="postgresql+asyncpg://..."
fly secrets set N8N_API_KEY="..."
fly secrets set N8N_BASE_URL="https://your-n8n.fly.dev"
fly secrets set MCP_SERVER_URL="https://your-mcp.fly.dev"

# 4. Deploy
fly deploy --ha=false

# 5. Set GitHub repo vars for SPA build
# VITE_API_URL=https://autoboros.fly.dev/api/v1
# VITE_WS_URL=wss://autoboros.fly.dev/ws
```

---

## ✅ Remaining Known Issues (non-blocking)

- Pydantic v2 `class Config` deprecation warnings → **fixed** in `app_schemas.py` + `app_config.py` patches
- GitHub Pages static-only limitation → **documented** in `DEPLOYMENT_GUIDE.md` (use Fly staticfiles or set public API vars)
- MCP command allowlist conservative → **intentional**; extend `ALLOWED_COMMANDS` deliberately
- JWT revocation (S5) → **architectural**; requires Redis or stateful session store — not a quick patch

---

## 🛡️ Security Checklist Before Going Live

- [ ] `SECRET_KEY` and `AB_PASSWORD` changed from defaults
- [ ] `CORS_ORIGINS` set to exact cockpit origin (no `*`)
- [ ] `seed` route JWT-gated or removed in prod
- [ ] WS auth mandatory (4001 on missing/invalid token)
- [ ] `shell=True` lint gate active in CI
- [ ] CSP headers serving from API
- [ ] Rate limit distributed (Redis) if multi-VM
- [ ] JWT `jti` + revocation implemented
- [ ] `localStorage` token → `httpOnly` cookie migration planned
- [ ] n8n memory limits in compose
- [ ] Frontend error logging to backend

---

All files are ready to download. Apply patches by copying contents over existing files (or diff-merge). Infrastructure files (`fly.toml`, `Dockerfile.fly`, etc.) are net-new.
