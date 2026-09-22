#!/usr/bin/env bash
# 30-ssh-cyberdeck.sh — turn the S10 into a headless cyberdeck you can SSH into
# from a laptop. Key-based auth only; password auth disabled.
source "$(cd "$(dirname "$0")/.." && pwd)/lib/common.sh"

banner "SSH cyberdeck access"
require_authorization
load_env "$(cd "$(dirname "$0")/.." && pwd)/.env"

: "${CYBERDECK_SSH_PORT:=8022}"          # Termux sshd default
: "${CYBERDECK_AUTHORIZED_KEY:=}"        # your laptop's public key

log "Installing/configuring openssh in Termux"
run pkg install -y openssh

if [ -n "$CYBERDECK_AUTHORIZED_KEY" ]; then
  log "Installing your public key into authorized_keys"
  run mkdir -p "$HOME/.ssh"
  run chmod 700 "$HOME/.ssh"
  printf '%s\n' "$CYBERDECK_AUTHORIZED_KEY" >> "$HOME/.ssh/authorized_keys"
  run chmod 600 "$HOME/.ssh/authorized_keys"
else
  warn "CYBERDECK_AUTHORIZED_KEY not set in .env — add your laptop key before exposing sshd."
fi

log "Starting sshd on port $CYBERDECK_SSH_PORT (device-only)"
device_only run sshd

ok "SSH ready. From your laptop: ssh -p $CYBERDECK_SSH_PORT <user>@<phone-ip>"
