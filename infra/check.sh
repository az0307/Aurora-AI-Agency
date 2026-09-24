#!/usr/bin/env bash
# check.sh — confirm the whole Aurora box is healthy, in one command. Run ON the server:
#
#   bash /opt/aurora/check.sh           # free: containers, ports, router, Hermes, MCP, disk/RAM
#   bash /opt/aurora/check.sh --live    # + ask every job alias "reply OK" (a few cents total)
#
# Read-only: it never starts, stops or changes anything. Exit code 0 = all good,
# 1 = something needs fixing (each ✗ line says what). From a phone: `ssh aurora-01
# bash /opt/aurora/check.sh`, or ask Hermes "run the box check".
set -u

DIR=$(cd "$(dirname "$0")" && pwd)          # /opt/aurora on the box (= infra/ in the repo)
LIVE=0; [ "${1:-}" = "--live" ] && LIVE=1
ROUTER=http://127.0.0.1:4000

if [ -t 1 ]; then G=$'\e[32m'; R=$'\e[31m'; Y=$'\e[33m'; B=$'\e[1m'; D=$'\e[2m'; N=$'\e[0m'
else G=; R=; Y=; B=; D=; N=; fi
FAIL=0; WARN=0
ok()   { printf '  %s✓%s %s\n' "$G" "$N" "$*"; }
bad()  { printf '  %s✗%s %s\n' "$R" "$N" "$*"; FAIL=$((FAIL+1)); }
warn() { printf '  %s!%s %s\n' "$Y" "$N" "$*"; WARN=$((WARN+1)); }
info() { printf '  %s·%s %s\n' "$D" "$N" "$*"; }
head_() { printf '\n%s%s%s\n' "$B" "$*" "$N"; }

# Read one KEY=value from an .env file without sourcing it (values can hold anything).
# Drops an inline "  # comment" and surrounding spaces, so `KEY=   # note` reads as empty.
envval() { [ -f "$1" ] && sed -n "s/^$2=//p" "$1" | tail -1 | sed 's/[[:space:]]#.*$//; s/^#.*$//; s/^[[:space:]]*//; s/[[:space:]]*$//' | tr -d '"'"'"; }

for f in "$DIR/stacks/router/.env" "$DIR/stacks/hermes/data/.env"; do
  if [ -e "$f" ] && [ ! -r "$f" ]; then
    printf '%s!%s Can'"'"'t read %s as %s — key checks will be wrong. Run: sudo bash %s\n' "$Y" "$N" "$f" "$(id -un)" "$0"
  fi
done

# ----------------------------------------------------------------------------- host
head_ "Host"
mem_avail=$(awk '/MemAvailable/{printf "%d", $2/1024}' /proc/meminfo)
mem_total=$(awk '/MemTotal/{printf "%d", $2/1024}' /proc/meminfo)
if [ "$mem_avail" -lt 700 ]; then bad "RAM: only ${mem_avail} MB free of ${mem_total} MB — stop an on-demand stack (ollama / computer desktop)"
elif [ "$mem_avail" -lt 1500 ]; then warn "RAM: ${mem_avail} MB free of ${mem_total} MB — not enough to also start the desktop or a local model"
else ok "RAM: ${mem_avail} MB free of ${mem_total} MB"; fi
disk_pct=$(df -P / | awk 'NR==2{gsub("%","",$5); print $5}')
if [ "$disk_pct" -ge 90 ]; then bad "Disk: ${disk_pct}% used — run: docker system prune -af (removes unused images)"
elif [ "$disk_pct" -ge 75 ]; then warn "Disk: ${disk_pct}% used"
else ok "Disk: ${disk_pct}% used"; fi
swap=$(awk '/SwapTotal/{printf "%d", $2/1024}' /proc/meminfo)
[ "$swap" -gt 0 ] && ok "Swap: ${swap} MB" || warn "No swap — a memory spike will kill a container instead of slowing down"

# ------------------------------------------------------------------------- containers
head_ "Containers"
if ! command -v docker >/dev/null || ! docker info >/dev/null 2>&1; then
  bad "Docker isn't running (or this user isn't in the docker group)"
