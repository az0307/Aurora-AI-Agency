# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**Aurora-AI-Agency** is a monorepo containing two independent subsystems:

| Subsystem | Path | Description |
|-----------|------|-------------|
| **gastown** | `gastown/` | Zero-dependency Python 3 CLI — generates project scaffolding from natural language |
| **hexstrike-ai** | `hexstrike-ai/` | AI-native red team platform — live Kali Linux integration via SSH-over-WebSocket |

There is no shared code, test suite, linter, build system, or CI/CD pipeline across either subsystem.

---

## gastown

### What it does

Takes a natural language description (e.g. `"REST API for users"`) and generates a full directory tree with boilerplate files for one of 7 detected project types. Zero external dependencies — pure Python 3 stdlib only.

### Commands

```bash
# Interactive mode (prompts for input)
python3 gastown/project_generator.py

# Pass description directly
python3 gastown/project_generator.py "web app for task management"

# Specify output directory (default: ./generated_project)
python3 gastown/project_generator.py "REST API for users" -o ~/output-dir

# Validate syntax without running
python3 -m py_compile gastown/project_generator.py
```

### Architecture

Single file: `gastown/project_generator.py` (~843 lines). No modules, no packages, no dependencies.

#### `ProjectGenerator` class — key flow

```
User input (idea string)
  → _detect_project_type()       keyword matching → one of 7 types
  → _get_structure_template()    nested dict: path → content
  → _create_structure()          recursive mkdir + write_text
```

#### Project type detection (`_detect_project_type`)

Detection is substring matching on the lowercased idea string. **First match wins** (order matters):

| Type | Trigger keywords |
|------|-----------------|
| `web_frontend` | web, website, frontend, react, vue, angular |
| `api_backend` | api, backend, server, rest, graphql |
| `cli_tool` | cli, command, tool, script |
| `ml_project` | ml, machine learning, ai, model, neural |
| `data_project` | data, analytics, pipeline, etl |
| `mobile_app` | mobile, app, ios, android |
| `general` | *(fallback — no keywords matched)* |

#### Structure template format (`_get_structure_template`)

Returns a nested `dict`. Keys ending in `/` are directories; values are either another `dict` (subdirectory), a string (file content from a stub method), or `""` (empty placeholder like `.gitkeep`).

#### Stub methods (`_stub_*`)

50+ methods that each return a boilerplate string for one file type. Naming convention: `_stub_<filetype>()`. All generated files include `# TODO` / `// TODO` comments as guidance.

**JavaScript/Node stubs:** `_stub_react_component`, `_stub_css`, `_stub_helpers`, `_stub_index_js`, `_stub_html`, `_stub_test`, `_stub_package_json`, `_stub_gitignore_node`, `_stub_route`, `_stub_controller`, `_stub_model`, `_stub_middleware`, `_stub_db_config`, `_stub_app_js`, `_stub_env`, `_stub_react_native_screen`, `_stub_navigation`, `_stub_theme`

**Python stubs:** `_stub_py_command`, `_stub_py_helpers`, `_stub_py_main`, `_stub_py_test`, `_stub_requirements`, `_stub_setup_py`, `_stub_gitignore_python`, `_stub_notebook`, `_stub_ml_model`, `_stub_preprocess`, `_stub_train`, `_stub_requirements_ml`, `_stub_extract`, `_stub_transform`, `_stub_load`, `_stub_general_main`, `_stub_yaml_config`, `_stub_sql_schema`

**Docs:** `_stub_readme`, `_stub_design_doc`, `_stub_gitignore_general`

#### CLI entry point (`main`)

Uses `argparse`. Positional `idea` arg is optional — omitting it triggers an interactive prompt. `-o / --output` sets output directory (default: `./generated_project`). Exits with code 1 if idea is empty.

#### Generated structures by type

