#!/usr/bin/env bash
# OpenBot aurora-01 run pack — execute ON aurora-01 only.
# Preconditions: Docker green; 127.0.0.1:3020 free; /opt/aurora/stacks/openbot/openbot.env filled (secrets never in git/chat).
# Bind: 127.0.0.1:3020→3001; then: tailscale serve --bg --https=3020 http://127.0.0.1:3020
set -euo pipefail
IMAGE='ghcr.io/copilotkit/openbot@sha256:29daf0d4f80ec6ff851ad2a5d82736ff3d49d3ff37f6acfde69ffdecd82b28dd'
ENV_FILE="${OPENBOT_ENV_FILE:-/opt/aurora/stacks/openbot/openbot.env}"
NAME=openbot
PORT=3020

if [[ ! -f "$ENV_FILE" ]]; then
  echo "missing env file: $ENV_FILE" >&2
  exit 1
fi
if ss -ltn | grep -qE '127\\.0\\.0\\.1:3020\\s'; then
  echo "port 3020 already in use on loopback" >&2
  exit 1
fi

mkdir -p "$(dirname "$ENV_FILE")"
docker pull "$IMAGE"
docker rm -f "$NAME" 2>/dev/null || true
docker run -d --name "$NAME" \
  --restart unless-stopped \
  -p "127.0.0.1:${PORT}:3001" \
  --env-file "$ENV_FILE" \
  -e EMBEDDED_POSTGRES=on \
  -v openbot-data:/var/lib/postgresql \
  "$IMAGE"

echo "container started; add Serve: tailscale serve --bg --https=${PORT} http://127.0.0.1:${PORT}"
echo "health: curl -sS http://127.0.0.1:${PORT}/api/capabilities"
