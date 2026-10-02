# Install Manager recommendations — Aaron (git dossier)

**When:** 2026-10-03 ~02:30 AEST  
**Host:** https://aurora-01.tail9a65b0.ts.net:3020 · pin v0.0.15 `sha256:29daf0d4…` · Path B langgraph sidecar LIVE  
**No secrets in this file.**

## Status note (blocker)

- **Search** Built-in create succeeded (correct path when `MANAGED_AGENT_*` set).
- Channel smoke: **`Failed to initialize thread`** (also saw 502 while VPN stabilizing).
- Likely next infra fix: `AGENT_ENDPOINT_ALLOWED_HOSTS=openbot-agent-langgraph:4201` → recreate **openbot only** (private AG-UI host otherwise refused). Box openbot.env updated; VPN re-scp + recreate when ready.
- Hold Wave 2 customs until one coworker **run** (not just create) passes.

## Short bullets — additions / updates

### Image upgrade
- Stay on **digest-pinned v0.0.15** until Search thread smoke is green.
- Upgrade later only with Aaron yes: newer tag may add Parallel Search / Built-in Bot runtime; still expect AG-UI sidecar unless release notes say one-container carries Bot.
- Never float `:latest` on aurora-01.

### AG-UI / token in UI
- Env `MANAGED_AGENT_AG_UI_URL` + `MANAGED_AGENT_TOKEN` are **server-side**; they do **not** auto-fill Managed create fields.
- Create coworkers as **Built-in** (empty endpoint) so server bakes managed URL + auto `x-openbot-agent-token`.
- If editing to Managed: endpoint `http://openbot-agent-langgraph:4201/ag-ui`, **auth field blank**, Test connection. Do not paste token into Authorization.
- Optional UI polish (upstream/product): allow Managed+empty when deployment has managed Bot — not available on this pin.

### Drive OAuth client (docs for CoS / Aaron Console)
- Project: enable **Drive API** (`drive.googleapis.com`).
- OAuth Web client; scope `https://www.googleapis.com/auth/drive.readonly`.
- Redirect (exact): `https://aurora-01.tail9a65b0.ts.net:3020/api/plugins/oauth/callback`
- Testing mode: add Aaron as test user; paste client id/secret into `/admin/plugins/google-drive`; Aaron Connect at connected-accounts.
- Can reuse same GCP project as sign-in OAuth; **separate** client or authorized redirect for plugin callback is required.

### Composio — enable first (key already in openbot.env)
Admin `/admin/plugins/composio` — enable apps in this order, then grant actions to Bots, then each person Connect:
1. **Gmail**
2. **Google Calendar**
3. **GitHub**
4. Later: Slack / Linear as needed  
Skip bulk enable; action counts are large — grant narrowly per Bot.

### Plugins order (product)
1. Notion (in progress) → 2. Drive OAuth → 3. Composio apps above → 4. Routines **fire** needs worker + `WORKER_SHARED_SECRET` (grants alone ≠ firing).

### Parallel Search
- Absent on v0.0.15 catalogue — interim = Research Desk + browser; Parallel needs image upgrade research, not Composio.

## Anti-jobs (unchanged)
No Funnel · no Tailscale SSH from IM · no Hermes↔OpenBot bridge · no secrets in git/chat · no Wave 2 until thread smoke green.