else
  ps_out=$(docker ps -a --format '{{.Names}}|{{.Image}}|{{.State}}|{{.Status}}')
  need() {  # need <label> <image-substring> <required|optional> <how to start>
    line=$(printf '%s\n' "$ps_out" | awk -F'|' -v img="$2" 'index($2,img){print; exit}')
    if [ -z "$line" ]; then
      [ "$3" = required ] && bad "$1: not created — $4" || info "$1: not installed ($4)"
      return
    fi
    name=${line%%|*}; state=$(echo "$line" | cut -d'|' -f3); status=$(echo "$line" | cut -d'|' -f4)
    case "$state/$status" in
      running/*unhealthy*) bad "$1 ($name): running but UNHEALTHY — docker logs $name" ;;
      running/*)           ok  "$1 ($name): $status" ;;
      restarting/*)        bad "$1 ($name): crash-looping — docker logs --tail 50 $name" ;;
      *)                   [ "$3" = required ] && bad "$1 ($name): $state — $4" || info "$1 ($name): $state" ;;
    esac
  }
  need "LLM router"      "berriai/litellm"            required "cd $DIR/stacks/router && docker compose up -d"
  need "n8n"             "n8nio/n8n"                  required "cd $DIR/stacks/n8n && docker compose up -d"
  need "Hermes agent"    "nousresearch/hermes-agent"  required "cd $DIR/stacks/hermes && docker compose up -d"
  need "Tailscale"       "tailscale/tailscale"        required "cd $DIR/stacks/tailscale && docker compose up -d"
  need "Playwright MCP"  "playwright/mcp"             optional "cd $DIR/stacks/computer && docker compose up -d"
  need "Uptime Kuma"     "uptime-kuma"                optional "monitoring stack"
  need "Ollama"          "ollama/ollama"              optional "on demand"
  need "Computer desktop" "computer-use-demo"         optional "on demand: --profile desktop"
  crashed=$(printf '%s\n' "$ps_out" | awk -F'|' '$3=="restarting"{print $1}')
  [ -n "$crashed" ] && bad "Crash-looping: $(echo $crashed)"
fi

# ---------------------------------------------------------------------- open ports
head_ "Exposure (what the internet could reach)"
if command -v ss >/dev/null; then
  public=$(ss -ltnH 2>/dev/null | awk '{print $4}' | grep -E '^(0\.0\.0\.0|\*|\[::\]):' | grep -vE ':(22)$' | sort -u)
  if [ -n "$public" ]; then
    bad "Listening on ALL interfaces (bind these to 127.0.0.1): $(echo $public)"
  else ok "Only SSH listens publicly; every service is loopback / Tailscale only"; fi
  info "The Hetzner cloud firewall is the second wall: keep it SSH-only (or nothing, once Tailscale works)"
else warn "ss not found — can't check listening ports"; fi

# --------------------------------------------------------------------------- router
head_ "LLM router"
KEY=$(envval "$DIR/stacks/router/.env" LITELLM_MASTER_KEY)
if curl -fsS -m 5 "$ROUTER/health/liveliness" >/dev/null 2>&1; then
  ok "Router answers on $ROUTER"
  if [ -z "$KEY" ]; then warn "No LITELLM_MASTER_KEY in stacks/router/.env — can't list models"
  else
    models=$(curl -fsS -m 10 -H "Authorization: Bearer $KEY" "$ROUTER/v1/models" 2>/dev/null | tr ',' '\n' | sed -n 's/.*"id": *"\([^"]*\)".*/\1/p')
    missing=""
    for a in general general-free code code-free reason fast vision search research hermes auto auto-free; do
      printf '%s\n' "$models" | grep -qx "$a" || missing="$missing $a"
    done
    [ -z "$missing" ] && ok "All job aliases loaded ($(printf '%s\n' "$models" | grep -c .) models total)" \
                      || bad "Missing aliases:$missing — cp config.yaml.example config.yaml, then docker compose restart"
  fi
  # Keys the chains need. Empty = that hop is skipped (it errors and falls through).
  RENV="$DIR/stacks/router/.env"
  [ -n "$(envval "$RENV" OPENROUTER_API_KEY)" ] && ok "OPENROUTER_API_KEY set" \
    || bad "OPENROUTER_API_KEY empty in stacks/router/.env — nearly every chain needs it"
  [ -n "$(envval "$RENV" ANTHROPIC_API_KEY)" ] && ok "ANTHROPIC_API_KEY set" \
    || warn "ANTHROPIC_API_KEY empty — Claude hops are skipped, so general/code/reason start at their 2nd model"
  for k in KIMI_API_KEY HF_TOKEN; do
    [ -n "$(envval "$RENV" $k)" ] && ok "$k set" || info "$k empty — its fallback hop is skipped (fine)"
  done
else
  bad "Router not answering on $ROUTER — docker logs \$(docker ps -qf ancestor=ghcr.io/berriai/litellm:main-stable)"
fi

if [ "$LIVE" = 1 ] && [ -n "$KEY" ]; then
  head_ "Live test: each job alias answers (who answered = first healthy model in its chain)"
  timeouts=0
  for a in general general-free code code-free reason fast vision search hermes; do
    out=$(curl -sS -m 60 -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
      "$ROUTER/v1/chat/completions" \
      -d "{\"model\":\"$a\",\"max_tokens\":8,\"messages\":[{\"role\":\"user\",\"content\":\"Reply with just: OK\"}]}" 2>&1)
    who=$(printf '%s' "$out" | sed -n 's/.*"model": *"\([^"]*\)".*/\1/p' | head -1)
    if printf '%s' "$out" | grep -q '"choices"'; then ok "$(printf '%-13s' "$a") → ${who:-answered}"
    else
      bad "$(printf '%-13s' "$a") → $(printf '%s' "$out" | tr '\n' ' ' | cut -c1-140)"
      case "$out" in *"timed out"*) timeouts=$((timeouts+1)) ;; *) timeouts=0 ;; esac
      if [ "$timeouts" -ge 2 ]; then
        bad "Two aliases timed out in a row — the box probably can't reach the providers; stopping the live test"
        break
      fi
    fi
  done