| Type | Tech stack | Key files |
|------|-----------|-----------|
| `web_frontend` | React | src/components/, src/styles/, public/index.html, package.json |
| `api_backend` | Express/Node | src/routes/, src/controllers/, src/models/, src/middleware/, .env.example |
| `cli_tool` | Python | src/commands/, src/utils/, setup.py, requirements.txt |
| `ml_project` | Python/Jupyter | data/raw/, data/processed/, notebooks/, src/models/, src/preprocessing/ |
| `data_project` | Python/SQL | data/, src/pipeline/ (extract/transform/load), sql/schema.sql, config.yaml |
| `mobile_app` | React Native | src/screens/, src/components/, src/navigation/, assets/ |
| `general` | Python | src/main.py, tests/, docs/design.md |

---

## hexstrike-ai

### What it does

AI-native red team platform with live Kali Linux integration. The backend runs on a Kali box and exposes security tools via HTTP+SSE and WebSocket; the frontend (React/Vite/xterm.js) deploys to Vercel and connects over WSS.

### Architecture

```
Browser → Vercel (React/Vite/xterm.js)
               ↓ WSS / HTTPS
         Nginx Proxy (Kali)
               ↓
      HexStrike API :3001  (Express + ssh2 + SSE)
               ↓                    ↓
       Kali Linux tools        FastMCP :8889
       (7 tool routes)        (hexstrike_mcp.py)
```

### Backend (`hexstrike-ai/server/index.ts`)

TypeScript/Express server. Key design decisions:

- **`shell: false` everywhere** — all subprocess calls use `spawn(cmd, args[])`, never `exec` with shell interpolation for untrusted input
- **Command allowlist** — `ALLOWED_CMDS = Set(['nmap','masscan','nikto','sqlmap','hashcat','msfvenom','msfconsole'])`; any other command is rejected
- **Argument sanitization** — `sanitizeArg()` blocks shell metacharacters (`;`, `&&`, `|`, backticks, `$()`, redirects)
- **IP allowlist** — optional `ALLOWED_IPS` env var; all requests from unlisted IPs return 403

#### HTTP endpoints

| Route | Method | Tool | Notes |
|-------|--------|------|-------|
| `/health` | GET | — | Returns `{ok: true, ts}` |
| `/status` | GET | — | Checks which tools are installed via `which` |
| `/tools/nmap` | POST | nmap | Returns XML output; body: `{target, flags?, ports?}` |
| `/tools/nmap/stream` | POST | nmap | SSE streaming; same body |
| `/tools/masscan` | POST | masscan | body: `{target, ports?, rate?}` |
| `/tools/nikto` | POST | nikto | body: `{target}` |
| `/tools/nikto/stream` | POST | nikto | SSE |
| `/tools/sqlmap` | POST | sqlmap | body: `{url, level?, risk?}` |
| `/tools/sqlmap/stream` | POST | sqlmap | SSE |
| `/tools/hashcat` | POST | hashcat | body: `{hash, wordlist?, mode?}` |
| `/tools/hashcat/stream` | POST | hashcat | SSE |
| `/tools/msfvenom` | POST | msfvenom | body: `{platform?, arch?, payload?, lhost, lport?, format?}` |
| `/tools/msfvenom/stream` | POST | msfvenom | SSE |
| `/mcp/invoke` | POST | MCP bridge | Forwards to FastMCP at `HEXSTRIKE_MCP_URL` |

#### WebSocket endpoints

- `/ws` — general message bus; broadcasts messages to all other connected clients
- `/ssh` — SSH-over-WebSocket proxy; query params: `host`, `port`, `username`, `cols`, `rows`; supports resize events via `{type: "resize", rows, cols}` JSON message

#### Backend environment variables

```
PORT=3001
KALI_SSH_HOST=localhost
KALI_SSH_PORT=22
KALI_SSH_USER=kali
KALI_SSH_PASS=           # optional; key-based auth preferred
KALI_SSH_KEY=/home/kali/.ssh/id_rsa
HEXSTRIKE_MCP_URL=http://localhost:8889
FRONTEND_URL=*           # CORS origin
ALLOWED_IPS=             # comma-separated; empty = allow all
```

### Frontend

