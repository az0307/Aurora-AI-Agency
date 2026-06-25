#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# APRIL 2026 RED TEAM STACK — install.sh
# One-shot setup: clones deps, configures, starts stack
# Usage: ./scripts/install.sh [--kali | --docker | --full]
# ─────────────────────────────────────────────────────────────

set -euo pipefail

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[1;33m'
BLU='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

banner() {
  echo -e "${RED}"
  echo "  ██████╗ ███████╗██████╗     ████████╗███████╗ █████╗ ███╗   ███╗"
  echo "  ██╔══██╗██╔════╝██╔══██╗    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║"
  echo "  ██████╔╝█████╗  ██║  ██║       ██║   █████╗  ███████║██╔████╔██║"
  echo "  ██╔══██╗██╔══╝  ██║  ██║       ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║"
  echo "  ██║  ██║███████╗██████╔╝       ██║   ███████╗██║  ██║██║ ╚═╝ ██║"
  echo "  ╚═╝  ╚═╝╚══════╝╚═════╝        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝"
  echo -e "${NC}"
  echo -e "  ${YLW}APRIL 2026 BEST-COMBO RED TEAM STACK${NC}"
  echo -e "  ${BLU}HexStrike v6.0 + Kali MCP + PentestAgent + PentestThinkingMCP${NC}"
  echo ""
}

log() { echo -e "${GRN}[+]${NC} $*"; }
warn() { echo -e "${YLW}[!]${NC} $*"; }
err() { echo -e "${RED}[-]${NC} $*" >&2; }

check_deps() {
  log "Checking dependencies..."
  local missing=()
  for cmd in docker git python3 curl; do
    command -v "$cmd" &>/dev/null || missing+=("$cmd")
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    err "Missing: ${missing[*]}"
    err "Install them and re-run."
    exit 1
  fi

  # Check Docker Compose v2
  if ! docker compose version &>/dev/null; then
    err "Docker Compose v2 not found. Install Docker Desktop or docker-compose-plugin."
    exit 1
  fi

  log "Dependencies OK"
}

setup_env() {
  log "Setting up environment..."
  cd "$ROOT_DIR"

  if [[ ! -f .env ]]; then
    cp .env.example .env
    warn ".env created from template — EDIT IT before starting the stack!"
    warn "Set: HEXSTRIKE_API_TOKEN, POSTGRES_PASSWORD, KALI_PASSWORD"
    echo ""
    read -rp "Press ENTER after editing .env to continue, or Ctrl+C to exit..."
  else
    log ".env already exists — skipping"
  fi
}

clone_tools() {
  log "Cloning tool repos..."
  cd "$ROOT_DIR"

  # HexStrike AI
  if [[ ! -d "hexstrike-ai" ]]; then
    log "Cloning HexStrike AI..."
    git clone https://github.com/0x4m4/hexstrike-ai.git hexstrike-ai
  else
    log "HexStrike AI already cloned — pulling latest..."
    git -C hexstrike-ai pull origin main 2>/dev/null || true
  fi

  # PentestAgent
  if [[ ! -d "pentestagent" ]]; then
    log "Cloning PentestAgent..."
    git clone https://github.com/GH05TCREW/pentestagent.git pentestagent
  else
    log "PentestAgent already cloned"
  fi

  # PentestThinkingMCP
  if [[ ! -d "pentestthinking" ]]; then
    log "Cloning PentestThinkingMCP..."
    git clone https://github.com/ibrahimsaleem/PentestThinkingMCP.git pentestthinking
  else
    log "PentestThinkingMCP already cloned"
  fi

  log "Tool repos ready"
}

install_python_deps() {
  log "Installing Python dependencies..."

  pip3 install --break-system-packages \
    mcp fastmcp paramiko asyncssh \
    requests flask \
    litellm 2>/dev/null || \
  pip3 install \
    mcp fastmcp paramiko asyncssh \
    requests flask litellm

  # PentestAgent
  if [[ -f "$ROOT_DIR/pentestagent/requirements.txt" ]]; then
    pip3 install --break-system-packages -r "$ROOT_DIR/pentestagent/requirements.txt" 2>/dev/null || \
    pip3 install -r "$ROOT_DIR/pentestagent/requirements.txt"
  fi

  log "Python deps installed"
}

install_kali_native() {
  log "Installing HexStrike AI natively (Kali 2025.4+)..."
  if command -v apt &>/dev/null; then
    sudo apt update -q
    sudo apt install -y hexstrike-ai
    log "hexstrike-ai installed via apt"
  else
    warn "apt not found — skipping native install"
  fi
}

start_docker_stack() {
  log "Starting Docker stack..."
  cd "$ROOT_DIR"

  docker compose pull 2>/dev/null || true
  docker compose up -d --build

  log "Stack started. Waiting for health checks..."
  sleep 10

  ./scripts/healthcheck.sh
}

setup_ssh_key() {
  log "Setting up SSH key for Kali MCP..."
  local key_path="$HOME/.ssh/kali_mcp_ed25519"

  if [[ ! -f "$key_path" ]]; then
    ssh-keygen -t ed25519 -f "$key_path" -N "" -C "kali-mcp-key"
    log "SSH key generated at $key_path"
    warn "Add the public key to Kali MCP container:"
    warn "  docker exec -it kali-mcp bash -c 'mkdir -p /home/kali/.ssh && cat >> /home/kali/.ssh/authorized_keys' < ${key_path}.pub"
  else
    log "SSH key already exists at $key_path"
  fi
}

configure_claude_code() {
  log "Configuring Claude Code MCP..."
  local claude_config_dir="$HOME/.config/claude"
  mkdir -p "$claude_config_dir"

  if [[ -f "$ROOT_DIR/claude.json" ]]; then
    cp "$ROOT_DIR/claude.json" "$claude_config_dir/claude.json"
    log "claude.json installed to $claude_config_dir"
  fi

  warn "To start Claude Code with this stack:"
  warn "  cd $ROOT_DIR && claude --dangerously-skip-permissions"
}

create_loot_dir() {
  log "Creating loot directory structure..."
  mkdir -p "$ROOT_DIR/loot/.gitkeep"
  echo "loot/*" >> "$ROOT_DIR/.gitignore" 2>/dev/null || true
  echo "# Loot directory — evidence, findings, shells" > "$ROOT_DIR/loot/README.md"
  log "loot/ created (git-ignored)"
}

main() {
  banner
  check_deps

  MODE="${1:---full}"

  case "$MODE" in
    --kali)
      log "Mode: Kali native install"
      setup_env
      install_kali_native
      clone_tools
      install_python_deps
      setup_ssh_key
      configure_claude_code
      create_loot_dir
      ;;
    --docker)
      log "Mode: Docker stack only"
      setup_env
      clone_tools
      start_docker_stack
      configure_claude_code
      create_loot_dir
      ;;
    --full|*)
      log "Mode: Full install (Docker + Python deps + Claude Code config)"
      setup_env
      clone_tools
      install_python_deps
      start_docker_stack
      setup_ssh_key
      configure_claude_code
      create_loot_dir
      ;;
  esac

  echo ""
  echo -e "${GRN}═══════════════════════════════════════════════${NC}"
  echo -e "${GRN}  INSTALL COMPLETE${NC}"
  echo -e "${GRN}═══════════════════════════════════════════════${NC}"
  echo ""
  echo -e "  HexStrike API:  ${BLU}http://localhost:8888${NC}"
  echo -e "  Grafana:        ${BLU}http://localhost:3000${NC}"
  echo -e "  Kali MCP:       ${BLU}http://localhost:8000${NC}"
  echo ""
  echo -e "  Start Claude Code:"
  echo -e "  ${YLW}cd $ROOT_DIR && claude --dangerously-skip-permissions${NC}"
  echo ""
}

main "$@"