fi

# --------------------------------------------------------------------------- hermes
head_ "Hermes agent"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx hermes; then
  if docker exec hermes hermes doctor >/tmp/aurora-hermes-doctor.txt 2>&1; then
    ok "hermes doctor: no problems"
  else bad "hermes doctor found problems — see /tmp/aurora-hermes-doctor.txt (try: docker exec hermes hermes doctor --fix)"; fi
  HENV="$DIR/stacks/hermes/data/.env"
  [ "$(envval "$HENV" GATEWAY_ALLOW_ALL_USERS)" = "true" ] \
    && bad "GATEWAY_ALLOW_ALL_USERS=true — ANYONE who finds the bot can use it. Set false + *_ALLOWED_USERS" \
    || ok "Bot answers only allow-listed users"
  n=0; for p in TELEGRAM_BOT_TOKEN DISCORD_BOT_TOKEN SLACK_BOT_TOKEN; do [ -n "$(envval "$HENV" $p)" ] && n=$((n+1)); done
  [ "$(envval "$HENV" WHATSAPP_ENABLED)" = "true" ] && n=$((n+1))
  [ "$n" -gt 0 ] && ok "$n chat app(s) configured" || bad "No chat app token in stacks/hermes/data/.env (start with TELEGRAM_BOT_TOKEN)"
  njobs=$(docker exec hermes hermes cron list 2>/dev/null | grep -cE '^[[:space:]]*[0-9a-f]{6,}|every |[0-9*]+ [0-9*]+ ' || true)
  info "Scheduled background jobs: ${njobs:-0} (list: docker exec hermes hermes cron list)"
else
  bad "Hermes container not running"
fi

# ------------------------------------------------------------------------------ MCP
head_ "MCP tools on the box"
init='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"aurora-check","version":"1"}}}'
if out=$(curl -fsS -m 10 -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
         -X POST http://127.0.0.1:8931/mcp -d "$init" 2>/dev/null) && printf '%s' "$out" | grep -q serverInfo; then
  ok "Playwright MCP answers on 127.0.0.1:8931/mcp"
else info "Playwright MCP not answering (start: cd $DIR/stacks/computer && docker compose up -d)"; fi
if curl -fsS -m 5 -o /dev/null http://127.0.0.1:6080/vnc.html 2>/dev/null; then ok "Computer-use desktop up (chat :8501, screen :6080) — stop it when done"
else info "Computer-use desktop off (on demand)"; fi

# ------------------------------------------------------------------------ tailscale
head_ "Tailscale"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx tailscale; then
  if docker exec tailscale tailscale status --self --peers=false >/tmp/aurora-ts.txt 2>&1; then
    ok "Online: $(awk 'NR==1{print $1, $2}' /tmp/aurora-ts.txt)"
    served=$(docker exec tailscale tailscale serve status 2>/dev/null | grep -Eo 'https://[^ ]+' | sort -u | tr '\n' ' ')
    [ -n "$served" ] && ok "Private URLs: $served" || info "Nothing shared yet (tailscale serve --bg --https=<port> http://127.0.0.1:<port>)"
  else bad "Tailscale not logged in — set TS_AUTHKEY in stacks/tailscale/.env and restart"; fi
fi

# -------------------------------------------------------------------------- summary
printf '\n'
if [ "$FAIL" -eq 0 ]; then
  printf '%s%s✓ All good%s' "$B" "$G" "$N"; [ "$WARN" -gt 0 ] && printf ' (%d warning%s)' "$WARN" "$([ "$WARN" -gt 1 ] && echo s)"
  printf '\n'; exit 0
fi
printf '%s%s✗ %d problem%s%s, %d warning%s — fix the ✗ lines above, then run this again.\n' \
  "$B" "$R" "$FAIL" "$([ "$FAIL" -gt 1 ] && echo s)" "$N" "$WARN" "$([ "$WARN" -ne 1 ] && echo s)"
exit 1