Deployed to Vercel via `vercel.json`. Built with Vite from `hexstrike-ai/frontend/` (directory not yet checked in — only the build config exists in the repo).

**Vercel environment variables** (set as Vercel secrets):

| Variable | Secret name |
|----------|------------|
| `VITE_BACKEND_URL` | `@hexstrike_backend_url` |
| `VITE_KALI_HOST` | `@hexstrike_kali_host` |
| `VITE_KALI_SSH_PORT` | `@hexstrike_kali_ssh_port` |
| `VITE_KALI_USER` | `@hexstrike_kali_user` |
| `VITE_SHODAN_KEY` | `@hexstrike_shodan_key` |
| `VITE_VT_KEY` | `@hexstrike_vt_key` |
| `VITE_GN_KEY` | `@hexstrike_gn_key` |
| `VITE_GITHUB_TOKEN` | `@hexstrike_github_token` |

### Deployment

**Backend (Kali Linux):**
```bash
sudo bash hexstrike-ai/scripts/setup-kali.sh
# Installs: nmap, masscan, nikto, sqlmap, hashcat, metasploit, ttyd, cloudflared, Node 20
# Creates systemd services: hexstrike-api (port 3001), hexstrike-ttyd (port 7681)
# Edit /opt/hexstrike/.env before starting the API service
systemctl restart hexstrike-api
```

**Frontend (Vercel):**
```bash
cd hexstrike-ai/frontend
npm install && npm run build
vercel deploy --prod
```

**Tunnel (expose Kali to internet):**
```bash
cloudflared tunnel --url http://localhost:3001
```

---

---

## autoboros

### What it does

Real-time agentic job-orchestration platform. A FastAPI backend manages jobs, activities, and autonomous agent execution via n8n workflows. A React 19 cockpit (SPA) provides the operator UI with live WebSocket push. An MCP stdio server gives LLM agents sandboxed tool access (file ops, DB queries, shell commands).

**Status:** audited and patched — backend 4 tests pass, `vite build` exits 0, Alembic migration applies cleanly, zero functional `shell=True`. See `autoboros/docs/AUDIT_CHANGELOG.md` for the full fix log.

### Commands

**Backend:**
```bash
cd autoboros/backend

# Install deps (Python ≥3.11)
pip install -e ".[dev]"

# Run with SQLite (dev)
DATABASE_URL="sqlite+aiosqlite:///./dev.db" SECRET_KEY=x AB_PASSWORD=autoboros uvicorn app.main:app --reload

# Run migrations (Postgres)
alembic upgrade head

# Run tests
DATABASE_URL="sqlite+aiosqlite:///./t.db" SECRET_KEY=x AB_PASSWORD=autoboros python -m pytest tests/ -q

# Lint
ruff check .
```

**Cockpit (frontend):**
```bash
cd autoboros/cockpit
npm install
npm run dev        # dev server (Vite)
npm run build      # production build → dist/
npm run lint
```

**Docker Compose (full stack: API + n8n + Postgres):**
```bash
cd autoboros/backend
cp .env.example .env  # edit with real values
docker compose up
```

### Architecture

```
Browser (React 19 / Vite)
    ↕ REST + WebSocket
FastAPI :8000  (JWT auth, SQLAlchemy async, structlog)
    ↕ httpx webhook
n8n  :5678  (workflow automation)
    ↕ HTTP callback → /api/v1/n8n/callback
FastAPI (resolves job approval / notifies WS)
    ↕
MCP stdio server  (tool access for LLM agents)
```

### Backend structure (`autoboros/backend/`)

