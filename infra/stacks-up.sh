#!/usr/bin/env bash
# stacks-up.sh — start ONE stack on the box, with its .env filled from /opt/aurora/secrets.env.
#
# Runs ON THE SERVER as the `aurora` user (it uses sudo only to read the root-owned
# secrets.env). Staged on purpose: the 8 GB box shouldn't start everything at once, and each
# stage should be healthy before the next. Recommended order:
#
#   bash /opt/aurora/stacks-up.sh router       # LiteLLM on 127.0.0.1:4000 (needs a model key)
#   bash /opt/aurora/stacks-up.sh n8n          # Postgres + n8n on 127.0.0.1:5678
#   bash /opt/aurora/stacks-up.sh hermes       # the agent (needs the router + a chat token)
#   bash /opt/aurora/stacks-up.sh tailscale    # private network (needs TS_AUTHKEY)
#   bash /opt/aurora/stacks-up.sh monitoring   # Uptime Kuma + Dozzle
#   bash /opt/aurora/stacks-up.sh computer     # Playwright MCP browser on 127.0.0.1:8931
#   bash /opt/aurora/stacks-up.sh openbot      # OpenBot on 127.0.0.1:3020 (+ Tailscale Serve :3020)
#   bash /opt/aurora/stacks-up.sh status       # what's running + free RAM
#
# Add --env-only to write/refresh the .env without starting anything.
#
# How the .env is built: the stack's .env.example is copied once (so later hand edits to
# non-secret settings survive), then every key that appears in BOTH the example and
# secrets.env is (re)written from secrets.env, plus two renames: ROUTER_API_KEY ←
# LITELLM_MASTER_KEY and GENERIC_TIMEZONE ← TZ. Secret VALUES are never printed; only key
# names and "set/missing". Resulting .env files are mode 600.
#
# Exit codes: 0 ok · 1 missing secret / failed health check · 2 usage.
set -euo pipefail

ROOT="${AURORA_ROOT:-/opt/aurora}"
SECRETS="$ROOT/secrets.env"
STACK="${1:-}"; MODE="${2:-}"

