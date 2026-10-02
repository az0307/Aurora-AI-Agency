#!/usr/bin/env bash
# Box-side only. Run AFTER Aaron yes for Path B. Never print secret values.
set -euo pipefail
OPENBOT_ENV="${OPENBOT_ENV:-/workspace/Aurora-AI-Agency/infra/stacks/openbot/openbot.env}"
LG_ENV="${LG_ENV:-/workspace/Aurora-AI-Agency/infra/stacks/openbot/agent-langgraph.env}"
STACK_DIR="$(dirname "$OPENBOT_ENV")"
mkdir -p "$STACK_DIR"
umask 077

if [[ ! -f "$OPENBOT_ENV" ]]; then
  echo "missing $OPENBOT_ENV" >&2
  exit 1
fi

# Generate or reuse MANAGED_AGENT_TOKEN (do not echo value)
if grep -q '^MANAGED_AGENT_TOKEN=.\+' "$OPENBOT_ENV" 2>/dev/null; then
  echo "MANAGED_AGENT_TOKEN already set in openbot.env — reusing"
else
  TOKEN="$(openssl rand -base64 32)"
  {
    echo ""
    echo "# Path B AG-UI — added $(date -Iseconds)"
    echo "MANAGED_AGENT_AG_UI_URL=http://openbot-agent-langgraph:4201/ag-ui"
    echo "MANAGED_AGENT_TOKEN=${TOKEN}"
  } >> "$OPENBOT_ENV"
  chmod 600 "$OPENBOT_ENV"
  echo "appended MANAGED_AGENT_* to openbot.env"
fi

# Pull model settings from openbot.env without printing values
get_kv() { grep -E "^${1}=" "$OPENBOT_ENV" | head -1 | cut -d= -f2-; }
OPENAI_API_KEY_VAL="$(get_kv OPENAI_API_KEY || true)"
BOT_PROVIDER_VAL="$(get_kv BOT_PROVIDER || true)"
BOT_MODEL_VAL="$(get_kv BOT_MODEL || true)"
TOKEN_VAL="$(get_kv MANAGED_AGENT_TOKEN)"

if [[ -z "${OPENAI_API_KEY_VAL}" ]]; then
  echo "OPENAI_API_KEY missing in openbot.env — abort" >&2
  exit 1
fi
if [[ -z "${TOKEN_VAL}" ]]; then
  echo "MANAGED_AGENT_TOKEN missing after append — abort" >&2
  exit 1
fi

cat > "$LG_ENV" << INNER
# agent-langgraph sidecar for OpenBot Path B — mode 600. Do not commit.
MANAGED_AGENT_TOKEN=${TOKEN_VAL}
BOT_PROVIDER=${BOT_PROVIDER_VAL:-openai}
BOT_MODEL=${BOT_MODEL_VAL:-gpt-4.1}
OPENAI_API_KEY=${OPENAI_API_KEY_VAL}
OPENBOT_TOOL_URL=http://openbot:3001/api/agent-tools/call
INNER
chmod 600 "$LG_ENV"
echo "wrote $LG_ENV (600)"
echo "next: VPN ships openbot.env + agent-langgraph.env and runs aurora-01-agui-runpack.sh"
