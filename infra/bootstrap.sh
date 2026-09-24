#!/usr/bin/env bash
# bootstrap.sh — one command from nothing to a running agency box.
#
# Runs on YOUR machine (laptop, or a Claude session that has HCLOUD_TOKEN set). It:
#   1. runs hetzner/preflight.sh (read-only: token, server type, location, SSH key)
#   2. checks the live monthly price against BUDGET_AUD and refuses if it's over
#   3. asks before spending (skip with --yes)
#   4. creates / reuses: SSH key, a cloud firewall (SSH only), and the server
#   5. waits for cloud-init, then ships infra/ + your secrets to /opt/aurora on the box
#
# Re-running is safe: an existing server with the same NAME is reused (no second bill);
# the files are re-shipped. Starting the stacks is a manual step: runbooks/DAY1.md.
#
#   cp secrets.env.example secrets.env && $EDITOR secrets.env
#   ./bootstrap.sh --dry-run          # everything except creating anything
#   ./bootstrap.sh                    # asks once before creating the server
#
# Knobs (env): NAME=aurora-01 SERVER_TYPE=cpx31 LOCATION=sin IMAGE=ubuntu-24.04
#              BUDGET_AUD=39 EUR_AUD=1.75 SSH_KEY=~/.ssh/id_ed25519.pub
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
NAME="${NAME:-aurora-01}"
SERVER_TYPE="${SERVER_TYPE:-cpx31}"
LOCATION="${LOCATION:-sin}"
IMAGE="${IMAGE:-ubuntu-24.04}"
BUDGET_AUD="${BUDGET_AUD:-39}"
# Conservative EUR→AUD rate so the budget check errs on the side of refusing.
EUR_AUD="${EUR_AUD:-1.75}"
# Hetzner bills a primary IPv4 separately from the server type (~€0.50–0.60/mo).
IPV4_EUR="${IPV4_EUR:-0.60}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519.pub}"
SSH_USER=aurora
API="https://api.hetzner.cloud/v1"

DRY_RUN=0; ASSUME_YES=0
for a in "$@"; do
  case "$a" in
    --dry-run) DRY_RUN=1 ;;
    --yes|-y)  ASSUME_YES=1 ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "unknown flag: $a" >&2; exit 2 ;;
  esac
done

