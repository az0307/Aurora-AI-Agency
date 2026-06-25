#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# KALI AGENT — DEPLOYMENT VALIDATOR
# Run after setup-stage6-kaliagent.sh to verify full stack
#
# Usage: ./validate-deployment.sh
# ═══════════════════════════════════════════════════════════
set -uo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

HEXSTRIKE="/opt/hexstrike"
SKILLS_DIR="$HOME/.config/opencode/skills"
KALISHARE="/mnt/sf_KaliShare"
PASS=0
FAIL=0
WARN=0

check() {
    local desc="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $desc"
        ((PASS++))
    else
        echo -e "  ${RED}✗${NC} $desc"
        ((FAIL++))
    fi
}

warn_check() {
    local desc="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $desc"
        ((PASS++))
    else
        echo -e "  ${YELLOW}⚠${NC} $desc (optional)"
        ((WARN++))
    fi
}

echo -e "${RED}"
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║  💀 KALI AGENT — DEPLOYMENT VALIDATOR       ║"
echo "  ╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# ── SYSTEM ──
echo -e "\n${CYAN}[SYSTEM]${NC}"
check "Running on Linux" "uname -s | grep -qi linux"
check "Python 3.10+" "python3 -c 'import sys; assert sys.version_info >= (3,10)'"
warn_check "Node.js available" "which node"
warn_check "npm available" "which npm"
check "KaliShare mounted" "test -d $KALISHARE"

# ── HEXSTRIKE MODULES ──
echo -e "\n${CYAN}[HEXSTRIKE MODULES]${NC} $HEXSTRIKE/"
for mod in scope_guard audit_logger sanitizer hexstrike_mcp model_router \
           virustotal_enrichment burp_adapter deduplicator findings_exporter \
           mermaid_generator notion_sync test_modules integration_test; do
    check "$mod.py" "test -f $HEXSTRIKE/${mod}.py"
done

# ── JS MODULES ──
echo -e "\n${CYAN}[JS MODULES]${NC}"
for js in generate_report.js generate_proposal.js executePlaybook.js; do
    warn_check "$js" "test -f $HEXSTRIKE/$js"
done
warn_check "docx npm package" "test -d $HEXSTRIKE/node_modules/docx"

# ── SKILLS ──
echo -e "\n${CYAN}[SKILLS]${NC} $SKILLS_DIR/"
expected_skills=(
    scope-guard recon-osint vuln-analysis exploit-dev post-exploit
    red-team-report audit-logger tool-output-sanitizer credential-attack
    web-app-security active-directory threat-intel payload-craft
    wireless-recon network-forensics pentest-cheatsheet ctf-walkthrough
)
for skill in "${expected_skills[@]}"; do
    check "$skill" "test -f $SKILLS_DIR/$skill/SKILL.md"
done

# ── CONFIGS ──
echo -e "\n${CYAN}[CONFIGS]${NC}"
warn_check "scope_configs_example.json" "test -f $KALISHARE/config/scope_configs_example.json"
warn_check "kali_playbook_template.json" "test -f $KALISHARE/config/kali_playbook_template.json"
warn_check "vuln-kb-seed-data.json" "test -f $KALISHARE/references/vuln-kb-seed-data.json"
warn_check "kali-operations-guide.md" "test -f $KALISHARE/docs/kali-operations-guide.md"

# ── PENTEST TOOLS ──
echo -e "\n${CYAN}[PENTEST TOOLS]${NC}"
for tool in nmap nuclei nikto sqlmap subfinder whatweb ffuf gobuster \
            hydra john hashcat searchsploit crackmapexec wpscan curl; do
    check "$tool" "which $tool"
done
warn_check "certipy" "which certipy"
warn_check "bloodhound-python" "which bloodhound-python"
warn_check "evil-winrm" "which evil-winrm"
warn_check "responder" "which responder"
warn_check "feroxbuster" "which feroxbuster"

# ── MCP SERVERS ──
echo -e "\n${CYAN}[MCP SERVERS]${NC}"
warn_check "Desktop Commander" "which desktop-commander || npx --yes @wonderwhy-er/desktop-commander@latest --version"
warn_check "Shodan MCP" "which mcp-shodan || npm list -g @burtthecoder/mcp-shodan"
check "FastMCP importable" "python3 -c 'import mcp'"

# ── DIRECTORIES ──
echo -e "\n${CYAN}[DIRECTORIES]${NC}"
check "/tmp/pentest exists" "test -d /tmp/pentest"
check "~/.hexstrike/archives exists" "test -d $HOME/.hexstrike/archives"

# ── TESTS ──
echo -e "\n${CYAN}[TEST SUITE]${NC}"
if cd "$HEXSTRIKE" && python3 test_modules.py &>/dev/null; then
    result=$(python3 test_modules.py 2>&1 | grep -oP '\d+ passed')
    echo -e "  ${GREEN}✓${NC} Unit tests: $result"
    ((PASS++))
else
    echo -e "  ${RED}✗${NC} Unit tests failed"
    ((FAIL++))
fi

if python3 integration_test.py &>/dev/null; then
    result=$(python3 integration_test.py 2>&1 | grep -oP '\d+ passed')
    echo -e "  ${GREEN}✓${NC} Integration tests: $result"
    ((PASS++))
else
    echo -e "  ${YELLOW}⚠${NC} Integration tests — some failures (may need tool installs)"
    ((WARN++))
fi

# ── SECURITY CHECKS ──
echo -e "\n${CYAN}[SECURITY]${NC}"
check "No shell=True in modules" "! grep -rn 'shell=True' $HEXSTRIKE/*.py 2>/dev/null | grep -v '#' | grep -qv 'CRITICAL\|SAFE\|never\|comment'"
check "No hardcoded API keys" "! grep -rni 'api_key\s*=\s*.[a-zA-Z0-9]' $HEXSTRIKE/*.py 2>/dev/null | grep -qv 'your.*key\|YOUR.*KEY\|example\|placeholder\|env\|os.environ'"

# ── SUMMARY ──
TOTAL=$((PASS + FAIL + WARN))
echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}PASSED: $PASS${NC}  ${RED}FAILED: $FAIL${NC}  ${YELLOW}WARNINGS: $WARN${NC}  TOTAL: $TOTAL"
echo -e "${BOLD}═══════════════════════════════════════════════════${NC}"

if [ $FAIL -eq 0 ]; then
    echo -e "\n  ${GREEN}💀 DEPLOYMENT VALIDATED — Kali Agent is ready${NC}"
    echo ""
    echo "  Start HexStrike:  cd $HEXSTRIKE && python3 hexstrike_mcp.py"
    echo "  Operations guide: $KALISHARE/docs/kali-operations-guide.md"
    echo "  First engagement: Tell Claude 'Initialize a CTF pentest against 10.10.10.5'"
elif [ $FAIL -le 3 ]; then
    echo -e "\n  ${YELLOW}⚠ MOSTLY READY — fix the $FAIL failure(s) above${NC}"
else
    echo -e "\n  ${RED}✗ NEEDS ATTENTION — $FAIL items failed${NC}"
    echo "  Review output above and re-run Stage 6 or install missing components."
fi
echo ""
