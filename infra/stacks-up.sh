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
#   bash /opt/aurora/stacks-up.sh dashboard    # Homepage start page, 127.0.0.1:3002 (+ tailnet :3002)
#   bash /opt/aurora/stacks-up.sh admin        # Dockge stack manager GUI, 127.0.0.1:5001 (+ tailnet :5001)
#   bash /opt/aurora/stacks-up.sh assistant    # Aurora Assistant control panel, 127.0.0.1:8600 (+ tailnet :8600)
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

usage() { sed -n '2,28p' "$0"; exit 2; }
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
  # umask 077: the temp file holds the secret before the chmod below, so never let it be group/other-readable.
  ( umask 077
  K="$2" V="$v" awk 'BEGIN{k=ENVIRON["K"]; v=ENVIRON["V"]; done=0}
    index($0, k"=")==1 {print k"="v; done=1; next} {print}
    END{if(!done) print k"="v}' "$1" > "$1.tmp" )
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

# save_link NAME URL — record a NON-secret link in $ROOT/state/links (NAME=URL). The phone's
# `a` menu, the widgets and `aurora links` read it, so every "open X" button has a real URL.
LINKS="$ROOT/state/links"
save_link() {
  [ -n "$2" ] && [ "$MODE" != --env-only ] || return 0
  mkdir -p "$ROOT/state"; [ -f "$LINKS" ] || install -m 600 /dev/null "$LINKS"
  setkv "$LINKS" "$1" "$2"
}

ram_check() {  # warn before starting something big on a nearly-full box
  local avail; avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  [ "$avail" -ge 1500 ] || warn "only ${avail} MB RAM available — consider stopping something first"
}

wait_http() {  # wait_http URL NAME — up to ~2 min
  for _ in $(seq 1 24); do curl -fsS -o /dev/null "$1" 2>/dev/null && { say "$2 is healthy"; return 0; }; sleep 5; done
  die "$2 didn't answer at $1 — check: docker compose logs --tail 50"
}

# ts_serve PORT — publish 127.0.0.1:PORT on the tailnet only (HTTPS, never Funnel) and set
# TS_URL=https://<box>.<tailnet>.ts.net:PORT. Returns 1 (TS_URL empty) without a host tailscale.
TS_DNS=""; TS_URL=""
ts_serve() {
  TS_URL=""
  command -v tailscale >/dev/null || return 1
  [ -n "$TS_DNS" ] || TS_DNS=$(tailscale status --json 2>/dev/null | jq -r '.Self.DNSName // empty' | sed 's/\.$//')
  [ -n "$TS_DNS" ] || return 1
  TS_URL="https://$TS_DNS:$1"
  [ "$MODE" = --env-only ] || sudo tailscale serve --bg --https="$1" "http://127.0.0.1:$1" >/dev/null
}

# The router's compose creates aurora-llm. A stack that joins it as `external` before the router
# has ever run would fail, and a plain `docker network create` makes the router refuse the
# network later ("incorrect label"). So pre-create it with the router's own compose labels.
ensure_llm_net() {
  docker network inspect aurora-llm >/dev/null 2>&1 && return 0
  docker network create --label com.docker.compose.project=router \
    --label com.docker.compose.network=llm aurora-llm >/dev/null \
    && warn "created the aurora-llm network; LLM calls fail until the router runs (stacks-up.sh router)"
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
    # Publish n8n on loopback only (the base compose file only `expose`s it), and put it on the
    # router's aurora-llm network so the Aurora workflows reach http://router-litellm-1:4000.
    # The override is picked up automatically because we don't pass -f. Rewritten when it's our
    # own older version (no aurora-llm) so existing boxes get the network too.
    if [ ! -f docker-compose.override.yml ] || { grep -q '^# Written by stacks-up.sh' docker-compose.override.yml \
         && ! grep -q aurora-llm docker-compose.override.yml; }; then
      cat > docker-compose.override.yml <<'EOF'
# Written by stacks-up.sh: n8n on loopback only (SSH tunnel / `tailscale serve`), no Caddy,
# and on the router's aurora-llm network (the Aurora workflows call http://router-litellm-1:4000).
services:
  n8n:
    ports:
      - "127.0.0.1:5678:5678"
    environment:
      # Listen on IPv4: works whether or not the Docker network has IPv6 (n8n's default '::'
      # crash-loops without it). The published port is IPv4 loopback anyway.
      N8N_LISTEN_ADDRESS: 0.0.0.0
    networks: [default, llm]
networks:
  llm:
    name: aurora-llm
    external: true
EOF
      say "wrote docker-compose.override.yml (loopback port + aurora-llm network)"
    fi
    ensure_llm_net
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
    # Telegram deep link: ask Telegram for the bot's @username. The token goes to curl on
    # stdin (-K -), never on argv, and is never printed.
    if have TELEGRAM_BOT_TOKEN; then
      tg=$(printf 'url = "https://api.telegram.org/bot%s/getMe"\n' "$TELEGRAM_BOT_TOKEN" \
            | curl -fsS -m 15 -K - 2>/dev/null | jq -r '.result.username // empty' 2>/dev/null || true)
      if [ -n "$tg" ]; then save_link TELEGRAM "https://t.me/$tg"; say "chat with Hermes: https://t.me/$tg"
      else warn "Telegram didn't accept TELEGRAM_BOT_TOKEN (getMe failed) — re-copy it from @BotFather"; fi
    fi
    # The dashboard stays loopback-only: it rejects any Host header but the one it's bound to
    # (so a tailscale-serve link can't work), and it holds API keys. Reach it through an SSH
    # tunnel instead — the phone's "Hermes dashboard" button does that for you.
    save_link HERMES_DASHBOARD "http://127.0.0.1:9119"
    for _ in $(seq 1 12); do curl -fsS -o /dev/null http://127.0.0.1:9119/ 2>/dev/null && { say "hermes dashboard is up (127.0.0.1:9119 — open it with the phone's 📊 button)"; break; }; sleep 5; done
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
    for _ in $(seq 1 20); do
      [ "$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8931/mcp)" != 000 ] && { say "playwright MCP is listening on 127.0.0.1:8931/mcp"; break; }
      sleep 2
    done
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
    if ts_serve 3020; then
      setkv .env OPENBOT_PUBLIC_URL "$TS_URL"; setkv .env OPENBOT_APP_URL "$TS_URL"
      setkv .env TRUSTED_ORIGINS "http://127.0.0.1:3020,http://localhost:3020,$TS_URL"
      say "tailnet-only: $TS_URL"
    else
      warn "host tailscale CLI not found: OpenBot stays on 127.0.0.1:3020 (SSH tunnel / RDP Firefox)"
    fi
    for c in ollama desktop; do docker ps --format '{{.Names}}' 2>/dev/null | grep -q "$c" && warn "a container matching '$c' is running — OpenBot + it may not fit in 8 GB"; done
    grep -q aurora-llm docker-compose.override.yml 2>/dev/null && ensure_llm_net
    up
    wait_http http://127.0.0.1:3020/api/capabilities openbot
    save_link OPENBOT "${TS_URL:-http://127.0.0.1:3020}"
    say "open OpenBot: ${TS_URL:-http://127.0.0.1:3020 (SSH tunnel / RDP Firefox)}"
    if grep -q '^OPENBOT_SINGLE_USER=true' .env; then warn "single-user mode: anyone on your tailnet who opens it is you. Fine for a personal tailnet; switch to OAuth before sharing the tailnet."; fi
    ;;
  assistant)
    cd "$ROOT/stacks/assistant"
    [ -f .env ] || install -m 600 .env.example .env
    if ts_serve 8600; then setkv .env AURORA_TS_JS "\"$TS_DNS\""
    else setkv .env AURORA_TS_JS "location.hostname"; warn "no host tailscale: launcher tiles use the current hostname"; fi
    save_link ASSISTANT "${TS_URL:-http://127.0.0.1:8600}"
    # The "Chat with Hermes" tile needs the bot's t.me link (saved by `stacks-up.sh hermes`).
    tg=$(sed -n "s/^TELEGRAM=//p" "$LINKS" 2>/dev/null | tr -d "'")
    setkv .env AURORA_TG_JS "\"$tg\""
    docker ps --format '{{.Names}}' | grep -q '^n8n-n8n-1$' || warn "n8n isn't up — the 'send a task' box needs it (aurora start n8n) + the assistant-intake workflow imported & Active"
    up
    wait_http http://127.0.0.1:8600/ assistant
    if [ -n "$TS_URL" ]; then say "open on your phone: $TS_URL"; fi
    ;;
  dashboard)
    cd "$ROOT/stacks/dashboard"
    [ -f .env ] || install -m 600 .env.example .env
    if ts_serve 3002; then
      setkv .env HOMEPAGE_VAR_TS "$TS_DNS"
      setkv .env HOMEPAGE_ALLOWED_HOSTS "127.0.0.1:3002,localhost:3002,$TS_DNS:3002"
    else warn "host tailscale CLI not found: links in the dashboard will point at aurora-01.example.ts.net"; fi
    have TZ && setkv .env TZ "$TZ"
    up
    wait_http http://127.0.0.1:3002 dashboard
    if [ -n "$TS_URL" ]; then say "open on your phone: $TS_URL"; fi
    ;;
  admin)
    cd "$ROOT/stacks/admin"
    mkdir -p data
    ts_serve 5001 || warn "host tailscale CLI not found: Dockge stays on 127.0.0.1:5001"
    up
    wait_http http://127.0.0.1:5001 dockge
    say "open ${TS_URL:-http://127.0.0.1:5001} NOW and create the admin login (first visitor becomes admin)"
    ;;
  monitoring)
    cd "$ROOT/stacks/monitoring"
    up uptime-kuma dozzle
    wait_http http://127.0.0.1:3001 "uptime-kuma"
    # Publish both on the tailnet (the start page links Kuma :3001 and Dozzle :8080). Never Funnel.
    if ts_serve 3001 && ts_serve 8080; then say "open on your phone: https://$TS_DNS:3001 (Kuma) · :8080 (Dozzle logs)"
    else warn "host tailscale CLI not found: Kuma/Dozzle stay on 127.0.0.1:3001 / :8080"; fi
    ;;
  status)
    docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
    free -h | sed -n 1,2p
    ;;
  -h|--help) usage ;;
  *) echo "unknown stack: $STACK" >&2; usage ;;
esac
