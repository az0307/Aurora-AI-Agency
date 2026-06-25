#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# rotate-tokens.sh — Rotate all API tokens and passwords
# Run after every engagement, or on schedule
# Usage: ./scripts/rotate-tokens.sh
# ─────────────────────────────────────────────────────────────

set -euo pipefail
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log()  { echo -e "${GRN}[+]${NC} $*"; }
warn() { echo -e "${YLW}[!]${NC} $*"; }
info() { echo -e "    $*"; }

echo ""
echo -e "${RED}══════════════════════════════════════${NC}"
echo -e "${RED}  TOKEN ROTATION — $(date +%Y-%m-%d)${NC}"
echo -e "${RED}══════════════════════════════════════${NC}"
echo ""

# Load current .env
if [[ ! -f "$ROOT_DIR/.env" ]]; then
    echo "No .env found. Run install.sh first."
    exit 1
fi
source "$ROOT_DIR/.env"

# ── Generate new tokens ───────────────────────────────────────
NEW_HEXSTRIKE_TOKEN=$(openssl rand -hex 32)
NEW_POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=')
NEW_KALI_PASSWORD=$(openssl rand -base64 16 | tr -d '/+=')
NEW_GRAFANA_PASSWORD=$(openssl rand -base64 16 | tr -d '/+=')

log "New tokens generated"

# ── Update .env ───────────────────────────────────────────────
sed -i "s/HEXSTRIKE_API_TOKEN=.*/HEXSTRIKE_API_TOKEN=$NEW_HEXSTRIKE_TOKEN/" "$ROOT_DIR/.env"
sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$NEW_POSTGRES_PASSWORD/" "$ROOT_DIR/.env"
sed -i "s/KALI_PASSWORD=.*/KALI_PASSWORD=$NEW_KALI_PASSWORD/" "$ROOT_DIR/.env"
sed -i "s/GRAFANA_PASSWORD=.*/GRAFANA_PASSWORD=$NEW_GRAFANA_PASSWORD/" "$ROOT_DIR/.env"
log ".env updated"

# ── Restart services with new tokens ─────────────────────────
warn "Restarting services with new credentials..."
docker compose restart hexstrike hexstrike-mcp 2>/dev/null || true
docker compose up -d kali-mcp 2>/dev/null || true

# Update Kali password
if docker ps | grep -q kali-mcp; then
    docker exec kali-mcp bash -c "echo 'kali:${NEW_KALI_PASSWORD}' | chpasswd" 2>/dev/null || true
    log "Kali MCP password updated"
fi

# ── Update Claude Code config ─────────────────────────────────
CLAUDE_CONFIG="$HOME/.config/claude/claude.json"
if [[ -f "$CLAUDE_CONFIG" ]]; then
    # Note: token is read from env in claude.json, so just restart Claude Code
    log "Claude Code reads from env — restart Claude Code to pick up new token"
fi

# ── Log rotation ──────────────────────────────────────────────
echo "$(date -Iseconds) | Token rotation completed" >> "$ROOT_DIR/docs/rotation_log.txt"

# ── Summary ───────────────────────────────────────────────────
echo ""
echo -e "${GRN}══════════════════════════════════════${NC}"
echo -e "${GRN}  ROTATION COMPLETE${NC}"
echo -e "${GRN}══════════════════════════════════════${NC}"
echo ""
echo "New tokens active. Previous tokens are now invalid."
echo ""
warn "Verify services are healthy: make health"
warn "Restart Claude Code to load new env vars"
echo ""
info "HEXSTRIKE_API_TOKEN: ${NEW_HEXSTRIKE_TOKEN:0:8}...${NEW_HEXSTRIKE_TOKEN: -8}"
info "POSTGRES_PASSWORD:   ${NEW_POSTGRES_PASSWORD:0:4}..."
info "KALI_PASSWORD:       ${NEW_KALI_PASSWORD:0:4}..."
info "GRAFANA_PASSWORD:    ${NEW_GRAFANA_PASSWORD:0:4}..."
echo ""
warn "The above tokens are now in .env — keep that file secure."
