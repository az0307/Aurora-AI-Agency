# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Organization Context

This repo is one piece of a larger organization. Understanding the hierarchy helps when making decisions about where things belong:

```
Ouroboros Foundation Ltd Pty  (AU holding company)
├── Ouroboros AI Innovations Pte Ltd  (Singapore — R&D)
├── Ouroboros Technologies LLC  (Delaware — US market/IP)
└── SPVs per vertical
    ├── Aurora AI Agency        ← PUBLIC FACE — client delivery (this repo)
    ├── AutoBoros               ← ENGINE — n8n orchestration, MCP mesh, multi-agent
    ├── UltronOmega / HexStrike ← SECURITY — red team, pentest, Kali integration
    └── Meta Umbrella v3.0      ← GOVERNANCE — SOPs, compliance, legal
```

**This repo** (`Aurora-AI-Agency`) is the client-delivery and tooling layer: internal build tooling (gastown, autoboros), the AutoBoros operator cockpit and client-facing portal, security tooling (hexstrike-ai), client deliverables (ymi-roofing), experimental agent tooling (evermystic), and org strategy documents (`_empire/`).

`_empire/ARCHITECTURE_GAP_SYNTHESIS.md` maps the full skill ecosystem, gap analysis, and strategic priorities across all organization layers.

## Repository Overview

**Aurora-AI-Agency** is a monorepo of independent subsystems, each in its own top-level directory: `gastown/`, `hexstrike-ai/`, `autoboros/`, `autoboros-cockpit/`, `client-portal/`, `ymi-roofing/`, `evermystic/`, `_empire/`. Run `ls` and read each subsystem's own README for its layout.

**There is no shared code, test suite, linter, build system, or CI/CD pipeline across the subsystems** — treat each as its own project.

---

## gastown

Zero-dependency Python 3 CLI (`gastown/project_generator.py`, single file, stdlib only) that turns a natural-language description into a scaffolded project tree for one of 7 detected project types. No test suite, no linter, no build step — validate with `python3 -m py_compile gastown/project_generator.py`.

Flow: `_detect_project_type()` → `_get_structure_template()` → `_create_structure()`. Stub methods (`_stub_*`) return boilerplate strings per file type. Read the source for the current type list, keyword triggers, and stub inventory.

**Gotcha:** project-type detection is substring matching on the lowercased idea string and **first match wins — order matters**. Adding a keyword that overlaps an earlier type will shadow it.

---

## hexstrike-ai

AI-native red team platform with live Kali Linux integration. The backend (`hexstrike-ai/server/index.ts`, TypeScript/Express) runs on a Kali box and exposes security tools over HTTP+SSE and WebSocket; the frontend (React/Vite/xterm.js) deploys to Vercel and connects over WSS. Read `index.ts` for the current route list and request/response shapes; read the `hexstrike-ai/README.md` and `vercel.json` for the frontend/Vercel wiring.

### Backend security invariants (do not break)

- **`shell: false` everywhere** — all subprocess calls use `spawn(cmd, args[])`, never `exec` with shell interpolation for untrusted input. Route everything through `safeSpawn()`.
- **Command allowlist** — `ALLOWED_CMDS = Set(['nmap','masscan','nikto','sqlmap','hashcat','msfvenom','msfconsole'])`; any other command is rejected.
- **Argument sanitization** — `sanitizeArg()` blocks shell metacharacters (`;`, `&&`, `|`, backticks, `$()`, redirects).
- **IP allowlist** — optional `ALLOWED_IPS` env var; all requests from unlisted IPs return 403.

Backend config is env-driven (`PORT`, `KALI_SSH_*`, `HEXSTRIKE_MCP_URL`, `FRONTEND_URL`, `ALLOWED_IPS`); Vercel frontend vars are set as Vercel secrets. See the README for the full variable list. Never commit real secrets.

### Playbooks & proposals

`hexstrike-ai/playbooks/` holds operational playbooks for **authorized engagements only**, mapped to the D-CIPHER pattern (Strike → Analysis → Research → Report): `playbook-bug-bounty.md` (8-phase bug-bounty pipeline) and `playbook-container-k8s.md` (container/K8s escape + RBAC abuse). `hexstrike-ai/proposals/pentest-proposal-template.docx` is an external-pentest proposal template with placeholder client details — **replace client details before use**.

### Deployment

```bash
# Backend (Kali): installs tools, creates systemd services hexstrike-api (3001) + hexstrike-ttyd (7681)
sudo bash hexstrike-ai/scripts/setup-kali.sh
# edit /opt/hexstrike/.env before starting, then:
systemctl restart hexstrike-api

# Frontend (Vercel)
cd hexstrike-ai/frontend && npm install && npm run build && vercel deploy --prod

# Tunnel (expose Kali)
cloudflared tunnel --url http://localhost:3001
```

---

## autoboros

Real-time agentic job-orchestration platform: FastAPI backend (jobs, activities, autonomous agent execution via n8n), a React 19 cockpit SPA with live WebSocket push, and an MCP stdio server giving LLM agents sandboxed tool access.

**Status:** audited and patched — backend tests pass, `vite build` exits 0, Alembic migration applies cleanly, zero functional `shell=True`. See `autoboros/docs/AUDIT_CHANGELOG.md`.