| Path | Role |
|------|------|
| `app/main.py` | FastAPI app — lifespan, CORS, router mounts, prod boot guard |
| `app/config.py` | Pydantic `Settings` — all env vars, CORS list parser |
| `app/database.py` | Async SQLAlchemy engine + session factory |
| `app/models/job.py` | `Job` model (id, title, status, level, est, steps, result, timestamps) |
| `app/models/activity.py` | `Activity` model (id, job_id, type, message, created_at) |
| `app/schemas.py` | Pydantic v2 request/response schemas (ConfigDict) |
| `app/routers/auth.py` | `POST /api/v1/auth/login` — JWT issue; 5-try / 5-min brute-force lockout |
| `app/routers/jobs.py` | CRUD + `POST /jobs/{id}/approve` — fires n8n callback on L≥3 |
| `app/routers/activity.py` | `GET /api/v1/activity` — paginated activity feed |
| `app/routers/websocket.py` | `GET /api/v1/ws` — mandatory JWT auth (close 4001); broadcast with 2s backpressure |
| `app/routers/n8n.py` | `POST /api/v1/n8n/callback` + `POST /api/v1/n8n/webhook` |
| `app/routers/seed.py` | `POST /api/v1/seed/evermystic` — JWT-gated demo data loader |
| `app/services/n8n_bridge.py` | httpx async client with 10s/5s timeouts |
| `app/services/websocket_manager.py` | `ConnectionManager` — WS broadcast with per-send timeout |
| `mcp/mcp_server.py` | MCP stdio server — `shell_exec` (allowlist + `shell=False`), `file_read/write` (sandboxed), `db_query` (read-only, 10KB limit) |
| `mcp/mcp_http_bridge.py` | HTTP→MCP bridge (FastMCP) |
| `alembic/` | Async Alembic env — `jobs` + `activity` + indexes |
| `n8n/workflows/` | n8n workflow JSON exports (Evermystic phase 2, example approval) |
| `scripts/seed_evermystic.py` | Seeds demo jobs by importing canonical list from router |
| `tests/test_jobs.py` | 4 pytest-asyncio tests — CRUD, auth (401s), approval flow |

### API routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | public | `{status, version}` |
| POST | `/api/v1/auth/login` | public | Returns JWT; body: `{password}` |
| GET | `/api/v1/jobs` | JWT | List jobs (filter/sort) |
| POST | `/api/v1/jobs` | JWT | Create job |
| PATCH | `/api/v1/jobs/{id}` | JWT | Update job |
| POST | `/api/v1/jobs/{id}/approve` | JWT | Approve job; triggers n8n if L≥3 |
| GET | `/api/v1/activity` | JWT | Paginated activity feed |
| GET | `/api/v1/ws` | JWT (header) | WebSocket — real-time push |
| POST | `/api/v1/n8n/callback` | public | n8n → backend result delivery |
| POST | `/api/v1/n8n/webhook` | public | n8n → backend event push |
| POST | `/api/v1/seed/evermystic` | JWT | Load demo dataset |

### Backend environment variables

```
DATABASE_URL=postgresql+asyncpg://...   # sqlite+aiosqlite:///./dev.db for dev
SECRET_KEY=<random 32+ chars>           # app refuses to boot on default in prod
AB_PASSWORD=<password>                  # single shared password for JWT login
ENV=development                         # "production" enforces non-default secrets
API_BASE_URL=http://localhost:8000      # used by n8n for callback URLs
CORS_ORIGINS=http://localhost:5173      # comma-separated; no wildcard in prod
N8N_WEBHOOK_URL=http://localhost:5678/webhook/autoboros
N8N_API_KEY=
MCP_SERVER_URL=http://localhost:3001
MCP_WORKSPACE=~/autoboros_workspace     # sandbox root for MCP file ops
```

### Cockpit structure (`autoboros/cockpit/`)

React 19 / Vite 6 SPA. Key files:

| Path | Role |
|------|------|
| `src/main.jsx` | Entry — `StrictMode › ErrorBoundary › AppProvider › App` |
| `src/context/AppContext.jsx` | Global state — jobs, activities, auth; optimistic updates with rollback |
| `src/hooks/useWebSocket.js` | WS client — reconnect gated on token; cleanup closes socket on unmount |
| `src/hooks/useAuth.js` | Login/logout — token in `localStorage` (see S7 in docs/SECONDARY_REVIEW.md) |
| `src/api/client.js` | axios wrapper — injects JWT, handles 401 |
| `src/components/Feed.jsx` | Activity feed — stable keys, `useMemo` on time formatting |
| `src/utils/formatTime.js` | `formatRelative()` — ISO-8601 → human-readable |
| `src/components/ErrorBoundary.jsx` | Class boundary — catches render errors, shows reload |
| `vite.config.js` | `base` set for deployment; proxy to API in dev |
| `.github/workflows/deploy.yml` | GH Actions: build SPA → GitHub Pages |
| `nginx.conf` | SPA fallback for Docker deploy |

