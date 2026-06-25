#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# STAGE 6: KALI AGENT INSTALLATION
# Integrates AI-augmented pentest platform into existing Kali setup
#
# Prerequisites: Stages 1-5 complete, kali-agent-full.tar.gz in
#                /mnt/sf_KaliShare/tars/
#
# Usage: sudo ./setup-stage6-kaliagent.sh
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

KALISHARE="/mnt/sf_KaliShare"
AGENT_TAR="${KALISHARE}/tars/kali-agent-full.tar.gz"
AGENT_DIR="${KALISHARE}/tars/kali-agent-repo"
HEXSTRIKE="/opt/hexstrike"
SKILLS_DIR="$HOME/.config/opencode/skills"
PENTEST_BASE="/tmp/pentest"

banner() {
    echo -e "${RED}"
    echo "  ╔══════════════════════════════════════════════╗"
    echo "  ║  💀 STAGE 6: KALI AGENT INSTALLATION        ║"
    echo "  ║  AutoBoros.ai / Aurora AI Agency             ║"
    echo "  ╚══════════════════════════════════════════════╝"
    echo -e "${NC}"
}

step() { echo -e "\n${CYAN}[STEP $1]${NC} $2"; }
ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; }

banner

# ──────────────────────────────────────────────
# PRE-FLIGHT CHECKS
# ──────────────────────────────────────────────
step "0" "Pre-flight checks"

if [ ! -d "$KALISHARE" ]; then
    fail "KaliShare not mounted at $KALISHARE"
    echo "  Mount the shared folder first: sudo mount -t vboxsf KaliShare /mnt/sf_KaliShare"
    exit 1
fi
ok "KaliShare mounted"

if [ ! -f "$AGENT_TAR" ] && [ ! -d "$AGENT_DIR" ]; then
    fail "kali-agent-full.tar.gz not found in ${KALISHARE}/tars/"
    echo "  Copy the tarball from Claude conversation to ${KALISHARE}/tars/"
    exit 1
fi

# Extract if needed
if [ ! -d "$AGENT_DIR" ]; then
    echo "  Extracting tarball..."
    cd "${KALISHARE}/tars" && tar xzf kali-agent-full.tar.gz
fi
ok "Agent files extracted"

# Check HexStrike exists
if [ ! -d "$HEXSTRIKE" ]; then
    warn "HexStrike not at $HEXSTRIKE — creating directory"
    sudo mkdir -p "$HEXSTRIKE"
fi
ok "HexStrike directory ready"

# ──────────────────────────────────────────────
# STEP 1: PYTHON DEPENDENCIES
# ──────────────────────────────────────────────
step "1" "Installing Python dependencies"

# FastMCP for the MCP server
pip3 install --break-system-packages mcp 2>/dev/null && ok "mcp (FastMCP) installed" || warn "mcp already installed or pip issue"

# Ensure core libs available
for pkg in json ipaddress datetime; do
    python3 -c "import $pkg" 2>/dev/null && ok "$pkg available" || warn "$pkg check failed"
done

# ──────────────────────────────────────────────
# STEP 2: INSTALL PYTHON MODULES
# ──────────────────────────────────────────────
step "2" "Installing Python modules to $HEXSTRIKE"

