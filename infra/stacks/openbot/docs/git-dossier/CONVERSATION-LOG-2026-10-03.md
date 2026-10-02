# Conversation log — OpenBot / Aurora arc — 2026-10-03

**Zone:** Australia/Sydney (AEST, UTC+10)  
**Scope:** Facts only. **No secrets**, tokens, or env values.

## Timeline (box-local)

| Time (AEST) | Fact |
|-------------|------|
| Earlier (bring-up) | OpenBot one-container on aurora-01 :3020 Tailscale Serve; Google OAuth; digest pin v0.0.15 `sha256:29daf0d4…`; Aaron admin email configured |
| ~02:14 | Fleet-transfer Wave 1 roster drafted (`fleet-transfer/ROSTER-WAVE1.md`) |
| ~02:15–02:17 | Fleet mapping, expanded roster, plugin catalogue, Phase-1 create checklist written under `/workspace/openbot-install/` |
| ~02:19 | Path B prep scripts + env files on box (`prepare-agui-env.sh`, `aurora-01-agui-runpack.sh`); `MANAGED_AGENT_*` and Composio key presence added to host-bound env (values never logged here) |
| ~02:20 | `PATH-B-AGUI-RUNPACK.md` marked READY / HOLD pending Aaron yes |
| ~02:24 | **Path B LIVE** on aurora-01 (VPN confirmed): `openbot` + `openbot-agent-langgraph` on `openbot-net`; capabilities 200; Serve :3020 intact; Hermes untouched |
| ~02:24 | Coworker runtime blocker update: custom create should work; awaiting CoS Phase-1 managed smoke |
| ~02:24+ | **Search** coworker created; **thread init failing** (likely private-host / allowed-hosts gate for AG-UI) |
| ~02:26–02:27 | Durable pack + Aurora repo branch work started; Bot Forge Top 5 + Right Hand + VPN infra recs captured |

## Architecture facts

- Docker net `openbot-net`: OpenBot `:3001` (host `127.0.0.1:3020`), LangGraph `:4201` **no host publish**
- Managed URL shape: `http://openbot-agent-langgraph:4201/ag-ui`
- Built-in package coworkers still present (Research Desk, General Assistant, etc.)
- Parallel Search **not** in v0.0.15 catalogue on this pin
- OpenBot has **no** Grok-style teams object — use channels + naming `Aurora / <Channel> / <Role>`

## Product / fleet facts

- Phase-1 names: Search, Deep Dive, Chief of Staff, Agency Ops (+ Parallel → Research Desk if available)
- Search: created; thread init broken → fix before bulk Wave 2
- Path B AG-UI already live — do not re-ask Aaron yes for sidecar unless rollback
- Holds: no Ben contact; no live ads; no secrets in chat; Lab isolated; no Hermes bridge this week

## Repo facts (this session)

- `/workspace/openbot-install` — **not** a git repo (working transfer pack)
- `/workspace/Aurora-AI-Agency` — git; remote `https://github.com/az0307/Aurora-AI-Agency.git`; was only `main`
- Target branch for docs: **`infra/openbot-transfer-dossier-2026-10-03`**
- Never commit: `openbot.env`, `agent-langgraph.env`, `secrets.env`, `oauth-credentials.env`
- Ignore hardened: `infra/.gitignore` → `stacks/openbot/**/*.env` with `*.env.example` exception

## Bot Forge / Right Hand / VPN (conversation-derived)

See `RECOMMENDED-ADDITIONS.md` for full lists. Summary:

- **Bot Forge Top 5:** Deep Dive on Research Desk → Agency Core channel+skill → Mentor-Study → Client-YMI → Notion/Drive then Gmail/Calendar/GitHub
- **Right Hand:** Life Continuity Desk; Open-Loop/Decision PA; Mentor & Study spaced-review; Household Admin (pair Tradbot); Weekly Personal Board — skip extra YMI/ads/RH twin
- **VPN next:** keep Serve/Path B; managed URL + optional `AGENT_ENDPOINT_ALLOWED_HOSTS`; Composio UI; Drive OAuth redirect; Routines worker secret; no Hermes bridge; pin images

## Repo policy (Aaron 2026-10-03)

- Aurora-AI-Agency treated as **private** for this pack — **tailnet URLs OK** in dossier docs.
- Still never commit filled env files, oauth credentials, or tokens.