### Cockpit environment variables

```
VITE_API_URL=https://autoboros.fly.dev/api/v1
VITE_WS_URL=wss://autoboros.fly.dev/api/v1/ws
```

### Deployment

See `autoboros/docs/DEPLOYMENT_GUIDE.md` for full options. Quick reference:

**Fly.io (recommended):**
```bash
fly apps create autoboros
fly volumes create autoboros_data --region iad --size 1
fly secrets set SECRET_KEY=$(openssl rand -base64 32) AB_PASSWORD=$(openssl rand -base64 24) ...
fly deploy --ha=false
```

**Docker Compose (VPS):**
```bash
cp autoboros/backend/.env.example autoboros/backend/.env
docker compose -f autoboros/backend/docker-compose.yml up
```

### Known open issues (non-blocking for single-machine demo)

See `autoboros/docs/SECONDARY_REVIEW.md` for full details. Priority items before internet-facing production:

- **S5 (P1):** JWT has no `jti`/revocation — stolen token valid for 30 days. Requires Redis-backed blacklist.
- **S6 (P1):** Rate-limit state is in-process — bypassed across multiple VMs. Use Redis-backed `slowapi`.
- **S7 (P1):** JWT stored in `localStorage` — exfiltrable via XSS. Migrate to `httpOnly` cookie.

---

---

## ymi-roofing

### What it does

Client delivery package for **Y.M.I Roofing** (client: Ben Breheny, ACN 695 710 055). A complete local-trades digital presence: static website (Cloudflare Pages), privacy policy, terms of service, n8n lead-capture and review-machine workflow specs, ManyChat chatbot spec, and all ops documents (invoices, welcome letter, Google Sheets setup, SEO tracking, DNS cheatsheet).

### Structure

```
ymi-roofing/
├── site/           ← Files deployed to Cloudflare Pages
│   ├── index.html          Website (v2.0 — pressure washing, floating CTA, ACL compliance)
│   ├── privacy.html        Privacy policy (ACL, OAIC, opt-out, 7-year retention)
│   ├── terms.html          Terms of service (full ACL compliance, cooling-off, remedies)
│   ├── robots.txt
│   ├── sitemap.xml
│   ├── favicon.png         (64×64)
│   ├── og-image.jpg        (1200×630 social sharing)
│   ├── manifest.json       (PWA manifest)
│   └── email-signature.html Ben's branded email signature
└── ops/            ← Agency-internal docs (not deployed)
    ├── MASTER-DELIVERY-CHECKLIST.md   6-phase launch checklist (v2.0)
    ├── GOOGLE-SHEETS-SETUP.md         CRM sheet structure (Leads, Jobs, Monthly Summary)
    ├── MANYCHAT-SETUP-CHECKLIST.md    8-flow chatbot build guide
    ├── SEO-TRACKING-SETUP.md          Google Search Console / GA4 / Meta Pixel setup
    ├── n8n-BACKUP-SECURITY.md         Workflow backup & security hardening guide
    ├── DOMAIN-DNS-CHEATSHEET.md       DNS records reference for ymiroofing.com.au
    ├── WELCOME-LETTER.txt             Client onboarding letter
    └── INVOICE-TEMPLATE.txt           AURORA-0001 invoice template
```

### Deployment

**Website (Cloudflare Pages):**
1. Create Cloudflare Pages project `ymi-roofing`
2. Upload all files from `ymi-roofing/site/`
3. Optionally connect custom domain `ymiroofing.com.au` (VentraIP ~$14/yr)