say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[33mWARN\033[0m %s\n' "$*"; }
die()  { printf '\033[31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

usage() { sed -n '2,25p' "$0"; exit 2; }
[ -n "$STACK" ] || usage

# --- Load secrets into this process only (bootstrap.sh wrote them with printf %q) ------
if [ "$STACK" != status ]; then
  sudo test -f "$SECRETS" || die "$SECRETS not found — run ./bootstrap.sh --ship-only from the phone first"
  # Plain shell variables, NOT exported: docker compose and other children never see them;
  # values reach a stack only through the .env files written below.
  # shellcheck disable=SC1090
  . <(sudo cat "$SECRETS")
fi

have() { [ -n "${!1:-}" ]; }            # is secret $1 set? (indirect expansion, no echo)
need() { have "$1" || die "$1 is missing from secrets.env — add it on the phone, then ./bootstrap.sh --ship-only"; }

# setkv FILE KEY VALUE — replace KEY=… (or append) without the value touching argv/sed.
# Values with anything beyond [A-Za-z0-9._:/@+=-] are single-quoted: Docker Compose (and
# dotenv) expand $VARS in unquoted values but treat '…' literally.
setkv() {
  local v="$3"
  case "$v" in *\'*) die "$2 contains a single quote, which .env files can't hold safely — regenerate it";; esac
  [[ "$v" =~ ^[A-Za-z0-9._:/@+=-]*$ ]] || v="'$v'"
  K="$2" V="$v" awk 'BEGIN{k=ENVIRON["K"]; v=ENVIRON["V"]; done=0}
    index($0, k"=")==1 {print k"="v; done=1; next} {print}
    END{if(!done) print k"="v}' "$1" > "$1.tmp"
  mv "$1.tmp" "$1"; chmod 600 "$1"
}

# fill_env EXAMPLE TARGET — create TARGET once, then sync every shared secret into it.
fill_env() {
  local ex="$1" env="$2" k n=0
  [ -f "$env" ] || { install -m 600 "$ex" "$env"; say "created $(realpath --relative-to="$ROOT" "$env")"; }
  for k in $(grep -oE '^[A-Z][A-Z0-9_]*=' "$ex" | tr -d =); do
    if have "$k"; then setkv "$env" "$k" "${!k}"; n=$((n+1)); fi
  done
  if grep -q '^ROUTER_API_KEY=' "$ex" && have LITELLM_MASTER_KEY; then
    setkv "$env" ROUTER_API_KEY "$LITELLM_MASTER_KEY"; n=$((n+1))
  fi
  if grep -q '^GENERIC_TIMEZONE=' "$ex" && have TZ; then setkv "$env" GENERIC_TIMEZONE "$TZ"; fi
  say "$n secret(s) written to $(realpath --relative-to="$ROOT" "$env") (values not shown)"
}

ram_check() {  # warn before starting something big on a nearly-full box
  local avail; avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  [ "$avail" -ge 1500 ] || warn "only ${avail} MB RAM available — consider stopping something first"
}

wait_http() {  # wait_http URL NAME — up to ~2 min
  for _ in $(seq 1 24); do curl -fsS -o /dev/null "$1" 2>/dev/null && { say "$2 is healthy"; return 0; }; sleep 5; done
  die "$2 didn't answer at $1 — check: docker compose logs --tail 50"
}

up() { [ "$MODE" = --env-only ] && { say "env only; not starting"; exit 0; }; ram_check; docker compose up -d "$@"; }

case "$STACK" in
  router)
    cd "$ROOT/stacks/router"
    need LITELLM_MASTER_KEY
    case "$LITELLM_MASTER_KEY" in sk-*) ;; *) die "LITELLM_MASTER_KEY must start with sk- (regenerate it; see secrets.env.example)";; esac
    have OPENROUTER_API_KEY || have ANTHROPIC_API_KEY || have GEMINI_API_KEY || have KIMI_API_KEY || have HF_TOKEN \
      || warn "no model provider key yet — the router starts, but every model call will fail"
    [ -f config.yaml ] || { cp config.yaml.example config.yaml; say "created stacks/router/config.yaml"; }
    fill_env .env.example .env
    up
    wait_http http://127.0.0.1:4000/health/liveliness router
    echo "  Test (prints only the model count): curl -s -H \"Authorization: Bearer \$LITELLM_MASTER_KEY\" 127.0.0.1:4000/v1/models | jq '.data|length'"
    ;;
  n8n)
    cd "$ROOT/stacks/n8n"
    need POSTGRES_PASSWORD; need N8N_ENCRYPTION_KEY
    new=0; [ -f .env ] || new=1
    fill_env .env.example .env
    if [ "$new" = 1 ] && ! have N8N_DOMAIN; then
      # No public domain yet: plain http on loopback, reached by SSH tunnel / Tailscale serve.
      setkv .env N8N_HOST localhost; setkv .env N8N_PROTOCOL http
      setkv .env WEBHOOK_URL http://localhost:5678/; setkv .env N8N_DOMAIN ""
    fi
    # Publish n8n on loopback only (the base compose file only `expose`s it). The override is
    # picked up automatically because we don't pass -f.
    [ -f docker-compose.override.yml ] || cat > docker-compose.override.yml <<'EOF'
# Written by stacks-up.sh: n8n on loopback only (SSH tunnel / `tailscale serve`), no Caddy.
services:
  n8n:
    ports:
      - "127.0.0.1:5678:5678"
