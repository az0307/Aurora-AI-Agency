# Aurora / Ouroboros — Repository Review & Consolidated TODO

> Review date: **2026-06-27** · Scope: all 10 in-scope repositories under `az0307`.
> Status legend: 🟢 healthy · 🟡 needs work · 🔴 stub / blocked.
> This is a point-in-time snapshot to drive the next round of work — see the per-repo TODOs and the
> consolidated backlog at the bottom.

---

## Per-repository review

### 1. `Aurora-AI-Agency` 🟢
The monorepo and public face. Contains AutoBoros, HexStrike, Gastown, the YMI client package,
client-portal, evermystic tools, and `_empire` strategy docs. Well documented via `CLAUDE.md`.

- ✅ Strong technical docs (`CLAUDE.md`), clear subsystem boundaries.
- 🟡 `README.md` repo layout block lists `ymi-roofing/site` twice and omits `client-portal/`,
  `evermystic/`, and `autoboros-cockpit/` (which exist on disk).
- 🟡 No top-level business definition existed — added `AGENCY.md` (agency + clients) this round.
- 🟡 No CI across subsystems; each is validated manually.
- **TODO:** sync `CLAUDE.md` / `README.md` layout with the actual tree (add `client-portal`,
  `evermystic`, `autoboros-cockpit`); consider a minimal CI matrix (py_compile gastown, pytest
  autoboros, vite build cockpit).

### 2. `ymiroofing.com.au` 🟢 *(was 🔴)*
The deployable Y.M.I Roofing website. **Was an empty repo (one-line README); now populated** this
round with the full site, `_headers`, Worker proxy, 404, and a deploy README.

- **TODO (pre-launch):** replace `WEBHOOK_URL` placeholder with the deployed Worker URL; set the
  `N8N_WEBHOOK_URL` Worker secret; point DNS; confirm ABN + BPC number; supply real photos; optional GA4.

### 3. `ymiroofing` 🟡
Companion repo holding the YMI n8n workflows (lead-capture, review-machine, missed-call, sms-optout,
maintenance-reminder), the Cloudflare Worker, and ops docs.

- 🔴 `static/404.html`, `static/robots.txt`, `sitemap.xml` contain **placeholder local paths**
  (`/mnt/user-data/outputs/...`) instead of real content — broken if deployed as-is.
- 🟡 Overlaps with `ymiroofing.com.au` and `Aurora-AI-Agency/ymi-roofing`; the three-way split is
  confusing. Decide canonical homes: **site → `ymiroofing.com.au`**, **workflows/ops → `ymiroofing`**,
  **design source/ops → Aurora**.
- **TODO:** fix the three placeholder static files (or delete them, now that the real site lives in
  `ymiroofing.com.au`); add a README explaining the repo split.

### 4. `AutoBoros.AI-` 🟡
Product/docs repo for the AutoBoros engine (README + `docs/TESTING.md`). Code lives in
`Aurora-AI-Agency/autoboros`.

- ✅ Clear README (architecture, L0–L4 ladder, security baseline, roadmap).
- 🟡 Docs-only; easy for it to drift from the actual `autoboros` code in the monorepo.
- **TODO:** add a one-line note + link to the canonical code; keep the ladder/security tables in sync
  with the monorepo on each change.

### 5. `autoborosai-dashboard` 🟢
Next.js 15 "Nexus Agent Dashboard" — glass-morphism multi-agent monitoring UI. Good `CLAUDE.md`,
`DEPLOYMENT.md`, Vitest config, Vercel config.

- 🟡 `.env.production` is committed. It is **sanitized** (no live secrets) and self-documents the
  required `git filter-repo --path .env.production --invert-paths` purge — but that purge has not
  been run, and a committed prod env file invites future leaks.
- 🟡 Backend it targets (`http://localhost:8000`) is the AutoBoros API — confirm the prod contract.
- **TODO:** run the documented history purge for `.env.production` and gitignore it; verify build
  (`npm run build` / `type-check`); confirm prod API + WS URLs.

### 6. `AutoborosAi.com` 🟡
Public site + app (React 19 + Vite 7 + Hono + tRPC + Drizzle). Real app under `src/`, `api/`, `db/`.
Has `CLAUDE.md`, `info.md`, env example.

