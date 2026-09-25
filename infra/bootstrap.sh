#!/usr/bin/env bash
# bootstrap.sh — one command from nothing to a running agency box.
#
# Runs on YOUR machine: the Reno 11 in Termux, a laptop, or a Claude session with the
# provider token set. VPS_PROVIDER in secrets.env picks where the box lives:
#
#   hostinger (default)  hostinger/provision.sh: reuses your VPS, sets up one you bought
#                        in hPanel, or buys one (budget-checked; you type "buy")
#   hetzner              hetzner/provision.sh: creates a Hetzner Cloud server
#
# Either way it puts the box behind the provider's firewall (SSH + Tailscale only),
# waits for the base setup (cloud-init / post-install script), then ships infra/ and
# your secrets to /opt/aurora. Re-running is safe: the same box is reused, and the
# files are shipped again. Starting the stacks is the next step: SETUP.md §6.
#
#   cp secrets.env.example secrets.env && $EDITOR secrets.env   (or: aurora-secrets fill)
#   ./bootstrap.sh --dry-run          # everything except buying/creating/changing anything
#   ./bootstrap.sh                    # asks before anything that costs money
#
# Knobs (env or secrets.env): VPS_PROVIDER NAME=aurora-01 BUDGET_AUD=39
#   SSH_KEY=~/.ssh/id_ed25519.pub, plus the provider's own (see its provision.sh).
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
NAME="${NAME:-aurora-01}"
BUDGET_AUD="${BUDGET_AUD:-39}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519.pub}"
SSH_USER=aurora

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
             OPENAI_API_KEY KIMI_API_KEY HF_TOKEN CURSOR_API_KEY
             TELEGRAM_BOT_TOKEN TELEGRAM_ALLOWED_USERS DISCORD_BOT_TOKEN DISCORD_ALLOWED_USERS
             SLACK_BOT_TOKEN SLACK_APP_TOKEN SLACK_ALLOWED_USERS WHATSAPP_ALLOWED_USERS
             COMPOSIO_CONSUMER_KEY ZAPIER_MCP_TOKEN GROQ_API_KEY GITHUB_PAT CONTEXT7_API_KEY TS_AUTHKEY
             INTELLIGENCE_API_KEY)
# (No associative arrays: macOS still ships bash 3.2.)
LOCAL_KEYS=(VPS_PROVIDER HCLOUD_TOKEN HOSTINGER_API_TOKEN HOSTINGER_PLAN HOSTINGER_TERM HOSTINGER_VM_ID)
# Provider tokens are used here and NEVER shipped to the box.
for k in "${LOCAL_KEYS[@]}" "${SECRET_KEYS[@]}"; do
  [ -n "${!k:-}" ] && printf -v "ENVSAVE_$k" '%s' "${!k}"
done
if [ -f "$DIR/secrets.env" ]; then
  set -a; # shellcheck disable=SC1091
  . "$DIR/secrets.env"; set +a
fi
for k in "${LOCAL_KEYS[@]}" "${SECRET_KEYS[@]}"; do
  v="ENVSAVE_$k"; [ -n "${!v:-}" ] && printf -v "$k" '%s' "${!v}"
done

[ -f "$SSH_KEY" ] || die "no public key at $SSH_KEY — run: ssh-keygen -t ed25519"
PUBKEY="$(tr -d '\r' < "$SSH_KEY" | head -1)"

have_key=0
for k in OPENROUTER_API_KEY ANTHROPIC_API_KEY GEMINI_API_KEY XAI_API_KEY OPENAI_API_KEY KIMI_API_KEY; do
  [ -n "${!k:-}" ] && have_key=1
done
[ "$have_key" = 1 ] || say "WARNING: no model API keys set — the box will come up, but the router and CLIs will have nothing to call."

VPS_PROVIDER="${VPS_PROVIDER:-hostinger}"
case "$VPS_PROVIDER" in
  hostinger) . "$DIR/hostinger/provision.sh"; provision_hostinger ;;
  hetzner)   . "$DIR/hetzner/provision.sh";   provision_hetzner ;;
  *) die "VPS_PROVIDER must be hostinger or hetzner (got '$VPS_PROVIDER')" ;;
esac

# --- Wait for SSH + the base setup, ship files ------------------------------------------
SSH=(ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 "$SSH_USER@$IP")
say "Waiting for SSH (the base setup creates the $SSH_USER user; first boot takes a few minutes)"
for _ in $(seq 1 "${SSH_WAIT_TRIES:-90}"); do "${SSH[@]}" true 2>/dev/null && break; sleep 10; done
"${SSH[@]}" true || die "SSH to $SSH_USER@$IP never came up"
say "Waiting for the base setup to finish"
# The login shell is fish, so every remote command goes through `bash -c`.
"${SSH[@]}" "bash -c '$READY_CMD'" || die "the base setup didn't finish on $IP"

say "Shipping infra/ to /opt/aurora"
tar -C "$DIR" -czf - --exclude='secrets.env' --exclude='.env' --exclude='*.tfstate*' \
  --exclude='.terraform' --exclude='main.tf' --exclude='.mcp.json' . \
  | "${SSH[@]}" "bash -c 'sudo mkdir -p /opt/aurora && sudo tar --no-same-owner -xzf - -C /opt/aurora \
      && sudo chown -R aurora:aurora /opt/aurora'"   # the aurora user edits .env files + runs compose

say "Shipping secrets (mode 600; the provider token stays on this machine)"
{
  for k in "${SECRET_KEYS[@]}"; do
    # `|| printf` (not `&& printf`): an empty LAST key would otherwise end the loop
    # "false", and with pipefail that aborted the script right here.
    [ -z "${!k:-}" ] || printf '%s=%q\n' "$k" "${!k}"
  done
} | "${SSH[@]}" "bash -c 'sudo install -m 600 -o root -g root /dev/stdin /opt/aurora/secrets.env'"


cat <<EOF

Done. $NAME is up at $IP: $PRICE_LINE.

  ssh $SSH_USER@$IP

Nothing is exposed publicly except SSH (and Tailscale on Hostinger). Open the UIs through an SSH tunnel:

  ssh -N -L 5678:127.0.0.1:5678 -L 4000:127.0.0.1:4000 -L 3001:127.0.0.1:3001 $SSH_USER@$IP
  # n8n → http://localhost:5678   router → http://localhost:4000/ui   uptime → http://localhost:3001

Next: start the stacks from /opt/aurora/stacks: SETUP.md §6. Then: bash /opt/aurora/check.sh
EOF
