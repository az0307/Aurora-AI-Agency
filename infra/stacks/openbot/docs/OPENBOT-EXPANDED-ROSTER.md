# OpenBot expanded roster — Aurora AI Agency transfer plan

**Owner:** Bot Forge → executor CoS (UI create)  
**Host:** aurora-01 · `https://aurora-01.tail9a65b0.ts.net:3020`  
**Written:** 2026-10-03 ~02:16 AEST  
**Companion:** `OPENBOT-ROSTER-MAP.md` (Phase-1 prompts §D) · `PHASE1-CREATE.md` (live create checklist) · `AURORA-FLEET-MAPPING.md`

## Phase-1 first (authoritative — do not skip or contradict)

| Rule | Detail |
|------|--------|
| No Grok teams | OpenBot uses **channels + naming** + admin grants. No first-class teams object. |
| Phase-1 create only | Coworkers: **Search**, **Deep Dive**, **Chief of Staff**, **Agency Ops**. Plugin: **Parallel Search** → Research Desk (+ Search / Deep Dive). |
| Prompts | Reuse `OPENBOT-ROSTER-MAP.md` **§D** for Search Specialist / Deep-Dive Analyst / CoS. |
| Defer until Phase-1 usable | Bot Forge, Right Hand, full seating, marketplace recreates, Lab. |
| Wave 2+ | Create as **channels** per §1; coworkers per §2. |

**Naming convention:** `Aurora / <Channel> / <Role>` (matches Phase-1).

**Holds (all waves):** no secrets in chat; no Ben/YMI contact; no live ads spend; no inventing share/plugin IDs; Lab isolated from client/social.

---

## Runtime status (2026-10-03 ~02:30 AEST) — corrected

**Path B AG-UI is live** (`openbot-agent-langgraph` on `openbot-net`). Search coworker created. Managed empty endpoint still UI-required; thread smoke (`Failed to initialize thread`) — OpenBot IM / CoS fixing Managed endpoint URL.

**Interim / create rules:**
- Keep **OPENBOT-EXPANDED-ROSTER.md** as create queue once Search smoke passes
- Role text via Skills where needed; department channels `Aurora / …`
- No §D hotfix

**Forge top-5 next (after Search smoke):** see `git-dossier/RECOMMENDED-ADDITIONS.md`

**Git dossier pack (Forge-owned, no secrets):** roster map, expanded roster, Phase-1 create, fleet mapping, plugin catalogue, path-B runpack, forge-status, brief/ops/validation/env-checklist/docker-run — **never** pack `*.env` / oauth credential files.

---

## 1) Department channel list

Channels (not Grok teams). **≤6 seats** each. Cross-seat CoS thinly; do not dump every specialist into every room.

### Core (create after Phase-1 smoke)

| Channel | Seat (≤6 OpenBot coworkers) | Purpose |
|---------|-----------------------------|---------|
| **Agency Core** | Chief of Staff, Agency Ops, Campaign Ops, Content Writer, Bot Forge, Projects Manager* | Day-to-day agency OS — ops, briefs, campaign tracking |
| **Agency Delivery** | Chief of Staff, Ads Manager, Web/Growth, Client Reporting Analyst, Outbound Prospecting*, GitHub | Paid / growth / reporting / ship path |
| **Marketing Intel** | Chief of Staff, SEO & AEO Desk*, Stalk Bot*, Content Writer, Web/Growth, Deep Dive | SEO/GEO/competitor intel (Search floats in for pulls) |
| **Social Desk** | Social/LinkedIn, LinkedIn Creative, LinkedIn Engagement, Content Writer, Chief of Staff, Copy Humanizer* | Social lane only — no Lab / no YMI noise |
| **Client / YMI** | YMI Account, Ads Manager, Agency Ops, Web/Growth, Right Hand, Chief of Staff | Client-signal clean (same as Grok Ymi) — **no** social/lab |
| **Mentor / Study** | Study Coach, Right Hand, Chief of Staff, Deep Dive, Projects Manager*, Writing Bot* | Learning / mentor lane |
| **PA Desk** | Chief of Staff, Right Hand, Termus (PA/terms), Bot Forge | Aaron personal/ops desk |
| **Aurora Infra** | GitHub, Web/Growth, Bot Forge, Chief of Staff, VPN Manager†, OpenBot Install Manager† | Host/deploy/fleet visibility — infra owners stay Grok-primary for docker/SSH |

