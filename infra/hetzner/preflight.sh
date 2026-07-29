#!/usr/bin/env bash
# preflight.sh — validate everything BEFORE you spend money provisioning.
#
# Read-only: it never creates, modifies, or destroys any resource. It only asks
# Hetzner what exists and checks your local tooling. Run it first, every time.
#
#   export HCLOUD_TOKEN=...            # a Hetzner Cloud API token (per Project)
#   ./preflight.sh                     # defaults: cpx21 in sin (Singapore)
#   SERVER_TYPE=cax21 LOCATION=fsn1 ./preflight.sh
#
# Heads-up on env var names — the SAME token is read under two different names
# depending on the tool, which is an easy footgun:
#   HCLOUD_TOKEN        → Terraform hcloud provider + the official `hcloud` CLI (and this script)
#   HETZNER_API_TOKEN   → the Hetzner MCP server (see ../mcp/.mcp.json.example)
# This script accepts either and tells you if only one is set.
#
# Why this exists: server types are NOT available in every location — Ampere/ARM
# (CAX) is EU-only, while Singapore offers AMD (CPX/CCX). Asking the API up front
# turns a failed `terraform apply` (or a surprise bill) into a 5-second check.
set -euo pipefail

SERVER_TYPE="${SERVER_TYPE:-cpx21}"
LOCATION="${LOCATION:-sin}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519.pub}"
API="https://api.hetzner.cloud/v1"

pass() { printf '  \033[32mOK\033[0m   %s\n' "$1"; }
warn() { printf '  \033[33mWARN\033[0m %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAILED=1; }
FAILED=0

echo "Preflight: ${SERVER_TYPE} in ${LOCATION}"
echo

# --- 1. Local tooling ------------------------------------------------------
echo "Local tooling"
command -v curl >/dev/null && pass "curl present" || fail "curl missing"
command -v jq   >/dev/null && pass "jq present"   || warn "jq missing (output will be raw JSON)"
command -v terraform >/dev/null && pass "terraform present" \
  || warn "terraform missing — fine if you provision via the Hetzner MCP instead"
echo

# --- 2. SSH key ------------------------------------------------------------
echo "SSH key"
if [ -f "$SSH_KEY" ]; then
  pass "public key found: $SSH_KEY"
  grep -qE '^(ssh-ed25519|ssh-rsa|ecdsa-)' "$SSH_KEY" \
    && pass "looks like a valid public key" \
    || fail "$SSH_KEY does not look like a public key"
  case "$SSH_KEY" in
    *.pub) ;;
    *) warn "SSH_KEY does not end in .pub — make sure this is the PUBLIC key" ;;
  esac
else
  fail "no public key at $SSH_KEY (generate: ssh-keygen -t ed25519)"
fi
echo

# --- 3. API token ----------------------------------------------------------
echo "Hetzner API"
# Accept either name; they're the same credential (see header note).
TOKEN="${HCLOUD_TOKEN:-${HETZNER_API_TOKEN:-}}"
if [ -z "$TOKEN" ]; then
  fail "no token set — export HCLOUD_TOKEN (or HETZNER_API_TOKEN); create one per Project in the Hetzner console"
  echo; echo "Preflight FAILED — cannot check the API without a token."; exit 1
fi
if [ -n "${HCLOUD_TOKEN:-}" ] && [ -z "${HETZNER_API_TOKEN:-}" ]; then
  warn "only HCLOUD_TOKEN is set — the Hetzner MCP server needs HETZNER_API_TOKEN too"
elif [ -n "${HETZNER_API_TOKEN:-}" ] && [ -z "${HCLOUD_TOKEN:-}" ]; then
  warn "only HETZNER_API_TOKEN is set — Terraform/hcloud CLI need HCLOUD_TOKEN too"
fi

auth=(-sS -H "Authorization: Bearer ${TOKEN}")
if ! me="$(curl "${auth[@]}" -o /dev/null -w '%{http_code}' "${API}/servers?per_page=1")"; then
  fail "could not reach ${API} (network/proxy issue?)"; echo; exit 1
fi
case "$me" in
  200) pass "token authenticates" ;;
  401|403) fail "token rejected (HTTP $me) — wrong/revoked token, or wrong Project"; echo; exit 1 ;;
  *) fail "unexpected HTTP $me from the API"; echo; exit 1 ;;
esac

# --- 4. Does this server type exist in this location? ----------------------
# This is the check that catches the CAX-is-EU-only class of mistake.
types_json="$(curl "${auth[@]}" "${API}/server_types?per_page=100")"
locs_json="$(curl "${auth[@]}" "${API}/locations")"

if command -v jq >/dev/null; then
  if ! echo "$locs_json" | jq -e --arg l "$LOCATION" '.locations[]|select(.name==$l)' >/dev/null; then
    fail "location '$LOCATION' does not exist. Available: $(echo "$locs_json" | jq -r '[.locations[].name]|join(", ")')"
  else
    pass "location '$LOCATION' exists"
  fi

  st="$(echo "$types_json" | jq --arg t "$SERVER_TYPE" '.server_types[]|select(.name==$t)')"
  if [ -z "$st" ]; then
    fail "server type '$SERVER_TYPE' does not exist"
  else
    cores="$(echo "$st" | jq -r '.cores')"; mem="$(echo "$st" | jq -r '.memory')"
    disk="$(echo "$st" | jq -r '.disk')";  arch="$(echo "$st" | jq -r '.architecture // "?"')"
    pass "server type '$SERVER_TYPE' exists (${cores} vCPU / ${mem} GB / ${disk} GB / ${arch})"

    # Availability is reported per-datacenter; a type unavailable in the target
    # location is the single most common cause of a rejected apply.
    if echo "$st" | jq -e --arg l "$LOCATION" \
        '.prices[]|select(.location==$l)' >/dev/null 2>&1; then
      price="$(echo "$st" | jq -r --arg l "$LOCATION" \
        '.prices[]|select(.location==$l)|.price_monthly.gross')"
      pass "'$SERVER_TYPE' IS offered in '$LOCATION' (~€${price}/mo gross)"
    else
      fail "'$SERVER_TYPE' is NOT offered in '$LOCATION'"
      echo "       Offered in: $(echo "$st" | jq -r '[.prices[].location]|join(", ")')"
      echo "       Types available in '$LOCATION':"
      echo "$types_json" | jq -r --arg l "$LOCATION" \
        '[.server_types[]|select(.prices[]?.location==$l)|.name]|join(", ")' \
        | sed 's/^/         /'
    fi
  fi
else
  warn "install jq for the server-type/location compatibility check"
fi
echo

# --- 5. Existing footprint (so you don't double-provision) -----------------
if command -v jq >/dev/null; then
  n="$(curl "${auth[@]}" "${API}/servers?per_page=50" | jq '.servers|length')"
  if [ "$n" = "0" ]; then
    pass "no existing servers in this Project (clean slate)"
  else
    warn "this Project already has ${n} server(s) — confirm you're not duplicating"
  fi
fi
echo

if [ "$FAILED" = "1" ]; then
  echo "Preflight FAILED — fix the above before provisioning. Nothing was created."
  exit 1
fi
echo "Preflight PASSED. Safe to provision (see runbooks/DAY1.md). This spends money."
