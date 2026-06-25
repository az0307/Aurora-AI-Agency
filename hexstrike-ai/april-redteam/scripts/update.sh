#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# update.sh — Update all repos and Docker images in the stack
# Usage: ./scripts/update.sh [--major]
# ─────────────────────────────────────────────────────────────

set -euo pipefail
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; BLU='\033[0;34m'; NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAJOR="${1:-}"

log()  { echo -e "${GRN}[+]${NC} $*"; }
warn() { echo -e "${YLW}[!]${NC} $*"; }
info() { echo -e "${BLU}[*]${NC} $*"; }
err()  { echo -e "${RED}[-]${NC} $*" >&2; }

echo ""
echo -e "${BLU}══════════════════════════════════════════${NC}"
echo -e "${BLU}  APRIL 2026 RED TEAM STACK — UPDATER${NC}"
echo -e "${BLU}  $(date +%Y-%m-%d)${NC}"
echo -e "${BLU}══════════════════════════════════════════${NC}"
echo ""

cd "$ROOT_DIR"

# ── This repo ─────────────────────────────────────────────────
info "Updating stack repo..."
git pull origin main 2>/dev/null && log "Stack repo updated" || warn "Could not update stack repo (local changes?)"

# ── Tool repos ────────────────────────────────────────────────
REPOS=(
    "hexstrike-ai"
    "pentestagent"
    "pentestthinking"
    "pentestgpt"
    "autogpt"
    "stride-gpt"
    "vulngpt-v2"
    "agent-cai"
    "pentagi"
    "autopentest-ai"
)

info "Updating tool repos..."
for repo in "${REPOS[@]}"; do
    if [[ -d "$ROOT_DIR/$repo" ]]; then
        info "  Updating $repo..."
        (cd "$ROOT_DIR/$repo" && git pull 2>/dev/null && log "  $repo updated") || warn "  Could not update $repo"
    fi
done

# ── Kali apt packages ─────────────────────────────────────────
info "Updating Kali packages..."
if command -v apt &>/dev/null; then
    sudo apt update -qq
    sudo apt upgrade -y hexstrike-ai nuclei seclists 2>/dev/null || true
    log "Kali packages updated"
fi

# ── Python packages ───────────────────────────────────────────
info "Updating Python packages..."
pip install --upgrade slither-analyzer mythril frida-tools objection pyrit 2>/dev/null || warn "Some Python packages failed to update"

# ── Nuclei templates ──────────────────────────────────────────
info "Updating Nuclei templates..."
nuclei -update-templates 2>/dev/null && log "Nuclei templates updated (4000+)" || warn "Nuclei not installed or update failed"

# ── Docker images ─────────────────────────────────────────────
info "Pulling latest Docker images..."
docker compose pull 2>/dev/null && log "Docker images updated" || warn "Docker pull failed (check Docker daemon)"

# ── Wordlists ─────────────────────────────────────────────────
info "Checking SecLists..."
if [[ -d /usr/share/seclists ]]; then
    (cd /usr/share/seclists && sudo git pull 2>/dev/null) && log "SecLists updated" || warn "SecLists update failed"
else
    warn "SecLists not found — run: sudo apt install seclists"
fi

# ── Summary ───────────────────────────────────────────────────
echo ""
echo -e "${GRN}══════════════════════════════════════════${NC}"
echo -e "${GRN}  UPDATE COMPLETE${NC}"
echo -e "${GRN}══════════════════════════════════════════${NC}"
echo ""
warn "Restart the stack after major updates: make restart"
echo ""
