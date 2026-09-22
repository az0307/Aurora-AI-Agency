#!/usr/bin/env bash
# 00-termux-bootstrap.sh — one-shot Termux base setup for the S10 cyberdeck.
# Run this FIRST, inside Termux on the phone (or via the emulator to test flow).
source "$(cd "$(dirname "$0")/.." && pwd)/lib/common.sh"

banner "Termux bootstrap"
require_authorization

# Termux package set. On device these use pkg; in the emulator, mock-termux/pkg
# shims to apt so the flow is exercised end to end.
CORE_PKGS="git openssh curl wget python nodejs vim tmux proot-distro tsu \
termux-api termux-tools nmap"

log "Updating package index and upgrading base system"
run pkg update -y
run pkg upgrade -y

log "Granting Termux access to shared storage (device-only)"
device_only run termux-setup-storage

log "Installing core packages"
# shellcheck disable=SC2086
run pkg install -y $CORE_PKGS

log "Enabling wake-lock so long jobs survive the screen turning off"
device_only run termux-wake-lock

log "Creating cyberdeck workspace directories"
run mkdir -p "$HOME/cyberdeck/loot" "$HOME/cyberdeck/logs" "$HOME/cyberdeck/scopes"

ok "Termux bootstrap complete. Next: scripts/10-nethunter-install.sh"
