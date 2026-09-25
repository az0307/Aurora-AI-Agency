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
    ├── AutoBoros               ← ENGINE — n8n orchestration, MCP mesh (separate repo/SPV)
    ├── UltronOmega / HexStrike ← SECURITY — red team, pentest (separate repo/SPV)
    └── Meta Umbrella v3.0      ← GOVERNANCE — SOPs, compliance, legal
```

The AutoBoros and HexStrike SPVs are real sibling companies but their code lives in their own
repos, **not here** — see the scope note below.

**This repo** (`Aurora-AI-Agency`) is the agency's client-delivery and hosting layer. It contains:
- The client-facing portal (client-portal)
- Client deliverables (ymi-roofing)
- The agency's own marketing site (site)
- Self-hosting / infrastructure strategy and runnable stacks (infra)
- Experimental/agent tooling (evermystic)
- Organizational strategy documents (_empire)

> **Scope note:** this repo is intentionally limited to agency and client work. Non-agency
> subsystems that used to live here (the AutoBoros orchestration engine + cockpit, the HexStrike
> security platform, the gastown scaffolding CLI) were removed; they belong to their own SPVs and
> repos. Do not re-add them here.

## Repository Overview

**Aurora-AI-Agency** is a monorepo containing independent subsystems:

| Subsystem | Path | Description |
|-----------|------|-------------|
| **client-portal** | `client-portal/` | Aurora client portal — Next.js 14 (App Router) + Clerk auth + Prisma + Stripe |
| **ymi-roofing** | `ymi-roofing/` | Client delivery package — Y.M.I Roofing website, ops docs, chatbot spec |
| **site** | `site/` | Aurora AI Agency's own marketing landing page (static HTML) |
| **infra** | `infra/` | VPS hosting strategy + runnable Docker stacks (n8n, monitoring, dashboard, agents, LLM router) |
| **evermystic** | `evermystic/` | Experimental tooling — Evermystic Haiku executor (single self-contained HTML tool) |
| **_empire** | `_empire/` | Org-wide strategic documents — architecture gap analysis, skill ecosystem maps |

There is no shared code, test suite, linter, build system, or CI/CD pipeline across the subsystems.

---

## client-portal

### What it does

**Aurora client portal** (`aurora-client-portal`) — a Next.js 14 (App Router) client-facing portal where customers view deliverables, jobs, and invoices. Auth is handled by **Clerk**, data by **Prisma** (schema in `prisma/schema.prisma`), and billing by **Stripe**. TypeScript throughout; UI on Radix primitives + Tailwind.

### Commands

```bash
cd client-portal
npm install                 # postinstall runs `prisma generate`
npm run dev                 # next dev
npm run build               # next build
npm run lint                # next lint
npm run db:push             # prisma db push (dev schema sync)
npm run db:migrate          # prisma migrate deploy
npm run db:studio           # prisma studio
```

### Structure & env

- `src/app/(auth)/` — Clerk sign-in/sign-up routes; `src/app/(portal)/` — dashboard, deliverables, invoices, jobs (+ layout).
- `src/app/api/webhooks/clerk/route.ts` — Clerk webhook; `src/middleware.ts` — Clerk route protection.
- `src/lib/db.ts` — Prisma client; `prisma/schema.prisma` — data model.
- Config via `.env.example` → `.env.local` (Clerk keys, `DATABASE_URL`, Stripe keys). Never commit real secrets.

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
    ├── manychat-spec.md               Full ManyChat chatbot spec (5 flows, custom fields, n8n webhook)
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

## site

Aurora AI Agency's own public marketing landing page — static HTML deployed as-is (no build
step). Files: `index.html`, `404.html`, `robots.txt`, `sitemap.xml`, `_headers` (host headers),
`README.md`.

---

## infra

Self-hosting decision document plus runnable setup for standing up an agency box (Hostinger or Hetzner +
Cloudflare) and the Docker stacks that run on it.

- `infra/README.md`, `infra/STACK.md`, `infra/TOOLBOX.md`, `infra/AGENTS.md`, `infra/SERVICES.md` — the strategy, host port map, and agent failover notes.
- `infra/SETUP.md` (ordered setup), `infra/GUIDE.md` (how voice/text/pictures flow and what goes where), `infra/INVENTORY.md` (what's on the server and phones), `infra/check.sh` (read-only health check run on the server).
- `infra/phones/` — per-phone guides, Termux configs, setup scripts, and `phones/kit/` (the `a` menu, Needle phone commands, `aurora-ask`/`aurora-gen`, Bitwarden `aurora-secrets`, widget generator).
- `infra/bootstrap.sh` — provisions the box from the phone; `VPS_PROVIDER=hostinger` (default: `infra/hostinger/provision.sh` + `post-install.sh`, Hostinger KVM 2 via the official API, budget-guarded, typed `buy` confirmation) or `hetzner`.
- `infra/hostinger/` — Hostinger VPS module + post-install base setup (the Hostinger equivalent of cloud-init).
- `infra/hetzner/` — `cloud-init.yaml` (base provisioning) + `provision.sh` + `main.tf.example` (Terraform, hcloud provider). The alternative provider.
- `infra/runbooks/` — `DAY1.md` (stand-up sequence) and `BACKUP.md`.
- `infra/stacks/` — Docker Compose stacks:
  - `n8n/` — self-hosted n8n + Postgres (+ optional Caddy). Login gate is n8n's built-in owner account (n8n removed `N8N_BASIC_AUTH_*` in v1.0); keep it behind Cloudflare Access. Includes a staged workflow library under `stacks/n8n/workflows/`.
  - `router/` — a self-hosted **LiteLLM** proxy ("omni-router") fronting OpenRouter, Anthropic, Kimi and Gemini behind one endpoint with cross-provider fallback chains. Binds `127.0.0.1` only. **Never route client PII through the free model tiers** — keep sensitive traffic on the paid chains (`general`, `code`, `reason`, … — anything without `-free`).
  - `hermes/` — Hermes Agent (chat gateways, MCP, plugins, image/video gen); `FEATURES.md` lists every feature and what's on.
  - `computer/` — Playwright MCP + on-demand computer-use desktop (loopback + Tailscale only).
  - `monitoring/`, `dashboard/`, `agents/` — observability, start page, and sandboxed agent stacks.
  - Router chains are curated per job; run `stacks/router/check-chains.py` after editing them. Uncensored models only appear in the `uncensored*` chains.

Never commit real secrets — only `.env.example` templates.

---

## evermystic

Experimental/agent tooling. Currently a single self-contained tool: `evermystic/tools/evermystic-haiku-executor.html` (a standalone HTML executor — no build step; open in a browser).

---

## _empire

### What it is

Organizational strategy documents spanning the layers of the Ouroboros/Aurora ecosystem. Not deployable code — reference material for architectural decisions. Note: this document predates the repo slim-down and still references sibling SPVs (AutoBoros, HexStrike) as part of the wider org; those are separate companies/repos, not contents of this repo.

### Contents

| File | Description |
|------|-------------|
| `ARCHITECTURE_GAP_SYNTHESIS.md` | Full gap analysis of the skill ecosystem across the empire components. Maps missing skills against the command/attack patterns and identifies critical action items (restore lost legal skills, build P0 skills, wire skill-chain playbooks). |

---

## Repository layout

```
Aurora-AI-Agency/
├── CLAUDE.md                              ← this file
├── README.md                              ← repo front page
├── AGENCY.md                              ← agency operating context / service lines
├── REPOSITORY-REVIEW.md                   ← point-in-time cross-repo review
├── .gitignore                             ← Python bytecode, .env, node_modules, dist
├── client-portal/                        ← Aurora client portal (Next.js 14 + Clerk + Prisma + Stripe)
│   ├── src/app/(auth)/                   ← Clerk sign-in/sign-up
│   ├── src/app/(portal)/                 ← dashboard, deliverables, invoices, jobs
│   ├── src/app/api/webhooks/clerk/       ← Clerk webhook
│   ├── prisma/schema.prisma
│   └── package.json
├── ymi-roofing/
│   ├── site/                             ← static files for Cloudflare Pages
│   └── ops/                              ← agency-internal docs (incl. manychat-spec.md)
├── site/                                 ← Aurora's own marketing landing page (static)
├── infra/                                ← hosting strategy + Docker stacks (n8n, router, monitoring, …)
│   ├── hetzner/                          ← cloud-init + Terraform
│   ├── runbooks/                         ← DAY1 / BACKUP
│   └── stacks/                           ← n8n, router, monitoring, dashboard, agents
├── evermystic/
│   └── tools/evermystic-haiku-executor.html
└── _empire/
    └── ARCHITECTURE_GAP_SYNTHESIS.md     ← org-wide skill gap analysis
```

## Development conventions

- **client-portal** — Next.js 14 (App Router) + TypeScript, Clerk auth, Prisma, Stripe. `next lint` before pushing. Never commit `.env.local`.
- **ymi-roofing** — static site + ops docs; no build step. Keep ACL/Privacy Act compliance intact when editing site copy.
- **site** — static HTML, no build step.
- **infra** — Docker Compose stacks; commit only `.env.example`, never real `.env`. Pin container images for anything internet-facing. n8n and the LLM router sit behind Cloudflare Access / loopback binds.
- None of the subsystems share code or configuration.
- Never commit `.env` files — only `.env.example`.
