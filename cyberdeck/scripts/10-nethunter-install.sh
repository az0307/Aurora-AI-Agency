#!/usr/bin/env bash
# 10-nethunter-install.sh — install Kali NetHunter on the S10.
# Two supported paths:
#   ROOTLESS (default): NetHunter chroot inside Termux via the official
#                       Offensive Security installer (no root, no unlock).
#   ROOTED:             full NetHunter (Magisk + kernel) — see docs/SETUP.md;
#                       this script only stages the rootless chroot.
source "$(cd "$(dirname "$0")/.." && pwd)/lib/common.sh"

banner "Kali NetHunter (rootless chroot) install"
require_authorization

NH_INSTALLER_URL="https://offs.ec/2MceZWr"   # official install-nethunter-termux
NH_CACHE="$HOME/cyberdeck/install-nethunter-termux"

log "Fetching the official NetHunter installer"
run curl -fsSL -o "$NH_CACHE" "$NH_INSTALLER_URL"
run chmod +x "$NH_CACHE"

log "Running NetHunter installer (device-only; downloads the Kali rootfs)"
device_only run bash "$NH_CACHE"

if [ "$EMULATED" = "1" ]; then
  log "Emulator: standing up a Kali rootfs stand-in via proot-distro instead"
  run proot-distro install kali || warn "proot-distro kali install returned non-zero (ok in mock)"
fi

ok "NetHunter staged. Launch with 'nethunter' (nh) on device. Next: 20-pentest-toolkit.sh"
