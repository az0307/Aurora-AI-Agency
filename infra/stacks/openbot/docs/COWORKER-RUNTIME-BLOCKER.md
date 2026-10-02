**UPDATE 2026-10-03 ~02:24 AEST:** Path B LIVE on aurora-01 (VPN confirmed). Custom create should work — awaiting CoS one Phase-1 managed coworker smoke.

# Blocker: custom coworker create (2026-10-03)

## Confirmed (CoS UI)
- Built-in radio disabled: "this deployment has no Bot of its own for a coworker to run on."
- Managed requires AG-UI endpoint.
- Catalogue: Google Drive, Notion, Routines only (no Parallel). Composio needs env key.

## Root cause (upstream v0.0.15 deployment.md)
One-container image **does not carry** `agent-langgraph` or `agent-bot`.  
`MANAGED_AGENT_AG_UI_URL` must stay unset unless a Bot is reachable from the container.  
Product-created coworkers with empty endpoint are **refused** by design on path B.

## Recommendation

| Option | Verdict |
| --- | --- |
| **A** Enable in-image built-in Bot | **Not available** on this pin/image |
| **B** Shared LangGraph/AG-UI on aurora-01 + `MANAGED_AGENT_AG_UI_URL` (+ token) | **Correct mid-term fix** — needs Aaron yes + VPN (sidecar or compose/Helm). Not zero-touch |
| **C** Phase-1 customs wait; use shipped built-ins | **Do this now** |

### Immediate (C)
Use built-ins only:
- **Research Desk** → search / deep-dive (browser computer for public web; no Parallel on pin)
- **General Assistant** → Chief of Staff / triage stand-in
- **Knowledge** / **Meeting Follow-ups** / others → agency adjacent
Channels named `Aurora / …` as “teams”. Skills for standing roles. No custom coworker create until B.

### Mid-term (B) — escalate to VPN when Aaron yes
**Pack ready:** `PATH-B-AGUI-RUNPACK.md` + `prepare-agui-env.sh` + `aurora-01-agui-runpack.sh`
1. Aaron yes → run `prepare-agui-env.sh` on box (token + `agent-langgraph.env` 600)
2. VPN ships both env files; runs `aurora-01-agui-runpack.sh` (docker net `openbot-net`, no 4201 publish)
3. Retest capabilities; CoS create **one** Phase-1 managed coworker
4. Then Wave-2 / remaining Phase-1 names

### Do not
- Paste laptop `http://localhost:4201/ag-ui` into production env
- Expect COMPOSIO or Parallel to unlock coworker create (they do not)
- Add unreviewed custom MCP

## COMPOSIO_API_KEY / Parallel vs search
| Ask | Answer |
| --- | --- |
| Does COMPOSIO unlock search? | **No** — unlocks brokered apps (Gmail/Slack/…) after env key + recreate |
| Does Parallel unlock search? | **Not on v0.0.15** — not in catalogue; needs newer image or browser research |
| Search now | Research Desk + shared Chromium (Ask: open URL / research) |

## Plugins while blocked
- Skills review: yes
- Routines grants: yes; **firing** needs worker (separate)
- Notion: enable + Aaron Connect (no env secret)
- Drive: needs Google OAuth client for plugin redirect `…/api/plugins/oauth/callback`
- Composio: only after Aaron supplies COMPOSIO_API_KEY via secret path → VPN recreate