**Lead capture (n8n):**
- Import `lead-capture.json` workflow into n8n
- Set `WEBHOOK_URL` in `site/index.html` line ~883 to the n8n webhook URL ending in `/webhook/ymi-roofing-lead`
- Requires: Google Sheets with Leads/Jobs/Monthly Summary tabs, Twilio account

**Review machine (n8n):**
- Import `review-machine.json` into n8n
- Set Google Place ID and Twilio number

See `ymi-roofing/ops/MASTER-DELIVERY-CHECKLIST.md` for the complete 6-phase launch sequence.

### Key open items (from checklist)

- `WEBHOOK_URL` placeholder in `site/index.html` must be replaced with real n8n URL before go-live
- Facebook/Instagram footer links are placeholders — update with real URLs
- ABN not yet confirmed (only ACN 695 710 055 is set)
- BPC registration number not yet verified — required for display
- Real photos needed to replace emoji icons and placeholder testimonials
- n8n CORS is wildcard `*` — restrict to actual domain after go-live

---

## Repository layout

```
Aurora-AI-Agency/
├── CLAUDE.md                              ← this file
├── README.md                              ← placeholder (AI Studio banner)
├── .gitignore                             ← Python bytecode, .env, node_modules, dist
├── vercel.json                            ← Vercel config for hexstrike frontend
├── gastown/
│   ├── README.md
│   └── project_generator.py              ← entire gastown app (~843 lines)
├── hexstrike-ai/
│   ├── README.md
│   ├── server/
│   │   └── index.ts                      ← entire backend (~257 lines)
│   └── scripts/
│       └── setup-kali.sh                 ← one-shot Kali provisioning script
├── ymi-roofing/
│   ├── site/                             ← static files for Cloudflare Pages
│   └── ops/                              ← agency-internal docs
└── autoboros/
    ├── backend/                           ← FastAPI + n8n + MCP (Python ≥3.11)
    │   ├── app/                           ← routers, models, schemas, services
    │   ├── mcp/                           ← MCP stdio server + HTTP bridge
    │   ├── alembic/                       ← async migrations
    │   ├── n8n/workflows/                 ← n8n workflow exports
    │   ├── tests/                         ← pytest-asyncio tests
    │   ├── scripts/                       ← seed scripts
    │   ├── Dockerfile / Dockerfile.mcp
    │   ├── docker-compose.yml
    │   └── pyproject.toml
    ├── cockpit/                           ← React 19 / Vite 6 SPA
    │   ├── src/
    │   │   ├── components/                ← 30+ UI components
    │   │   ├── context/AppContext.jsx
    │   │   ├── hooks/                     ← useWebSocket, useAuth, useApi, etc.
    │   │   └── utils/
    │   ├── .github/workflows/deploy.yml
    │   ├── Dockerfile / nginx.conf
    │   └── package.json
    └── docs/
        ├── AUDIT_CHANGELOG.md             ← full fix log (5 batches)
        ├── SECONDARY_REVIEW.md            ← 13 follow-up findings (P0–P3)
        ├── DEPLOYMENT_GUIDE.md            ← Fly.io / Docker / Railway options
        └── REMEDIATION_PACKAGE.md         ← deliverables index
```

## Development conventions

- **gastown** — no test suite, no linter, no build step. Validate with `python3 -m py_compile`.
- **hexstrike-ai backend** — TypeScript, no `tsconfig.json` in repo; setup script runs via `ts-node/esm/transpile-only`. All subprocess calls must use `safeSpawn()` — never `exec()` with string interpolation.
- **autoboros backend** — Python ≥3.11, linted with `ruff` (100-char line length). Uses `pytest-asyncio` in auto mode. MCP `shell_exec` must go through the command allowlist + `shell=False`.
- **autoboros cockpit** — React 19, Vite 6, ESLint. No TypeScript (plain JSX). WS reconnect must be gated on token presence to avoid login-screen reconnect loops.
- None of the subsystems share code or configuration.
- Never commit `.env` files — only `.env.example`.
