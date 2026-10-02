# Aurora Grok Bot fleet → OpenBot mapping (draft 2026-10-03)

## Auth / session (current)
- Serve: https://aurora-01.tail9a65b0.ts.net:3020
- Auth: Google OAuth only; `OPENBOT_SINGLE_USER` absent
- Session: Better Auth cookies after Google sign-in; unauthenticated `/api/agents` → **401**
- Admin: `INITIAL_ADMIN_EMAILS=REPLACE_WITH_AARON_GOOGLE_EMAIL` (must sign in once)
- **No agent/session cookie on Install Manager** — cannot create coworkers via API from this box without Aaron’s signed-in session

## Create path
| What | How |
| --- | --- |
| Coworkers (Bots) | **UI primary:** `/agents` → create (name, title, role, visibility, optional AG-UI endpoint) |
| API | Authenticated REST under `/api/agents` (401 without session). `POST /api/agents/test-connection` for endpoint check. Prefer UI for first fleet; no bulk-import tool in install pack |
| Package agents | Built into image via tenant package (`examples/fintech`); edit needs image rebuild / custom tenant — **not** for day-1 |
| Teams (Grok-style) | **No first-class “teams” object in OpenBot.** Closest: **channels** (per-coworker threads), admin **grants** (MCP/skills per Bot), and human grouping by naming/title. Do not expect sidebar “teams” like Grok Bot |

## Path B caveat (aurora-01 one-container)
- `MANAGED_AGENT_AG_UI_URL` typically **unset** — product-created coworkers without a custom AG-UI endpoint may be **refused**
- Built-in package coworkers (12) already registered and runnable via Intelligence mode
- New “search / deep-dive” bots: prefer **enable Parallel Search plugin + grant to Research Desk** (and/or create UI coworkers that use built-in Intelligence Bot if managed URL exists), not invent AG-UI hosts yet

## Existing agents on live instance
**Built-in (from `/api/copilotkit/info`, no auth):** 12  
`general-assistant`, `knowledge`, `research-desk`, `expense-review`, `feedback-digest`, `interview-notes`, `meeting-follow-ups`, `onboarding-buddy`, `oncall-handover`, `release-notes`, `ticket-triage`, `vendor-review`

User-created coworker list: **unknown until Aaron signs in** (`GET /api/agents` → 401)

## Recommended mapping (phase 1 — do not 1:1 clone 52 bots)

### Team A — Core ops (map to OpenBot channels + reuse built-ins)
| Aurora Grok Bot | OpenBot |
| --- | --- |
| Chief of Staff / Right Hand / PA Desk | `general-assistant` + new coworker “Chief of Staff” (role: triage, escalate to Aaron) |
| OpenBot Install Manager / VPN Manager / Aurora Infra | new coworker “Infra Desk” (ops runbooks; no Tailscale SSH claims) |
| Bot Forge | defer (meta) or “Bot Forge” skill later |

### Team B — Research / search / deep-dive (Aaron asked)
| Need | OpenBot |
| --- | --- |
| Search bot | Grant Parallel `web_search`+`web_fetch` to **Research Desk**; optional new coworker “Search” with same grants + research skill |
| Deep-dive bot | New coworker “Deep Dive” — longer role (multi-source, cite URLs, flag gaps); same Parallel grants; use `/research-public-web` |

### Team C — Agency delivery
| Aurora | OpenBot |
| --- | --- |
| Agency Ops / Agency Delivery / Agency Core / Projects Manager | `meeting-follow-ups` + new “Agency Ops” coworker |
| YMI Account / Client Reporting / Ads Manager / Campaign Ops | new “YMI Account” + `vendor-review` / reporting role coworkers |
| Content Writer / Content Engine / SEO & AEO / Social* / LinkedIn* / Web Growth / Distribution / Marketing* | collapse into 2–3: “Content”, “Social/LinkedIn”, “Growth/SEO” |

### Team D — Lab / security (careful)
| Aurora | OpenBot |
| --- | --- |
| S10 / Lab / NetHunter / Toolkit / Hygiene | **defer** or private coworker with strict `/admin/boundaries` — not public fleet day-1 |

### Team E — Personal
| Aurora | OpenBot |
| --- | --- |
| Tradbot / Study* / Hobby* / Morning Newspaper | personal private coworkers or stay on Grok until OpenBot smoke passes |

## Create order (CoS-driven, Aaron signs in)
1. Aaron Google sign-in smoke as admin
2. Admin → Plugins → add **Parallel Search**; grant Research Desk (+ Search / Deep Dive when created)
3. `/agents` create: **Search**, **Deep Dive**, **Chief of Staff**, **Agency Ops** (minimum viable)
4. Start a channel per coworker; pin naming convention `Aurora / <team> / <role>`
5. Only then expand agency/social clones; do not bulk-transfer all 52

## Still needed from CoS / Aaron
1. Aaron completes Google sign-in (unblocks `/api/agents` and UI create)
2. Confirm phase-1 MVP list (Search + Deep Dive + CoS + Agency Ops) vs full fleet
3. Parallel: anonymous OK vs API-key secret card
4. Whether any coworker needs a **custom AG-UI endpoint** (path B has no managed langgraph) — if yes, engineering work; else use Intelligence built-ins + Parallel

## Status 2026-10-03 ~02:15 AEST
- Aaron sign-in DONE
- Phase-1 MVP APPROVED; CoS creating via UI
- See PHASE1-CREATE.md
