# Path B — shared LangGraph AG-UI on aurora-01 (custom coworker unlock)

**Status:** READY on box — **HOLD** until Aaron yes (CoS mid-term). Do not VPN-execute until then.  
**Written:** 2026-10-03 ~02:20 AEST · OpenBot Install Manager  
**Pin:** OpenBot `ghcr.io/copilotkit/openbot@sha256:29daf0d4…` (= v0.0.15)  
**LangGraph image:** `ghcr.io/copilotkit/openbot-agent-langgraph@sha256:7ea8406e1637579497cefc60168598fbce448e177c2725d87518adc905b6054f`

## Verdict

| Option | Action |
| --- | --- |
| **A** Built-in coworker radio / in-image Bot | **Impossible** on one-container v0.0.15 — image does not carry `agent-langgraph` / `agent-bot`. No env flag flips that. |
| **B** Sidecar AG-UI + `MANAGED_AGENT_*` | **This pack.** Needs Aaron yes → CoS/IM token into env → VPN run → recreate OpenBot → CoS creates one Phase-1 coworker → IM/CoS confirm. |
| **C** Built-ins + channels + Skills | **Continue now** until B lands. |

## Architecture (Tailscale-only)

```
docker network: openbot-net
  openbot                 :3001 (host publish 127.0.0.1:3020→3001)  Serve :3020
  openbot-agent-langgraph :4201 (NO host publish; only on openbot-net)
```

- OpenBot env: `MANAGED_AGENT_AG_UI_URL=http://openbot-agent-langgraph:4201/ag-ui` + matching `MANAGED_AGENT_TOKEN`
- LangGraph env: same `MANAGED_AGENT_TOKEN`, model key (`OPENAI_API_KEY` + `BOT_PROVIDER`/`BOT_MODEL` from openbot.env), `OPENBOT_TOOL_URL=http://openbot:3001/api/agent-tools/call`
- Never Funnel; never publish 4201 on public/Tailscale IP; optional `127.0.0.1:4201` only for host-side health debug

## Gate order (do not skip)

1. **Aaron yes** for Path B (CoS owns the ask).
2. Generate `MANAGED_AGENT_TOKEN` on box (`openssl rand -base64 32`) → append to `openbot.env` + write `agent-langgraph.env` (both mode 600). Never chat.
3. VPN ships both env files + runs `aurora-01-agui-runpack.sh`.
4. Health: langgraph `/health` from openbot network; OpenBot `/api/capabilities` still 200.
5. CoS UI: create **one** Phase-1 managed coworker (empty endpoint OK once managed URL set) — e.g. `Aurora / Agency Core / Search`.
6. IM priority-ping CoS when create succeeds (or report fail with logs).

## Files

| Path | Purpose |
| --- | --- |
| `/workspace/openbot-install/aurora-01-agui-runpack.sh` | VPN runs on aurora-01 |
| `/workspace/openbot-install/prepare-agui-env.sh` | Box-side: generate token + langgraph env (after Aaron yes) |
| `/workspace/openbot-install/container-images-v0.0.15.json` | Digest pin source |

## Rollback

```bash
# on aurora-01
docker rm -f openbot-agent-langgraph || true
# strip MANAGED_AGENT_* from openbot.env, recreate openbot on openbot-net OR previous runpack
# (built-ins still work with URL unset)
```

## Anti-jobs

No secrets in chat/YAML/git; no Funnel; no Tailscale SSH from Install Manager; no image upgrade without Aaron yes; no Wave-2 customs until one Phase-1 create succeeds.