say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
die()  { printf '\033[31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

for t in curl jq ssh tar; do command -v "$t" >/dev/null || die "$t is required on this machine"; done

# --- Secrets: file first, then the shell environment overrides it -------------------
SECRET_KEYS=(TZ N8N_DOMAIN OPENROUTER_API_KEY ANTHROPIC_API_KEY GEMINI_API_KEY XAI_API_KEY
             OPENAI_API_KEY KIMI_API_KEY HF_TOKEN
             TELEGRAM_BOT_TOKEN TELEGRAM_ALLOWED_USERS DISCORD_BOT_TOKEN DISCORD_ALLOWED_USERS
             SLACK_BOT_TOKEN SLACK_APP_TOKEN SLACK_ALLOWED_USERS WHATSAPP_ALLOWED_USERS
             COMPOSIO_CONSUMER_KEY TS_AUTHKEY INTELLIGENCE_API_KEY)
# (No associative arrays: macOS still ships bash 3.2.)
for k in HCLOUD_TOKEN "${SECRET_KEYS[@]}"; do
  [ -n "${!k:-}" ] && printf -v "ENVSAVE_$k" '%s' "${!k}"
done
if [ -f "$DIR/secrets.env" ]; then
  set -a; # shellcheck disable=SC1091
  . "$DIR/secrets.env"; set +a
fi
for k in HCLOUD_TOKEN "${SECRET_KEYS[@]}"; do
  v="ENVSAVE_$k"; [ -n "${!v:-}" ] && printf -v "$k" '%s' "${!v}"
done

export HCLOUD_TOKEN="${HCLOUD_TOKEN:-${HETZNER_API_TOKEN:-}}"
[ -n "$HCLOUD_TOKEN" ] || die "HCLOUD_TOKEN is not set (put it in infra/secrets.env or your environment)"
[ -f "$SSH_KEY" ] || die "no public key at $SSH_KEY — run: ssh-keygen -t ed25519"
PUBKEY="$(tr -d '\r' < "$SSH_KEY" | head -1)"

have_key=0
for k in OPENROUTER_API_KEY ANTHROPIC_API_KEY GEMINI_API_KEY XAI_API_KEY OPENAI_API_KEY KIMI_API_KEY; do
  [ -n "${!k:-}" ] && have_key=1
done
[ "$have_key" = 1 ] || say "WARNING: no model API keys set — the box will come up, but the router and CLIs will have nothing to call."

# --- 1. Preflight (read-only) ---------------------------------------------------------
say "Preflight"
SERVER_TYPE="$SERVER_TYPE" LOCATION="$LOCATION" SSH_KEY="$SSH_KEY" bash "$DIR/hetzner/preflight.sh"

api() { # api METHOD PATH [JSON]
  local m="$1" p="$2" body="${3:-}"
  if [ -n "$body" ]; then
    curl -sS -X "$m" -H "Authorization: Bearer $HCLOUD_TOKEN" -H 'Content-Type: application/json' \
      --data "$body" "$API$p"
  else
    curl -sS -X "$m" -H "Authorization: Bearer $HCLOUD_TOKEN" "$API$p"
  fi
}
api_ok() { # fail loudly on a Hetzner error object
  local out="$1"
  if echo "$out" | jq -e '.error' >/dev/null 2>&1; then
    die "Hetzner API: $(echo "$out" | jq -r '.error.code + ": " + .error.message')"
  fi
}

# --- 2. Budget guard --------------------------------------------------------------------
say "Budget check (cap: AUD \$${BUDGET_AUD}/mo)"
st="$(api GET "/server_types?name=$SERVER_TYPE")"; api_ok "$st"
eur="$(echo "$st" | jq -r --arg l "$LOCATION" \
  '.server_types[0].prices[]|select(.location==$l)|.price_monthly.gross' | head -1)"
[ -n "$eur" ] && [ "$eur" != null ] || die "no price for $SERVER_TYPE in $LOCATION"
aud="$(awk -v e="$eur" -v ip="$IPV4_EUR" -v r="$EUR_AUD" 'BEGIN{printf "%.2f",(e+ip)*r}')"
echo "  $SERVER_TYPE in $LOCATION: €${eur} + IPv4 €${IPV4_EUR} ≈ AUD \$${aud}/mo (at ${EUR_AUD} AUD/EUR)"
awk -v a="$aud" -v b="$BUDGET_AUD" 'BEGIN{exit !(a<=b)}' \
  || die "≈AUD \$${aud}/mo is over the AUD \$${BUDGET_AUD} cap. Pick a smaller SERVER_TYPE or raise BUDGET_AUD."

# --- 3. Render cloud-init with your public key ----------------------------------------
USER_DATA="$(<"$DIR/hetzner/cloud-init.yaml")"
USER_DATA="${USER_DATA//"<YOUR_SSH_PUBLIC_KEY>"/$PUBKEY}"
grep -q '<YOUR_SSH_PUBLIC_KEY>' <<<"$USER_DATA" && die "failed to substitute SSH key into cloud-init"

existing="$(api GET "/servers?name=$NAME")"; api_ok "$existing"
SERVER_ID="$(echo "$existing" | jq -r '.servers[0].id // empty')"

if [ "$DRY_RUN" = 1 ]; then
  say "Dry run complete. Would $( [ -n "$SERVER_ID" ] && echo "REUSE existing server $NAME (#$SERVER_ID)" || echo "CREATE $NAME ($SERVER_TYPE, $LOCATION, $IMAGE)")."
  echo "  Nothing was created or changed."
  exit 0
fi

if [ -z "$SERVER_ID" ] && [ "$ASSUME_YES" != 1 ]; then
  read -r -p "Create $NAME ($SERVER_TYPE in $LOCATION) for ≈AUD \$${aud}/mo? This starts billing. [y/N] " ans
  [[ "$ans" =~ ^[Yy]$ ]] || die "aborted — nothing was created"
fi

# --- 4. SSH key, firewall, server (create or reuse) -----------------------------------
say "SSH key"
keys="$(api GET "/ssh_keys?per_page=50")"; api_ok "$keys"
key_body="$(awk '{print $1" "$2}' <<<"$PUBKEY")"
KEY_ID="$(echo "$keys" | jq -r --arg k "$key_body" \
  '.ssh_keys[]|select((.public_key|split(" ")[0:2]|join(" "))==$k)|.id' | head -1)"
if [ -z "$KEY_ID" ]; then
  out="$(api POST /ssh_keys "$(jq -n --arg n "$NAME-key" --arg k "$PUBKEY" '{name:$n,public_key:$k}')")"
  api_ok "$out"; KEY_ID="$(echo "$out" | jq -r '.ssh_key.id')"
  echo "  uploaded (#$KEY_ID)"
else
  echo "  reusing (#$KEY_ID)"
fi

say "Cloud firewall (inbound SSH only — Docker-published ports can bypass ufw, this can't be bypassed)"
fw="$(api GET "/firewalls?name=$NAME-fw")"; api_ok "$fw"
FW_ID="$(echo "$fw" | jq -r '.firewalls[0].id // empty')"
if [ -z "$FW_ID" ]; then
  out="$(api POST /firewalls "$(jq -n --arg n "$NAME-fw" '{name:$n, rules:[
    {direction:"in",protocol:"tcp",port:"22",source_ips:["0.0.0.0/0","::/0"],description:"ssh"},
    {direction:"in",protocol:"icmp",source_ips:["0.0.0.0/0","::/0"],description:"ping"}]}')")"
  api_ok "$out"; FW_ID="$(echo "$out" | jq -r '.firewall.id')"
  echo "  created (#$FW_ID)"
else
  echo "  reusing (#$FW_ID)"
fi

if [ -z "$SERVER_ID" ]; then
  say "Creating server $NAME"
  body="$(jq -n --arg n "$NAME" --arg t "$SERVER_TYPE" --arg l "$LOCATION" --arg i "$IMAGE" \
    --arg ud "$USER_DATA" --argjson k "$KEY_ID" --argjson f "$FW_ID" \
    '{name:$n,server_type:$t,location:$l,image:$i,ssh_keys:[$k],user_data:$ud,
      firewalls:[{firewall:$f}],labels:{"managed-by":"aurora-bootstrap"},
      public_net:{enable_ipv4:true,enable_ipv6:true},start_after_create:true}')"
  out="$(api POST /servers "$body")"; api_ok "$out"
  SERVER_ID="$(echo "$out" | jq -r '.server.id')"