### Commands

```bash
# Backend (Python ≥3.11)
cd autoboros/backend
pip install -e ".[dev]"
DATABASE_URL="sqlite+aiosqlite:///./dev.db" SECRET_KEY=x AB_PASSWORD=autoboros uvicorn app.main:app --reload
alembic upgrade head                                                   # Postgres migrations
DATABASE_URL="sqlite+aiosqlite:///./t.db" SECRET_KEY=x AB_PASSWORD=autoboros python -m pytest tests/ -q
ruff check .

# Cockpit
cd autoboros/cockpit && npm install && npm run dev   # build / lint as usual

# Full stack (API + n8n + Postgres)
cd autoboros/backend && cp .env.example .env && docker compose up
```

Read `app/` (routers, models, schemas, services), `app/config.py`, and the router files for the current API surface and env vars. Deployment options are in `autoboros/docs/DEPLOYMENT_GUIDE.md`.

### Invariants & known issues (not derivable from code)

- **MCP `shell_exec`** (`mcp/mcp_server.py`) must go through the command allowlist with `shell=False`; `file_read/write` stay sandboxed to `MCP_WORKSPACE`; `db_query` is read-only with a 10KB limit.
- The app **refuses to boot in production on a default `SECRET_KEY`/`AB_PASSWORD`**, and CORS uses an explicit origin list — no wildcard in prod.
- WebSocket route requires JWT auth (closes 4001 otherwise).
- **Open issues before internet-facing production** (see `autoboros/docs/SECONDARY_REVIEW.md`): S5 — JWT has no `jti`/revocation (stolen token valid 30 days; needs Redis blacklist); S6 — rate-limit state is in-process (bypassed across VMs; needs Redis-backed `slowapi`); S7 — JWT in `localStorage` is XSS-exfiltrable (migrate to `httpOnly` cookie).

---

## autoboros-cockpit

**AutoBoros Cockpit v2** — a standalone React 19 + Vite rebuild of the original single-file HTML operator dashboard (job board, activity feed, drawers, approval/draft UI, `localStorage` persistence, global search, keyboard shortcuts, accessibility). Self-contained SPA, distinct from `autoboros/cockpit/`; deploys independently. React 19 with `useReducer`, plain JSX (no TypeScript), ESLint runs with `--max-warnings 0`.

---

## client-portal

**Aurora client portal** (`aurora-client-portal`) — Next.js 14 (App Router) client-facing portal (deliverables, jobs, invoices). Auth by **Clerk**, data by **Prisma** (`prisma/schema.prisma`), billing by **Stripe**; TypeScript, Radix + Tailwind. Standard Next.js scripts plus `db:push` / `db:migrate` / `db:studio` (Prisma) — see `package.json`. Config via `.env.example` → `.env.local`; **never commit real secrets**.

---

## evermystic

Experimental/agent tooling. Currently a single self-contained tool: `evermystic/tools/evermystic-haiku-executor.html` — no build step, open in a browser.

---

## ymi-roofing

Client delivery package for **Y.M.I Roofing** (client: Ben Breheny, ACN 695 710 055). `site/` holds the static website + legal pages deployed to Cloudflare Pages; `ops/` holds agency-internal docs (delivery checklist, Google Sheets/CRM setup, ManyChat spec, SEO tracking, DNS cheatsheet, invoice/welcome templates) and is **not deployed**. See `ymi-roofing/ops/MASTER-DELIVERY-CHECKLIST.md` for the 6-phase launch sequence.

### Key open items (must resolve before go-live)

- `WEBHOOK_URL` placeholder in `site/index.html` (~line 883) must be replaced with the real n8n webhook URL ending in `/webhook/ymi-roofing-lead`.
- Facebook/Instagram footer links are placeholders.
- ABN not yet confirmed (only ACN 695 710 055 is set); BPC registration number not yet verified but required for display.
- Real photos still needed to replace emoji icons and placeholder testimonials.
- n8n CORS is wildcard `*` — restrict to the real domain after go-live.

---

## _empire

Organizational strategy documents spanning all layers of the Ouroboros/Aurora/HexStrike ecosystem — reference material, not deployable code. `ARCHITECTURE_GAP_SYNTHESIS.md` is the full skill-ecosystem gap analysis (maps 30+ missing skills against the D-CIPHER attack pattern and Ouro command pattern; identifies the critical action items).

## Development conventions

- **gastown** — no test suite, linter, or build step. Validate with `python3 -m py_compile`.
- **hexstrike-ai backend** — TypeScript, no `tsconfig.json` in repo; setup script runs via `ts-node/esm/transpile-only`. All subprocess calls must use `safeSpawn()` — never `exec()` with string interpolation.
- **autoboros backend** — Python ≥3.11, `ruff` (100-char lines), `pytest-asyncio` in auto mode. MCP `shell_exec` must go through the command allowlist + `shell=False`.
- **autoboros cockpit** — React 19, Vite 6, ESLint, plain JSX. WS reconnect must be gated on token presence to avoid login-screen reconnect loops.
- None of the subsystems share code or configuration.
- Never commit `.env` files — only `.env.example`.