- 🔴 Root `README.md` is still the **default Vite/React template** ("This template provides a minimal
  setup…") — not project documentation for a public-facing product.
- 🟡 Vitest is configured but there are **no test files** in the repo.
- **TODO:** replace the template README with a real one (overview, stack, commands, deploy); add at
  least a smoke test; verify `npm run check` / `lint` / `build`.

### 7. `creator-hub` 🟢
Real React 19 + Vite + Tailwind app — creator/client management with JWT auth, n8n chat, dashboard.
Has `ARCHITECTURE.md`, Docker Compose, n8n, install scripts.

- ✅ Most complete of the standalone app repos; good README + architecture doc.
- 🟡 Verify the n8n/Docker stack still boots and the `.env.example` is complete.
- **TODO:** quick build + lint pass; confirm install scripts (`agency.sh` / `.ps1`) match current layout.

### 8. `meta-automation-hub` 🔴
Governance layer (Ω6). Currently **README (one line) + LICENSE only** — no content.

- **TODO:** add the SOP/compliance/governance material this repo is meant to hold, or fold it into
  `_empire`; at minimum expand the README to state its purpose and what belongs here.

### 9. `KaliShare` 🔴
Kali home-lab project. **README one-liner only** — content lives in `kali-backup-system`.

- **TODO:** clarify relationship to `kali-backup-system` (point the README there) or populate it.

### 10. `kali-backup-system` 🟡
Substantial Kali home-lab backup/menu system — many docs, quick-reference cheatsheets, scripts.

- 🔴 Pervasive **duplicate files** — `AGENTS (2).md`, `AUDIT_REPORT (2).md`, `README (2).md`, etc.
  (Windows "copy" artifacts). Clutters the repo and risks divergence.
- 🟡 No single entry-point README that ties the many `.txt` cheatsheets together.
- **TODO:** delete the ` (2)` duplicates after confirming they match the originals; add an index
  README; consider moving large reference `.txt` files into a `docs/` folder.

---

## Cross-cutting observations

- **Repo sprawl / overlap.** YMI lives across three repos; AutoBoros across two; Kali across two.
  A short "where does what live" map (now partly in `AGENCY.md` §4) reduces confusion.
- **README quality varies wildly** — from excellent (`AutoBoros.AI-`, `creator-hub`) to default
  templates (`AutoborosAi.com`) to one-liners (`KaliShare`, `meta-automation-hub`, `ymiroofing*`).
- **No CI anywhere.** Even a per-repo build/lint check would catch drift early.
- **Committed env files.** `autoborosai-dashboard/.env.production` is the live example; audit every
  repo for committed `.env*` files and ensure only `.env.example` is tracked.

---

## Consolidated TODO (prioritised)

### P0 — launch-blocking
- [ ] **ymiroofing.com.au:** replace `WEBHOOK_URL` placeholder, set Worker `N8N_WEBHOOK_URL` secret, point DNS. *(repo: ymiroofing.com.au)*
- [ ] **ymiroofing:** fix the 3 placeholder static files (`404.html`, `robots.txt`, `sitemap.xml`). *(repo: ymiroofing)*
- [ ] **autoborosai-dashboard:** run the documented `.env.production` history purge and gitignore it. *(repo: autoborosai-dashboard)*

### P1 — correctness & hygiene
- [ ] **AutoborosAi.com:** replace the default-template README with real docs; add a smoke test. *(repo: AutoborosAi.com)*
- [ ] **kali-backup-system:** remove the ` (2)` duplicate files; add an index README. *(repo: kali-backup-system)*
- [ ] **Aurora-AI-Agency:** fix the `README.md`/`CLAUDE.md` layout (dedupe `ymi-roofing/site`, add `client-portal`, `evermystic`, `autoboros-cockpit`). *(repo: Aurora-AI-Agency)*
- [ ] **YMI confirmation:** verify ABN + BPC registration number, then display on the site. *(client: YMI)*

### P2 — structure & docs
- [ ] **meta-automation-hub:** populate with governance/SOP content or fold into `_empire`. *(repo: meta-automation-hub)*
- [ ] **KaliShare:** clarify relationship to `kali-backup-system` in the README. *(repo: KaliShare)*
- [ ] **AutoBoros.AI-:** link docs to the canonical monorepo code; keep tables in sync. *(repo: AutoBoros.AI-)*
- [ ] Audit all repos for committed `.env*` files (only `.env.example` should be tracked).

### P3 — quality bar
- [ ] Add minimal CI (build/lint/test) to each app repo.
- [ ] Carry the existing AutoBoros P1 security items forward (JWT revocation, Redis rate-limit,
      httpOnly cookie) — see `autoboros/docs/SECONDARY_REVIEW.md`.
- [ ] Replace YMI emoji service icons with real roofing photos when available.

---

*Generated by Aurora AI Agency. Re-run this review after the P0/P1 items land.*
