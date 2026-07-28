#!/usr/bin/env bash
# services.sh — rotate on-demand containers on/off so a small box only runs what's
# needed right now. Any driver (Claude Code / OpenCode / TARS / a human) calls this,
# or equivalently drives the Docker MCP. Frees RAM the moment a job is done.
#
#   ./services.sh list             # available profiles (services you can turn on)
#   ./services.sh status           # what's currently running
#   ./services.sh up   <profile>   # e.g. up browser | docs | search | rag | storage | scratch
#   ./services.sh down <profile>   # stop that profile, reclaim RAM
#   ./services.sh down-all         # stop everything in the pool
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE=(docker compose -f "$DIR/docker-compose.yml")
[ -f "$DIR/.env" ] && COMPOSE+=(--env-file "$DIR/.env")

cmd="${1:-help}"; svc="${2:-}"
case "$cmd" in
  list)     "${COMPOSE[@]}" config --profiles ;;
  status)   "${COMPOSE[@]}" ps ;;
  up)       [ -n "$svc" ] || { echo "usage: services.sh up <profile>" >&2; exit 1; }
            "${COMPOSE[@]}" --profile "$svc" up -d ;;
  down)     [ -n "$svc" ] || { echo "usage: services.sh down <profile>" >&2; exit 1; }
            "${COMPOSE[@]}" --profile "$svc" down ;;
  down-all) "${COMPOSE[@]}" --profile browser --profile docs --profile search \
              --profile rag --profile storage --profile scratch down ;;
  *)        echo "services.sh {list|status|up <profile>|down <profile>|down-all}" ;;
esac