EOF
    up postgres n8n
    wait_http http://127.0.0.1:5678/healthz n8n
    ;;
  hermes)
    cd "$ROOT/stacks/hermes"
    need LITELLM_MASTER_KEY
    curl -fsS -o /dev/null http://127.0.0.1:4000/health/liveliness 2>/dev/null \
      || warn "router isn't answering on 127.0.0.1:4000 — start it first: stacks-up.sh router"
    have TELEGRAM_BOT_TOKEN || have DISCORD_BOT_TOKEN || have SLACK_BOT_TOKEN \
      || warn "no chat token (Telegram/Discord/Slack) — Hermes will start but nobody can talk to it"
    mkdir -p data/workspace
    [ -f data/config.yaml ] || { cp config.yaml.example data/config.yaml; say "created stacks/hermes/data/config.yaml"; }
    fill_env .env.example data/.env
    up
    ;;
  tailscale)
    cd "$ROOT/stacks/tailscale"
    need TS_AUTHKEY
    fill_env .env.example .env
    up
    echo "  Next: check the admin console for aurora-01, then SETUP.md §8 (remove public SSH)."
    ;;
  computer)
    cd "$ROOT/stacks/computer"
    fill_env .env.example .env
    up            # default services only: the Playwright MCP browser (the desktop is on demand)
    # A bare GET on the MCP endpoint answers 400 by design, so only check the port is open.
    sleep 3; curl -s -o /dev/null http://127.0.0.1:8931/mcp && say "playwright MCP is listening on 127.0.0.1:8931/mcp"
    ;;
  openbot)
    cd "$ROOT/stacks/openbot"
    need INTELLIGENCE_API_KEY
    fill_env .env.example .env
    # Encryption key for the credentials OpenBot stores: generated ON the box, once, and kept
    # only in this .env (back it up with the stack; losing it means re-entering those keys).
    grep -qE '^KEY_ENCRYPTION_KEY=.+' .env || { setkv .env KEY_ENCRYPTION_KEY "$(openssl rand -base64 32)"; say "generated KEY_ENCRYPTION_KEY"; }
    if ! have OPENAI_API_KEY && have LITELLM_MASTER_KEY; then
      # No OpenAI key: send OpenBot's OpenAI-style calls through the router instead, over the
      # router's private Docker network (the router's host port is loopback-only).
      setkv .env OPENAI_API_KEY "$LITELLM_MASTER_KEY"
      setkv .env OPENAI_BASE_URL http://litellm:4000/v1
      cat > docker-compose.override.yml <<'EOF'
# Written by stacks-up.sh: reach the LiteLLM router as http://litellm:4000 (no OpenAI key set).
services:
  openbot:
    networks: [default, llm]
networks:
  llm:
    name: aurora-llm
    external: true
EOF
      say "no OPENAI_API_KEY: OpenBot will use the router (model names must exist there, e.g. gpt, general)"
    fi
    if command -v tailscale >/dev/null && dns=$(tailscale status --json 2>/dev/null | jq -r '.Self.DNSName // empty' | sed 's/\.$//') && [ -n "$dns" ]; then
      url="https://$dns:3020"
      setkv .env OPENBOT_PUBLIC_URL "$url"; setkv .env OPENBOT_APP_URL "$url"
      setkv .env TRUSTED_ORIGINS "http://127.0.0.1:3020,http://localhost:3020,$url"
      [ "$MODE" = --env-only ] || { sudo tailscale serve --bg --https=3020 http://127.0.0.1:3020 >/dev/null && say "tailnet-only: $url"; }
    else
      warn "host tailscale CLI not found: OpenBot stays on 127.0.0.1:3020 (SSH tunnel / RDP Firefox)"
    fi
    for c in ollama desktop; do docker ps --format '{{.Names}}' 2>/dev/null | grep -q "$c" && warn "a container matching '$c' is running — OpenBot + it may not fit in 8 GB"; done
    up
    wait_http http://127.0.0.1:3020/api/capabilities openbot
    grep -q '^OPENBOT_SINGLE_USER=true' .env && warn "single-user mode: anyone on your tailnet who opens it is you. Fine for a personal tailnet; switch to OAuth before sharing the tailnet."
    ;;
  monitoring)
    cd "$ROOT/stacks/monitoring"
    up uptime-kuma dozzle
    wait_http http://127.0.0.1:3001 "uptime-kuma"
    ;;
  status)
    docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
    free -h | sed -n 1,2p
    ;;
  -h|--help) usage ;;
  *) echo "unknown stack: $STACK" >&2; usage ;;
esac