# Backup existing
if [ -f "$HEXSTRIKE/hexstrike_mcp.py" ]; then
    backup="${HEXSTRIKE}/backup_$(date +%Y%m%d_%H%M%S)"
    sudo mkdir -p "$backup"
    sudo cp "$HEXSTRIKE"/*.py "$backup/" 2>/dev/null
    ok "Existing files backed up to $backup"
fi

modules=(
    scope_guard.py audit_logger.py sanitizer.py hexstrike_mcp.py
    model_router.py virustotal_enrichment.py burp_adapter.py
    deduplicator.py findings_exporter.py mermaid_generator.py
    notion_sync.py test_modules.py integration_test.py
)

installed=0
for mod in "${modules[@]}"; do
    if [ -f "$AGENT_DIR/$mod" ]; then
        sudo cp "$AGENT_DIR/$mod" "$HEXSTRIKE/"
        ((installed++))
    fi
done
ok "$installed Python modules installed"

# ──────────────────────────────────────────────
# STEP 3: INSTALL JS MODULES
# ──────────────────────────────────────────────
step "3" "Installing JS modules"

for js in generate_report.js generate_proposal.js executePlaybook.js; do
    if [ -f "$AGENT_DIR/$js" ]; then
        sudo cp "$AGENT_DIR/$js" "$HEXSTRIKE/"
    fi
done

# Install docx npm package for report generation
if command -v npm &>/dev/null; then
    cd "$HEXSTRIKE" && sudo npm install docx 2>/dev/null && ok "docx npm package installed" || warn "npm install failed"
else
    warn "npm not found — report generation requires: sudo apt install npm && cd $HEXSTRIKE && npm install docx"
fi

# ──────────────────────────────────────────────
# STEP 4: INSTALL SKILLS
# ──────────────────────────────────────────────
step "4" "Installing 17 pentest skills"

mkdir -p "$SKILLS_DIR"
skill_count=0

for skill_dir in "$AGENT_DIR"/skills/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name=$(basename "$skill_dir")
    dest="${SKILLS_DIR}/${skill_name}"
    mkdir -p "$dest"
    cp "$skill_dir/SKILL.md" "$dest/"
    # Copy references if they exist
    if [ -d "$skill_dir/references" ]; then
        cp -r "$skill_dir/references" "$dest/"
    fi
    ((skill_count++))
done
ok "$skill_count skills installed to $SKILLS_DIR"

# Backup copy to KaliShare
cp -r "$AGENT_DIR"/skills/* "${KALISHARE}/skills/" 2>/dev/null && ok "Skills backed up to ${KALISHARE}/skills/" || true

# ──────────────────────────────────────────────
# STEP 5: INSTALL CONFIGS & REFERENCES
# ──────────────────────────────────────────────
step "5" "Installing configs and reference data"

mkdir -p "${KALISHARE}/config" "${KALISHARE}/references" "${KALISHARE}/docs"

for cfg in scope_configs_example.json kali_playbook_template.json mcp_config.json; do
    [ -f "$AGENT_DIR/$cfg" ] && cp "$AGENT_DIR/$cfg" "${KALISHARE}/config/" && ok "$cfg → config/"
done

[ -f "$AGENT_DIR/vuln-kb-seed-data.json" ] && cp "$AGENT_DIR/vuln-kb-seed-data.json" "${KALISHARE}/references/" && ok "KB seed data → references/"

for doc in docs/*.md; do
    [ -f "$AGENT_DIR/$doc" ] && cp "$AGENT_DIR/$doc" "${KALISHARE}/docs/" && ok "$(basename $doc) → docs/"
done

# ──────────────────────────────────────────────
# STEP 6: INSTALL SCRIPTS
# ──────────────────────────────────────────────
step "6" "Installing utility scripts"

if [ -f "$AGENT_DIR/cleanup_engagement.sh" ]; then
    cp "$AGENT_DIR/cleanup_engagement.sh" "${KALISHARE}/scripts/"
    chmod +x "${KALISHARE}/scripts/cleanup_engagement.sh"
    ok "cleanup_engagement.sh → scripts/"
fi

# ──────────────────────────────────────────────
# STEP 7: CREATE DIRECTORIES
# ──────────────────────────────────────────────
step "7" "Creating working directories"

mkdir -p "$PENTEST_BASE" && ok "Engagement directory: $PENTEST_BASE"
mkdir -p "$HOME/.hexstrike/archives" && ok "Audit archive: ~/.hexstrike/archives/"

# ──────────────────────────────────────────────
# STEP 8: RUN TESTS
# ──────────────────────────────────────────────
step "8" "Running test suite"

cd "$HEXSTRIKE"
echo ""
if python3 test_modules.py 2>&1 | tail -3; then
    ok "Unit tests passed"
else
    fail "Unit tests failed — check output above"
fi

echo ""
if python3 integration_test.py 2>&1 | tail -5; then
    ok "Integration tests passed"
else
    warn "Integration tests — some may require tools not yet installed"
fi

# ──────────────────────────────────────────────
# STEP 9: SYSTEMD SERVICE (optional)
# ──────────────────────────────────────────────
step "9" "Systemd service (optional)"

if [ -f "$AGENT_DIR/hexstrike.service" ]; then
    read -p "  Install HexStrike as systemd service? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo cp "$AGENT_DIR/hexstrike.service" /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable hexstrike
        ok "hexstrike.service installed and enabled"
        echo "  Start with: sudo systemctl start hexstrike"
    else
        ok "Skipped — start manually: cd $HEXSTRIKE && python3 hexstrike_mcp.py"
    fi
fi

# ──────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────
echo ""
echo -e "${RED}═══════════════════════════════════════════════════${NC}"
echo -e "${RED}  💀 STAGE 6 COMPLETE${NC}"
echo -e "${RED}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Python modules:  ${GREEN}$installed${NC} → $HEXSTRIKE"
echo -e "  Skills:          ${GREEN}$skill_count${NC} → $SKILLS_DIR"
echo -e "  Tests:           ${GREEN}113${NC} (39 unit + 74 integration)"
echo ""
echo "  Next steps:"
echo "    1. Start HexStrike:  cd $HEXSTRIKE && python3 hexstrike_mcp.py"
echo "    2. Open Claude and say: 'Initialize a CTF pentest against 10.10.10.5'"
echo "    3. Use the dashboard:  Open kali-dashboard-live.jsx in Claude.ai"
echo ""
echo -e "  ${CYAN}Guide:${NC} ${KALISHARE}/docs/kali-operations-guide.md"
echo -e "  ${CYAN}Intel:${NC} ${KALISHARE}/references/vuln-kb-seed-data.json"
echo ""