### Optional / Phase-1 home

| Channel | Seat (≤6) | Purpose |
|---------|-----------|---------|
| **Research Desk** | Search, Deep Dive, Chief of Staff, Researchy* | **Phase-1 home** for Search + Deep Dive; Parallel Search grants live here |
| **CoS routing** *(optional)* | Chief of Staff, Agency Ops, Bot Forge, Search | Thin triage channel if CoS needs a dedicated inbox; skip if Core + Research cover it |
| **Lab S10** | S10 Nethunter, Lab Hygiene Librarian, Toolkit Script Engineer | Own-device lab only — **defer**; never mix with Client/Social |
| **Hobby** | Hobby Project Coach, Right Hand, Chief of Staff, Bot Forge | Side projects — create when Hobby lane used on OpenBot |

\* = recreate as OpenBot custom with same one-job (mirror of Grok marketplace absorb / dossier gap) — **no invented Grok share IDs**.  
† = infra-primary on Grok; OpenBot stub optional for visibility only.

**Skip v1:** Social Ops (legacy), empty Video/Bot shells, Marketing Core if Marketing Intel + Social Desk already cover the lane, Team Beta / n8n Desk until product/connectors ready.

---

## 2) Must-add OpenBot customs beyond Phase-1

**Already Phase-1 (do not re-create as different names):** Search, Deep Dive, Chief of Staff, Agency Ops.

Ordered waves **after** Phase-1 is usable. Prefer UI names that match Grok/dossier where practical; reuse `OPENBOT-ROSTER-MAP.md` §D-style prompts.

### Wave 2A — mentor + client (Aaron-widened priority)

| Title | One-line job | Prompt source |
|-------|--------------|---------------|
| **Study Coach** (Mentor / Study Coach) | Turn syllabus/readings/notes into Sydney-timezone study plans, quizzes, and source-linked summaries — never submit as Aaron or invent citations. | Skeleton below (§2.1) |
| **YMI Account** | Client account lead for Ben @ YMI Roofing — notes, deliverables tracker, website follow-ups; **no Ben contact / no live ads** without Aaron yes. | Skeleton below (§2.2) |

### Wave 2B — deferred from Phase-1

| Title | One-line job | Prompt source |
|-------|--------------|---------------|
| **Bot Forge** | Fleet architect — roster maps, one-job prompts, OpenBot↔Grok alignment; no docker/SSH/secrets. | `OPENBOT-ROSTER-MAP.md` §D.4 |
| **Right Hand** | Aaron context / PA continuity — priorities, calendar, preferences; drafts only, never send/spend. | Mirror Grok Right Hand one-job (dossier §10) |

### Wave 2C — agency transfer must-haves

| Title | One-line job |
|-------|--------------|
| **Campaign Ops** | Track campaigns across Notion/ClickUp/Shopify — status, deadlines, assets, handoffs. |
| **Content Writer** | Briefs/drafts/edits for blog, landing, email, campaign copy. |
| **Ads Manager** | Paid media audits/structure for Meta/Google (YMI+) — drafts only; no live spend. |
| **Web/Growth** | Landing pages, experiments, GitHub/Vercel ship path — conversion + analytics. |
| **Client Reporting Analyst** | Draft client scorecards from ads/organic/web/call exports — evidence, gaps, exec summary; never send to client. |
| **Projects Manager*** | Notion SoT projects + task claiming so CoS does not execute specialist work. |
| **GitHub** | Repos, PRs, issues, CI/shipping hygiene for agency + client work. |
| **Outbound Prospecting*** | ICP → researched first-message drafts; nothing sends without yes. |

### Wave 3 — marketing / social

| Title | One-line job |
|-------|--------------|
| **SEO & AEO Desk*** | Keywords → writer-ready search/AI-answer briefs (GSC-aware). |
| **Stalk Bot*** | Competitor onboarding/pricing/changelog pulse; never posts/contacts. |
| **Social/LinkedIn** | Posts, carousels, engagement plans for LinkedIn. |
| **LinkedIn Creative** | Post angles → slide/carousel briefs (Canva/Gamma-ready). |
| **LinkedIn Engagement** | Comment-reply drafts + engagement plans; performance notes. |

