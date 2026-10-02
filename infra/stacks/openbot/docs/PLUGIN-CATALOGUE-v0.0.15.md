# OpenBot v0.0.15 plugin / MCP / limits (aurora-01 one-container)

Pinned image: `ghcr.io/copilotkit/openbot@sha256:29daf0d4…` (`:v0.0.15`)  
Source: upstream docs at tag `v0.0.15` + live env presence checks 2026-10-03.

## 1) Catalogue available (Admin → Plugins)

| Entry | What | Notes |
| --- | --- | --- |
| **Google Drive** | Per-person read-only Drive | Admin enables + pastes Google OAuth client at `/admin/plugins/google-drive`; each user Connects at `/settings/connected-accounts`. Redirect: `<OPENBOT_PUBLIC_URL>/api/plugins/oauth/callback` |
| **Notion** | Per-person Notion MCP (read+write tools) | Enable at `/admin/plugins/notion`; DCR — no client secret to paste. Admin must Connect own Notion before Refresh tools |
| **Composio** | Brokered apps (Slack, Linear, Gmail, HubSpot, …) | Shows under “More apps” only as a hint until `COMPOSIO_API_KEY` is set in **env** (no UI to set key). Then enable apps + grant actions per Bot |
| **Routines** | `create_routine` / `update_routine` / `delete_routine` | Catalogue entry; grant per Bot at `/admin/plugins/routines`. Needs routine **worker** (`WORKER_SHARED_SECRET` + worker process) — **ABSENT** on current openbot.env |
| **Custom MCP** | Admin-added servers | Allowed if URL passes target checks; unknown/custom tools classified as **writes**; fail-closed gateway. **Do not add unreviewed servers** (IM anti-job) |
| **Skills** | Personal `/skills` + Admin `/admin/skills` | Instructions only — not capabilities. Grant deployment skills to Bots |
| **Browser / shell / files** | Per-Bot computer via gateway | Built-in; governed by `/admin/boundaries` + audit — not a “plugin” |

### Not in v0.0.15 docs (do not assume on this pin)
- **Parallel Search** (`web_search` / `web_fetch`) — documented on newer main; **no `docs/parallel-research.md` on tag v0.0.15**. If UI does not show Parallel, Search/Deep Dive use **browser** research + Research Desk role, or plan image upgrade later.

## 2) Safe-to-enable without new secrets vs needs secret cards

### Safe-ish without new secret cards (still needs admin UI + user OAuth consents)
| Enable | Secret card? | Catch |
| --- | --- | --- |
| **Notion** connector | No env secret | Per-user Notion OAuth consent; write tools exist — grant **reads first** |
| **Routines** catalogue entry | No (tools only) | Worker not running → routines won’t fire; don’t promise schedules until VPN adds worker |
| **Deployment / personal skills** | No | Text only |
| **Boundaries presets** | No | Tighten before broad MCP grants |
| Built-in package coworkers | No | Already present |

### Needs secrets / infra before useful
| Item | Need |
| --- | --- |
| **Google Drive** | New Google Cloud OAuth Web client (or reuse) + secret into plugin UI (encrypted); Drive API enabled; redirect `https://aurora-01.tail9a65b0.ts.net:3020/api/plugins/oauth/callback`; test users if app in Testing |
| **Composio marketplace** | `COMPOSIO_API_KEY` in openbot.env (env-only) → VPN recreate; then enable apps; each person Connects |
| **Routines that fire** | `WORKER_SHARED_SECRET` (+ worker/CronJob) — not on host yet |
| **Custom MCP** | Reviewed URL + any vendor key via `/admin/credentials`; IM: never unreviewed |
| **Parallel (if appears after upgrade)** | Anonymous OK first; API key only if rate-limited |

### Current env (presence)
- `COMPOSIO_API_KEY` **ABSENT**
- `MANAGED_AGENT_AG_UI_URL` **ABSENT**
- `WORKER_SHARED_SECRET` **ABSENT**

## 3) Hard limits

| Limit | Value | Source |
| --- | --- | --- |
| Enabled **routines** per person | **20** | docs/routines.md |
| Routine min interval | **15 minutes** | same |
| Routine auto-disable | 10 consecutive failures | same |
| Coworker count | **No documented hard cap** | coworkers.md / README |
| Channels | **No documented hard cap** | soft: Intelligence threads + ops load |
| Soft ops limits (aurora-01) | Host RAM/CPU; each Bot computer costs resources; Composio apps can expose **100+ tools** — grant selectively |

## 4) Wave 2+ create path — CRITICAL

**Confirmed intent:** public coworkers, **empty AG-UI endpoint**, built-in package + UI only.

**Path B risk:** with `MANAGED_AGENT_AG_UI_URL` unset, upstream says product-created coworkers **without** a custom endpoint are **refused**. Built-in package agents still work.

**Before bulk Wave 2:** CoS must confirm one Phase-1 UI create (Search or Deep Dive) **saved and runnable**. If create fails:
1. Prefer duplicate/edit built-ins + roles/skills/grants, **or**
2. Escalate: set managed AG-UI / sidecar / image upgrade (needs VPN + Aaron yes)

Do **not** assume empty-AG-UI bulk create works until one succeeds.

## Recommended enable order (expanded scope)
1. Finish Phase-1 coworkers + channels; verify create works
2. Notion (reads) for Agency Ops / CoS
3. Google Drive when OAuth client ready
4. Composio only after `COMPOSIO_API_KEY` secret + recreate — enable **few** apps (Gmail/Slack/Linear), grant reads first
5. Routines grants only after worker exists
6. Custom MCP: none unless Aaron + review
7. Parallel: only if present in UI on this pin; else browser research
