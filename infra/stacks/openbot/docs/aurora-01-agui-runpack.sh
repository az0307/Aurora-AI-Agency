#!/usr/bin/env bash
# Run on aurora-01 AFTER env files are in place. Loopback/Tailscale only. No Funnel.
set -euo pipefail

OPENBOT_ENV="${OPENBOT_ENV:-/opt/aurora/stacks/openbot/openbot.env}"
LG_ENV="${LG_ENV:-/opt/aurora/stacks/openbot/agent-langgraph.env}"
OPENBOT_IMAGE="${OPENBOT_IMAGE:-ghcr.io/copilotkit/openbot@sha256:29daf0d4f80ec6ff851ad2a5d82736ff3d49d3ff37f6acfde69ffdecd82b28dd}"
LG_IMAGE="${LG_IMAGE:-ghcr.io/copilotkit/openbot-agent-langgraph@sha256:7ea8406e1637579497cefc60168598fbce448e177c2725d87518adc905b6054f}"
NET="${OPENBOT_NET:-openbot-net}"

for f in "$OPENBOT_ENV" "$LG_ENV"; do
  [[ -f "$f" ]] || { echo "missing $f" >&2; exit 1; }
done
grep -q '^MANAGED_AGENT_AG_UI_URL=http://openbot-agent-langgraph:4201/ag-ui' "$OPENBOT_ENV" \
  || { echo "openbot.env missing MANAGED_AGENT_AG_UI_URL for sidecar" >&2; exit 1; }
grep -q '^MANAGED_AGENT_TOKEN=.\+' "$OPENBOT_ENV" \
  || { echo "openbot.env missing MANAGED_AGENT_TOKEN" >&2; exit 1; }

docker network inspect "$NET" >/dev/null 2>&1 || docker network create "$NET"

# LangGraph first (no host publish — only on docker network)
docker rm -f openbot-agent-langgraph 2>/dev/null || true
docker pull "$LG_IMAGE"
docker run -d --name openbot-agent-langgraph --restart unless-stopped \
  --network "$NET" \
  --env-file "$LG_ENV" \
  "$LG_IMAGE"

# Recreate OpenBot on same network (preserve volume)
docker rm -f openbot 2>/dev/null || true
docker pull "$OPENBOT_IMAGE"
docker run -d --name openbot --restart unless-stopped \
  --network "$NET" \
  -p 127.0.0.1:3020:3001 \
  --env-file "$OPENBOT_ENV" \
  -e EMBEDDED_POSTGRES=on \
  -v openbot-data:/var/lib/postgresql \
  "$OPENBOT_IMAGE"

# Serve usually persists; re-add if missing (no Funnel)
if ! tailscale serve status 2>/dev/null | grep -q ':3020'; then
  tailscale serve --bg --https=3020 http://127.0.0.1:3020 || true
fi

echo "waiting for health…"
for i in $(seq 1 36); do
  if docker exec openbot-agent-langgraph bun -e "await fetch('http://localhost:4201/health')" 2>/dev/null; then
    echo "langgraph /health OK"
    break
  fi
  sleep 5
done
curl -sfS -m 10 http://127.0.0.1:3020/api/capabilities | head -c 400 || true
echo
echo "done — CoS: create one Phase-1 managed coworker; empty endpoint OK"