### Wave 4 — PA / infra stubs / deferred lanes

| Title | One-line job | When |
|-------|--------------|------|
| **Termus** (PA/terms) | PA / terms helper — **not** Lab/NetHunter. | With PA Desk |
| **Hobby Project Coach** | Hobby idea → bounded milestones + next step; never buy/publish. | With Hobby channel |
| **VPN Manager†** / **OpenBot Install Manager†** | Infra stubs for visibility only. | Aurora Infra if needed |
| **Lab trio** | S10 / Hygiene / Toolkit. | Lab S10 only when used |
| **n8n Workflow Builder** | Workflow design after n8n MCP available. | After connectors |

### 2.1 Study Coach — short skeleton (missing from roster §D)

```text
You are Study Coach for Aaron Baker / Aurora AI Agency (OpenBot on aurora-01).

Job:
- Turn syllabus, readings, notes, and questions into a realistic Australia/Sydney study plan.
- Explain at the requested level; produce retrieval quizzes, spaced-review prompts, worked examples, source-linked summaries.
- Track understood vs weak; propose the next study block.

Anti-jobs:
- Never submit/impersonate Aaron, fabricate citations, complete graded work as Aaron, claim teacher authority, contact a school, buy materials, or make medical/legal/financial decisions.
- No secrets in chat. Do not invent plugin/share IDs.

Voice: clear plan → drill → check understanding.
Handoff: long investigations → Deep Dive; fleet/roster → Bot Forge; triage → Chief of Staff.
Placeholders: [COURSE], [ASSESSMENT], [DEPTH], [DEADLINE].
```

### 2.2 YMI Account — short skeleton (missing from roster §D)

```text
You are YMI Account for Aaron Baker / Aurora AI Agency (OpenBot on aurora-01).

Job:
- Client account lead for Ben at YMI Roofing: relationship notes, meeting notes, deliverables tracker, website follow-ups, status rollups Aaron can edit.
- Keep Client/YMI channel signal clean; hand ads/web/reporting to Ads Manager, Web/Growth, Client Reporting Analyst.

Anti-jobs / holds:
- No Ben / YMI contact unless Aaron explicitly asks.
- No live ads spend or publish without Aaron yes.
- No secrets, tokens, or .env in chat.
- Do not mix Social Desk or Lab work into this lane.

Voice: structured status + open loops + asks for missing inputs.
Placeholders: [DELIVERABLE], [DATE_RANGE], [OWNER], [BLOCKER].
```

---

## 3) Grok marketplace gaps worth recreating as OpenBot customs

Source: dossier §10.6 + TOP-100 must/absorb ranks. **Recreate as OpenBot custom with the same one-job** — do **not** “Add Grok share …” / invent plugin IDs.

| OpenBot custom name | Same one-job (from dossier / top-100) | Priority cue |
|---------------------|----------------------------------------|--------------|
| **AI Search Visibility** | GEO/AEO scoreboard — do AIs/Google recommend you, who instead | must |
| **GTM Loop Closer** | Find promises/follow-ups left in meetings, email, Slack, CRM, tasks | must |
| **Copy Humanizer** | Human-voice polish gate before client/social send; show changes; invent no facts | must |
| **Projects Manager** | Notion SoT projects; specialists claim tasks; stop CoS executing specialist work | must |
| **SEO & AEO Desk** | Keywords → writer-ready search/AI briefs | must |
| **Stalk Bot** | Competitor newsletter/onboarding/pricing/changelog pulse | must |
| **Meeting Recap Deck** | Notes/transcript → recap deck; never invent quotes | absorb |
| **Account Research** (Account Research Desk / GTM Account Research) | Pre-call brief + account plan for a named account | absorb |
| **Paid Media Report Desk** | Google/Meta/LinkedIn exports → one weekly report beside Ads Manager | absorb |
| **Site Audit** | SEO+speed+a11y+CRO+schema scored with evidence URLs | absorb |
| **Video Edit Desk** | Footage → cut clips, captions, platform exports (fills empty Video shell) | absorb |
| **Critiquito** | Screenshot/Figma → ranked design critique; never edits files | absorb |
| **Company Docs Q&A** | Cited answers from live docs / SOPs | absorb |
| **Researchy** | Sourced fact-check / research desk (complements Search + Deep Dive) | absorb |
| **Writing Bot** | Non-marketing prose partner; Content Writer stays marketing owner | absorb |
| **Outbound Prospecting** | ICP → researched first-message drafts | absorb |
| **last30days** | Grounded “what people say” last 30 days across public sources | absorb |
| **Product Marketer** | Positioning / tone / competitive differentiation | absorb later |
| **figma bro** | Figma → build spec; token/motion audit | when design→dev grows |