else
  say "Reusing existing server $NAME (#$SERVER_ID)"
fi

for _ in $(seq 1 60); do
  s="$(api GET "/servers/$SERVER_ID")"; api_ok "$s"
  [ "$(echo "$s" | jq -r '.server.status')" = running ] && break
  sleep 5
done
IP="$(echo "$s" | jq -r '.server.public_net.ipv4.ip')"
[ -n "$IP" ] && [ "$IP" != null ] || die "server has no IPv4 yet"
echo "  running at $IP"

# --- 5. Wait for SSH + cloud-init, ship files, run setup -------------------------------
SSH=(ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 "$SSH_USER@$IP")
say "Waiting for SSH (cloud-init creates the $SSH_USER user; first boot takes a few minutes)"
for _ in $(seq 1 90); do "${SSH[@]}" true 2>/dev/null && break; sleep 10; done
"${SSH[@]}" true || die "SSH to $SSH_USER@$IP never came up"
# The login shell is fish, so every remote command goes through `bash -c`.
"${SSH[@]}" "bash -c 'sudo cloud-init status --wait >/dev/null || true'"

say "Shipping infra/ to /opt/aurora"
tar -C "$DIR" -czf - --exclude='secrets.env' --exclude='.env' --exclude='*.tfstate*' \
  --exclude='.terraform' --exclude='main.tf' --exclude='.mcp.json' . \
  | "${SSH[@]}" "bash -c 'sudo mkdir -p /opt/aurora && sudo tar -xzf - -C /opt/aurora'"

say "Shipping secrets (mode 600; the Hetzner token stays on this machine)"
{
  for k in "${SECRET_KEYS[@]}"; do
    [ -n "${!k:-}" ] && printf '%s=%q\n' "$k" "${!k}"
  done
} | "${SSH[@]}" "bash -c 'sudo install -m 600 -o root -g root /dev/stdin /opt/aurora/secrets.env'"


cat <<EOF

Done. $NAME is up at $IP (≈AUD \$${aud}/mo).

  ssh $SSH_USER@$IP

Nothing is exposed publicly except SSH. Open the UIs through an SSH tunnel:

  ssh -N -L 5678:127.0.0.1:5678 -L 4000:127.0.0.1:4000 -L 3001:127.0.0.1:3001 $SSH_USER@$IP
  # n8n → http://localhost:5678   router → http://localhost:4000/ui   uptime → http://localhost:3001

Next: start the stacks from /opt/aurora/stacks — follow runbooks/DAY1.md §5.
EOF
