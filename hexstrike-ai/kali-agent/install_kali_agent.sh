#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# KALI AGENT — AUTOMATED INSTALLER
# Sets up the complete Kali Agent ecosystem on a Kali Linux host.
# 
# Usage: chmod +x install_kali_agent.sh && ./install_kali_agent.sh
# 
# AutoBoros.ai | 2026-03-27
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

HEXSTRIKE_DIR="${HOME}/hexstrike-ai"
PENTEST_BASE="/tmp/pentest"
LOG_DIR="/var/log/hexstrike"
MODULES_ARCHIVE="hexstrike-modules.tar.gz"

# ───────────────────────────────────────────
header() {
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════╗${NC}"
    echo -e "${RED}║${NC}  💀 ${PURPLE}KALI AGENT INSTALLER${NC}              ${RED}║${NC}"
    echo -e "${RED}║${NC}     AutoBoros.ai | 2026              ${RED}║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════╝${NC}"
    echo ""
}

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[  OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail()    { echo -e "${RED}[FAIL]${NC} $1"; }
step()    { echo -e "\n${PURPLE}━━━ $1 ━━━${NC}"; }

check_cmd() {
    if command -v "$1" &>/dev/null; then
        success "$1 found: $(command -v "$1")"
        return 0
    else
        fail "$1 not found"
        return 1
    fi
}

# ───────────────────────────────────────────
header

# Step 0: Verify we're on Kali (or at least Debian-based)
step "STEP 0: Environment Check"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    info "OS: $PRETTY_NAME"
else
    warn "Could not detect OS — proceeding anyway"
fi

check_cmd python3 || { fail "Python 3 required. Install with: sudo apt install python3"; exit 1; }
check_cmd pip3 || check_cmd pip || warn "pip not found — will try pip3"
check_cmd node || warn "Node.js not found — Desktop Commander needs it (install with: sudo apt install nodejs npm)"
check_cmd npm || warn "npm not found"
check_cmd git || warn "git not found"
check_cmd nmap || warn "nmap not found — core scanning tool"
check_cmd docker && DOCKER_AVAILABLE=true || { DOCKER_AVAILABLE=false; warn "Docker not found — optional Docker MCPs will be skipped"; }

# ───────────────────────────────────────────
step "STEP 1: Create Directory Structure"

mkdir -p "${HEXSTRIKE_DIR}"
mkdir -p "${PENTEST_BASE}"
sudo mkdir -p "${LOG_DIR}" 2>/dev/null && sudo chown "$(whoami)" "${LOG_DIR}" || mkdir -p "${HOME}/.hexstrike/logs"

success "Directories created"
info "  HexStrike:  ${HEXSTRIKE_DIR}"
info "  Pentest:    ${PENTEST_BASE}"
info "  Logs:       ${LOG_DIR}"

# ───────────────────────────────────────────
step "STEP 2: Install Python Dependencies"

PIP_FLAGS="--break-system-packages"

pip3 install fastmcp ${PIP_FLAGS} 2>/dev/null && success "fastmcp installed" || {
    pip install fastmcp ${PIP_FLAGS} 2>/dev/null && success "fastmcp installed (via pip)" || fail "Could not install fastmcp"
}

# Optional: zhipuai for GLM-4.5 integration
pip3 install zhipuai ${PIP_FLAGS} 2>/dev/null && success "zhipuai installed (GLM-4.5 support)" || warn "zhipuai not installed — GLM routing will fall back to Sonnet"

# Optional: anthropic SDK
pip3 install anthropic ${PIP_FLAGS} 2>/dev/null && success "anthropic SDK installed" || warn "anthropic SDK not installed — /interpret endpoint needs it"

# ───────────────────────────────────────────
step "STEP 3: Extract HexStrike Modules"

if [ -f "${MODULES_ARCHIVE}" ]; then
    tar xzf "${MODULES_ARCHIVE}" -C "${HEXSTRIKE_DIR}" --strip-components=1
    success "Modules extracted to ${HEXSTRIKE_DIR}"
elif [ -d "hexstrike-modules" ]; then
    cp -r hexstrike-modules/* "${HEXSTRIKE_DIR}/"
    success "Modules copied to ${HEXSTRIKE_DIR}"
else
    warn "No ${MODULES_ARCHIVE} or hexstrike-modules/ found in current directory"
    warn "Download from Claude conversation or clone from GitHub"
fi

ls -la "${HEXSTRIKE_DIR}"/*.py 2>/dev/null && success "Python modules present" || warn "No Python modules found"

# ───────────────────────────────────────────
step "STEP 4: Install Desktop Commander MCP"

if check_cmd npx; then
    info "Installing Desktop Commander..."
    npx @wonderwhy-er/desktop-commander@latest setup 2>/dev/null && \
        success "Desktop Commander installed" || \
        warn "Desktop Commander install failed — try manually: npx @wonderwhy-er/desktop-commander@latest setup"
else
    warn "npx not available — install Node.js first: sudo apt install nodejs npm"
fi

# ───────────────────────────────────────────
step "STEP 5: Install Shodan MCP"

SHODAN_KEY="${SHODAN_API_KEY:-}"

if [ -z "$SHODAN_KEY" ]; then
    warn "SHODAN_API_KEY not set"
    echo -e "${YELLOW}  To set it:${NC}"
    echo "    export SHODAN_API_KEY=your_key_here"
    echo "    Then re-run this script"
    echo ""
    echo -e "${BLUE}  Get a free key at: https://account.shodan.io${NC}"
else
    if check_cmd npx; then
        info "Installing Shodan MCP with API key..."
        npm install -g @burtthecoder/mcp-shodan 2>/dev/null && \
            success "Shodan MCP installed" || \
            warn "Shodan MCP install failed — try: npx -y @smithery/cli install @burtthecoder/mcp-shodan --client claude"
    fi
fi

# ───────────────────────────────────────────
step "STEP 6: Configure MCP Servers"

# Detect config file location
CLAUDE_CONFIG=""
if [ -f "${HOME}/.claude.json" ]; then
    CLAUDE_CONFIG="${HOME}/.claude.json"
elif [ -d "${HOME}/.config/claude" ]; then
    CLAUDE_CONFIG="${HOME}/.config/claude/claude_desktop_config.json"
fi

if [ -n "$CLAUDE_CONFIG" ]; then
    info "Claude config found: ${CLAUDE_CONFIG}"
    info "Add HexStrike MCP to your config manually:"
else
    info "No Claude config found — create one at ~/.claude.json"
fi

cat << 'MCPCONFIG'

Add this to your mcpServers block:

  "hexstrike": {
    "command": "python3",
    "args": ["HEXSTRIKE_DIR/hexstrike_mcp.py"],
    "env": { "PENTEST_BASE": "/tmp/pentest" }
  }

MCPCONFIG
echo "(Replace HEXSTRIKE_DIR with ${HEXSTRIKE_DIR})"

# ───────────────────────────────────────────
step "STEP 7: Verify Kali Tools"

info "Checking security tools..."
TOOLS_FOUND=0
TOOLS_MISSING=0

for tool in nmap nuclei nikto sqlmap subfinder amass whatweb ffuf gobuster \
            hydra john hashcat searchsploit metasploit-framework \
            crackmapexec enum4linux-ng wpscan dirb feroxbuster \
            tcpdump tshark whois dig curl wget socat; do
    if command -v "$tool" &>/dev/null 2>&1; then
        TOOLS_FOUND=$((TOOLS_FOUND + 1))
    elif dpkg -l "$tool" &>/dev/null 2>&1; then
        TOOLS_FOUND=$((TOOLS_FOUND + 1))
    else
        TOOLS_MISSING=$((TOOLS_MISSING + 1))
    fi
done

success "${TOOLS_FOUND} tools found"
[ $TOOLS_MISSING -gt 0 ] && warn "${TOOLS_MISSING} tools missing — install with: sudo apt install <tool>"

# ───────────────────────────────────────────
step "STEP 8: Docker MCP Servers (Optional)"

if [ "$DOCKER_AVAILABLE" = true ]; then
    echo ""
    read -rp "$(echo -e "${YELLOW}Clone and build mcp-security-hub Docker images? [y/N]:${NC} ")" BUILD_DOCKER

    if [[ "$BUILD_DOCKER" =~ ^[Yy]$ ]]; then
        info "Cloning FuzzingLabs/mcp-security-hub..."
        cd /tmp
        git clone --depth 1 https://github.com/FuzzingLabs/mcp-security-hub 2>/dev/null || warn "Clone failed"
        
        if [ -d /tmp/mcp-security-hub ]; then
            cd /tmp/mcp-security-hub
            
            for mcp in nmap-mcp nuclei-mcp sqlmap-mcp; do
                dir=$(find . -name "$mcp" -type d 2>/dev/null | head -1)
                if [ -n "$dir" ]; then
                    info "Building ${mcp}..."
                    docker build -t "${mcp}:latest" "${dir}" 2>/dev/null && \
                        success "${mcp} built" || warn "${mcp} build failed"
                fi
            done
        fi
    else
        info "Skipping Docker builds"
    fi
else
    info "Docker not available — skipping"
fi

# ───────────────────────────────────────────
step "STEP 9: Install systemd Service"

if [ -f "${HEXSTRIKE_DIR}/hexstrike.service" ]; then
    echo ""
    read -rp "$(echo -e "${YELLOW}Install HexStrike as systemd service? [y/N]:${NC} ")" INSTALL_SERVICE

    if [[ "$INSTALL_SERVICE" =~ ^[Yy]$ ]]; then
        # Update WorkingDirectory in service file
        sed -i "s|WorkingDirectory=.*|WorkingDirectory=${HEXSTRIKE_DIR}|" "${HEXSTRIKE_DIR}/hexstrike.service"
        sed -i "s|User=.*|User=$(whoami)|" "${HEXSTRIKE_DIR}/hexstrike.service"
        sed -i "s|Group=.*|Group=$(whoami)|" "${HEXSTRIKE_DIR}/hexstrike.service"

        sudo cp "${HEXSTRIKE_DIR}/hexstrike.service" /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable hexstrike
        success "HexStrike systemd service installed and enabled"
        info "Start with: sudo systemctl start hexstrike"
    fi
else
    warn "hexstrike.service not found in ${HEXSTRIKE_DIR}"
fi

# ───────────────────────────────────────────
step "STEP 10: Run Module Tests"

if [ -f "${HEXSTRIKE_DIR}/test_modules.py" ]; then
    info "Running unit tests..."
    cd "${HEXSTRIKE_DIR}"
    python3 test_modules.py 2>&1 || warn "Some tests failed — check output above"
else
    warn "test_modules.py not found"
fi

# ───────────────────────────────────────────
step "INSTALLATION COMPLETE"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Kali Agent installation finished!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${BLUE}HexStrike directory:${NC} ${HEXSTRIKE_DIR}"
echo -e "  ${BLUE}Pentest workspace:${NC}  ${PENTEST_BASE}"
echo ""
echo -e "  ${PURPLE}Quick start:${NC}"
echo "    cd ${HEXSTRIKE_DIR}"
echo "    python3 hexstrike_mcp.py          # Start MCP server"
echo ""
echo -e "  ${PURPLE}Or via systemd:${NC}"
echo "    sudo systemctl start hexstrike"
echo ""
echo -e "  ${PURPLE}Manual steps remaining:${NC}"
[ -z "$SHODAN_KEY" ] && echo "    - Set SHODAN_API_KEY and re-run"
echo "    - Add HexStrike to your Claude MCP config"
echo "    - Run a test engagement against a CTF target"
echo ""
echo -e "${RED}  ⚠️  Only test against authorized targets!${NC}"
echo ""
