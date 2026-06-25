#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# backup.sh — Encrypt and archive loot directory
# Usage: ./scripts/backup.sh [MISSION_NAME]
#        ./scripts/backup.sh --all
# ─────────────────────────────────────────────────────────────

set -euo pipefail
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$ROOT_DIR/backups"
mkdir -p "$BACKUP_DIR"

log()  { echo -e "${GRN}[+]${NC} $*"; }
warn() { echo -e "${YLW}[!]${NC} $*"; }
err()  { echo -e "${RED}[-]${NC} $*" >&2; }

MISSION="${1:-}"

if [[ "$MISSION" == "--all" ]]; then
    MISSIONS=$(ls "$ROOT_DIR/loot/" | grep -v 'README\|REPORT' | grep -v '\.md$' || echo "")
    if [[ -z "$MISSIONS" ]]; then
        warn "No missions found in loot/"
        exit 0
    fi
else
    if [[ -z "$MISSION" ]]; then
        echo "Usage: $0 [MISSION_NAME | --all]"
        echo "Available missions:"
        ls "$ROOT_DIR/loot/" | grep -v 'README\|REPORT\|\.md' || echo "  (none)"
        exit 1
    fi
    if [[ ! -d "$ROOT_DIR/loot/$MISSION" ]]; then
        err "Mission not found: loot/$MISSION"
        exit 1
    fi
    MISSIONS="$MISSION"
fi

for mission in $MISSIONS; do
    if [[ ! -d "$ROOT_DIR/loot/$mission" ]]; then continue; fi

    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    ARCHIVE="$BACKUP_DIR/${mission}_${TIMESTAMP}.tar.gz"
    ENCRYPTED="$ARCHIVE.gpg"

    log "Backing up: $mission"

    # Create archive
    tar -czf "$ARCHIVE" -C "$ROOT_DIR/loot" "$mission/"
    SIZE=$(du -sh "$ARCHIVE" | cut -f1)
    log "Archive created: $ARCHIVE ($SIZE)"

    # Encrypt
    warn "Enter passphrase for encryption (remember it — no recovery):"
    gpg --symmetric --cipher-algo AES256 --output "$ENCRYPTED" "$ARCHIVE"
    rm "$ARCHIVE"

    log "Encrypted: $ENCRYPTED"

    # Verify
    if gpg --list-packets "$ENCRYPTED" &>/dev/null; then
        log "Encryption verified"
    else
        err "Encryption verification failed!"
        exit 1
    fi

    # Log backup
    echo "$(date -Iseconds) | $mission | $ENCRYPTED" >> "$BACKUP_DIR/backup_log.txt"

done

echo ""
echo -e "${GRN}═══════════════════════════════════════${NC}"
echo -e "${GRN}  BACKUP COMPLETE${NC}"
echo -e "${GRN}═══════════════════════════════════════${NC}"
echo ""
echo "Archives in: $BACKUP_DIR/"
ls -lh "$BACKUP_DIR/"*.gpg 2>/dev/null || echo "(none)"
echo ""
warn "Transfer these files securely. Do NOT email unencrypted."
warn "Recommended: use client's secure file transfer system or SFTP."
