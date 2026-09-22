#!/usr/bin/env bash
# 99-verify.sh — post-install sanity check. Prints a PASS/FAIL table.
source "$(cd "$(dirname "$0")/.." && pwd)/lib/common.sh"

banner "Cyberdeck verification"

fail=0
check() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    ok "$label"
  else
    warn "$label — MISSING"
    fail=1
  fi
}

check "git present"        have git
check "python present"     have python || have python3
check "nmap present"       have nmap
check "openssh present"    have ssh
check "workspace exists"   test -d "$HOME/cyberdeck"

if [ "$EMULATED" = "1" ]; then
  check "proot-distro present" have proot-distro
fi

if [ "$fail" = "0" ]; then
  ok "All checks passed."
else
  die "One or more checks failed — re-run the matching script."
fi
