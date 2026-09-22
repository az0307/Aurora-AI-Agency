#!/usr/bin/env bash
# common.sh — shared helpers for the S10 cyberdeck provisioning scripts.
# Source this from every script:  source "$(dirname "$0")/../lib/common.sh"
#
# Design goals:
#  - The same script must run BOTH on a real Samsung S10 (Termux/NetHunter)
#    AND inside the emulator, where device-only steps are stubbed or skipped.
#  - Nothing destructive happens without an explicit authorization gate.

set -euo pipefail

# ---- environment detection ------------------------------------------------
# EMULATED=1 is set by emulator/run-emulator.sh. On a real device it is unset.
: "${EMULATED:=0}"

# Detect Termux even if EMULATED is not passed (real-device convenience).
if [ -n "${TERMUX_VERSION:-}" ] || [ -d "/data/data/com.termux" ]; then
  ON_TERMUX=1; export ON_TERMUX
else
  ON_TERMUX=0; export ON_TERMUX
fi

# ---- logging --------------------------------------------------------------
if [ -t 1 ]; then
  C_RESET=$'\033[0m'; C_INFO=$'\033[0;36m'; C_OK=$'\033[0;32m'
  C_WARN=$'\033[0;33m'; C_ERR=$'\033[0;31m'; C_DIM=$'\033[0;90m'
else
  C_RESET=; C_INFO=; C_OK=; C_WARN=; C_ERR=; C_DIM=
fi

log()  { printf '%s[*]%s %s\n' "$C_INFO" "$C_RESET" "$*"; }
ok()   { printf '%s[+]%s %s\n' "$C_OK"   "$C_RESET" "$*"; }
warn() { printf '%s[!]%s %s\n' "$C_WARN" "$C_RESET" "$*" >&2; }
die()  { printf '%s[x]%s %s\n' "$C_ERR"  "$C_RESET" "$*" >&2; exit 1; }

banner() {
  printf '\n%s==== %s ====%s\n' "$C_INFO" "$*" "$C_RESET"
}

# ---- run wrapper ----------------------------------------------------------
# run CMD...    -> executes normally on device; in the emulator, prints and
#                  skips anything marked device-only via `device_only run ...`.
run() {
  printf '%s    $ %s%s\n' "$C_DIM" "$*" "$C_RESET"
  "$@"
}

# device_only run CMD...  -> only runs when NOT emulated. Under EMULATED it is
# printed and skipped, so we can validate script flow without a phone.
device_only() {
  if [ "$EMULATED" = "1" ]; then
    printf '%s    (device-only, skipped in emulator) %s%s\n' \
      "$C_DIM" "$*" "$C_RESET"
    return 0
  fi
  "$@"
}

# ---- authorization gate ---------------------------------------------------
# Provisioning a pentest device is fine; USING it is only lawful against
# systems you own or are explicitly authorized to test. This gate makes that
# acknowledgement explicit and auditable. Set CYBERDECK_AUTHORIZED=yes to pass
# non-interactively (e.g. in CI/emulator).
require_authorization() {
  if [ "${CYBERDECK_AUTHORIZED:-}" = "yes" ]; then
    ok "Authorization acknowledged (CYBERDECK_AUTHORIZED=yes)."
    return 0
  fi
  cat <<'NOTE'

  ------------------------------------------------------------------
  This toolkit provisions a device YOU own for security testing.
  Only test systems you own or have written authorization to assess.
  Unauthorized access is illegal. See docs/SAFETY.md.
  ------------------------------------------------------------------

NOTE
  if [ ! -t 0 ]; then
    die "No TTY and CYBERDECK_AUTHORIZED!=yes — refusing to proceed."
  fi
  read -r -p "  Type 'I AGREE' to continue: " reply
  [ "$reply" = "I AGREE" ] || die "Authorization not given — aborting."
  ok "Authorization acknowledged."
}

# ---- misc -----------------------------------------------------------------
have() { command -v "$1" >/dev/null 2>&1; }

load_env() {
  local env_file="${1:-.env}"
  if [ -f "$env_file" ]; then
    log "Loading environment from $env_file"
    set -a; # shellcheck disable=SC1090
    . "$env_file"; set +a
  fi
}