**Do not recreate as OpenBot CoS-duplicate:** Alfred (orchestrator overlap).  
**Skip while Ads Manager owns paid:** Ad Spend Watch / Performance Marketer unless Ads Manager asks.  
**Personal QoL (Tradbot, Morning Newspaper, etc.):** only if Personal channel is used on OpenBot.

---

## 4) Recommended OpenBot plugins / MCP / skills to enable first

**Names only.** Priority order. Verify availability in OpenBot `/admin/plugins` marketplace UI before enabling — do not invent SKUs.

| # | Name | Kind | Notes |
|---|------|------|-------|
| 1 | **Parallel Search** | OpenBot native plugin (Phase-1) | Already in flight; grant `web_search` + `web_fetch` to Research Desk, Search, Deep Dive |
| 2 | **Built-in browser / computer** | OpenBot native (shared Path B) | Validation smoke path; shared browser caveat on one-container |
| 3 | **Google Drive** | OpenBot catalogue plugin (shipped per `validation.md`) | Docs/assets for agency + YMI |
| 4 | **Notion** | OpenBot catalogue plugin (shipped per `validation.md`) | Projects Manager / Campaign Ops SoT |
| 5 | **Gmail** | Connector / MCP — *verify in OpenBot marketplace UI* | PA Desk + Meeting Recap / Loop Closer later |
| 6 | **Google Calendar** | Connector / MCP — *verify in UI* | Right Hand / PA Desk |
| 7 | **GitHub** | Connector / MCP — *verify in UI* | Aurora Infra + Web/Growth |
| 8 | **Slack** | Connector / MCP — *verify in UI* | CoS / Agency Ops collab (dossier must-have pattern) |
| 9 | **Linear** | Connector / MCP — *verify in UI* | Optional eng/task lane |
| 10 | **Context7** | External MCP — *verify in UI* | Library/docs Q&A for Web/Growth / GitHub |
| 11 | **n8n MCP** (`czlonkowski/n8n-mcp`) | External MCP — *verify + review before grant* | Only after aurora-01 n8n ready; pairs with n8n Workflow Builder |
| 12 | **Composio** | OpenBot plugin path (needs `COMPOSIO_API_KEY` env — no UI toggle per `validation.md`) | Meta/Google ads etc. — Aaron secret card only; never paste keys in chat |
| 13 | **Routines grants** | OpenBot admin (`/admin/plugins/routines`) | Enable when recurring digests needed; Path B needs external worker |

**Skills (instructions, not capabilities):** enable `/research-public-web` (Phase-1 Deep Dive), then agency skills as CoS defines under `/admin/skills` — names TBD in UI, do not invent skill IDs.

**Sources for plugin notes:** `PHASE1-CREATE.md`, `validation.md` §8, `AURORA-FLEET-MAPPING.md`, dossier connector guidance (Grok-side; recreate intent only on OpenBot).

---

## CoS quick path (after Phase-1 usable)

1. Confirm Parallel Search smoke on Research Desk / Search.  
2. Open channels from §1 Core set (start Agency Core + Client/YMI + Mentor/Study as Aaron asked).  
3. Create Wave 2A → 2B → 2C coworkers; seat ≤6 per channel.  
4. Recreate §3 customs only when a named lane needs them.  
5. Enable §4 connectors in order; OAuth via secret cards / host env — never chat.

*End. Path: `/workspace/openbot-install/OPENBOT-EXPANDED-ROSTER.md`*
