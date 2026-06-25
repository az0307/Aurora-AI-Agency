#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# install-extended.sh — Install all 6 ecosystem tools from image
# Adds: PentestGPT, AutoGPT, VulnGPT, STRIDE-GPT
# Skips: WormGPT, ChaosGPT (malicious/experimental — not included)
# ─────────────────────────────────────────────────────────────

set -euo pipefail

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'
BLU='\033[0;34m'; CYN='\033[0;36m'; NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

log()  { echo -e "${GRN}[+]${NC} $*"; }
warn() { echo -e "${YLW}[!]${NC} $*"; }
skip() { echo -e "${BLU}[-]${NC} $* (skipping)"; }
info() { echo -e "${CYN}[i]${NC} $*"; }

echo ""
echo -e "${RED}══════════════════════════════════════════════════════${NC}"
echo -e "${RED}  EXTENDED ECOSYSTEM INSTALL — APRIL 2026              ${NC}"
echo -e "${RED}  Image: 'Best AI Tools Used By Hackers' (OxTrace)     ${NC}"
echo -e "${RED}══════════════════════════════════════════════════════${NC}"
echo ""
echo "Installing legitimate tools. Skipping malicious ones."
echo ""

# ── 1. PENTESTGPT (GreyDGL — USENIX Security 2024) ───────────
echo -e "${CYN}[1/4] PentestGPT — Autonomous Pentest Agent${NC}"
echo "      USENIX Security 2024 | 86.5% XBOW success rate"
echo "      github.com/GreyDGL/PentestGPT"
echo ""

if [[ ! -d "pentestgpt" ]]; then
    log "Cloning PentestGPT..."
    git clone --recurse-submodules \
        https://github.com/GreyDGL/PentestGPT.git pentestgpt
    cd pentestgpt
    log "Building PentestGPT..."
    make install 2>/dev/null || pip3 install --break-system-packages -e . 2>/dev/null || \
    pip3 install -e .
    cd ..
    log "PentestGPT installed"
else
    log "PentestGPT already cloned — pulling latest..."
    git -C pentestgpt pull origin main 2>/dev/null || true
fi

# ── 2. VULNGPT — GPT_Vuln-analyzer (morpheuslord) ────────────
echo ""
echo -e "${CYN}[2/4] VulnGPT — AI Vulnerability Analyzer${NC}"
echo "      Nmap + DNS + PCAP + JWT + LLM reporting"
echo "      github.com/morpheuslord/GPT_Vuln-analyzer"
echo ""

if [[ ! -d "vulngpt" ]]; then
    log "Cloning VulnGPT (GPT_Vuln-analyzer)..."
    git clone https://github.com/morpheuslord/GPT_Vuln-analyzer.git vulngpt
    cd vulngpt
    pip3 install --break-system-packages -r requirements.txt 2>/dev/null || \
    pip3 install -r requirements.txt
    cd ..
    log "VulnGPT installed"
else
    log "VulnGPT already cloned"
fi

# Also get VulnGPT v2 (FastAPI + Shodan)
if [[ ! -d "vulngpt-v2" ]]; then
    log "Cloning VulnGPT v2 (FastAPI + Shodan)..."
    git clone https://github.com/paulshovon94/VulnGPT.git vulngpt-v2
    cd vulngpt-v2
    pip3 install --break-system-packages -r requirements.txt 2>/dev/null || \
    pip3 install -r requirements.txt
    cd ..
    log "VulnGPT v2 installed"
fi

# ── 3. STRIDE-GPT / THREATGPT (mrwadams) ─────────────────────
echo ""
echo -e "${CYN}[3/4] ThreatGPT / STRIDE-GPT — AI Threat Modeling${NC}"
echo "      STRIDE methodology | streamlit web UI"
echo "      github.com/mrwadams/stride-gpt"
echo ""

if [[ ! -d "stride-gpt" ]]; then
    log "Cloning STRIDE-GPT..."
    git clone https://github.com/mrwadams/stride-gpt.git stride-gpt
    cd stride-gpt
    pip3 install --break-system-packages -r requirements.txt 2>/dev/null || \
    pip3 install -r requirements.txt
    cd ..
    log "STRIDE-GPT installed"
else
    log "STRIDE-GPT already cloned"
fi

# ── 4. AUTOGPT (Significant Gravitas) ────────────────────────
echo ""
echo -e "${CYN}[4/4] AutoGPT — Autonomous AI Agent${NC}"
echo "      OSINT, monitoring, intelligence automation"
echo "      github.com/Significant-Gravitas/AutoGPT"
echo "      (170k stars — largest AI project on GitHub)"
echo ""

if [[ ! -d "autogpt" ]]; then
    log "Cloning AutoGPT..."
    git clone https://github.com/Significant-Gravitas/AutoGPT.git autogpt
    # AutoGPT has its own setup — don't pip install globally
    log "AutoGPT cloned — run 'cd autogpt && docker compose up' to start"
else
    log "AutoGPT already cloned"
fi

# ── SKIPPED TOOLS ─────────────────────────────────────────────
echo ""
echo -e "${RED}══════════════════════════════════════════════════════${NC}"
echo -e "${RED}  SKIPPED — MALICIOUS / NOT INCLUDED                   ${NC}"
echo -e "${RED}══════════════════════════════════════════════════════${NC}"
echo ""
skip "WormGPT — dark web malicious LLM (jailbroken GPT-J)"
info "       Documented in docs/ai-tools-ecosystem.md for threat intel"
info "       Use case: understanding BEC phishing threats, defensive only"
echo ""
skip "ChaosGPT — adversarial AutoGPT experiment (2023)"
info "       Documented in docs/ai-tools-ecosystem.md for context"
info "       Not a functional security tool"
echo ""

# ── UPDATE ENVIRONMENT ────────────────────────────────────────
echo -e "${GRN}══════════════════════════════════════════════════════${NC}"
echo -e "${GRN}  UPDATING CONFIGURATION                               ${NC}"
echo -e "${GRN}══════════════════════════════════════════════════════${NC}"
echo ""

# Add new env vars to .env.example if not already there
if ! grep -q "SHODAN_API_KEY" .env.example 2>/dev/null; then
    cat >> .env.example << 'ENVEOF'

# ── EXTENDED ECOSYSTEM ──────────────────────────────────────
# VulnGPT v2 — Shodan integration
SHODAN_API_KEY=

# STRIDE-GPT / ThreatGPT
# Uses ANTHROPIC_API_KEY already set above

# AutoGPT
# Uses ANTHROPIC_API_KEY or OPENAI_API_KEY already set above
ENVEOF
    log "Updated .env.example with new vars"
fi

# Update .gitignore for new repos
for repo in pentestgpt vulngpt vulngpt-v2 stride-gpt autogpt; do
    if ! grep -q "^${repo}/" .gitignore 2>/dev/null; then
        echo "${repo}/" >> .gitignore
    fi
done
log "Updated .gitignore"

# ── SUMMARY ───────────────────────────────────────────────────
echo ""
echo -e "${GRN}══════════════════════════════════════════════════════${NC}"
echo -e "${GRN}  EXTENDED ECOSYSTEM READY                             ${NC}"
echo -e "${GRN}══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${CYN}From the OxTrace image — installation status:${NC}"
echo ""
echo -e "  ${GRN}✓${NC} WormGPT    → SKIPPED (malicious) | threat intel: docs/"
echo -e "  ${GRN}✓${NC} PentestGPT → INSTALLED | pentestgpt/"
echo -e "  ${GRN}✓${NC} ChaosGPT   → SKIPPED (experiment) | docs for context"
echo -e "  ${GRN}✓${NC} AutoGPT    → INSTALLED | autogpt/"
echo -e "  ${GRN}✓${NC} VulnGPT    → INSTALLED | vulngpt/ + vulngpt-v2/"
echo -e "  ${GRN}✓${NC} ThreatGPT  → INSTALLED | stride-gpt/ (STRIDE-GPT)"
echo ""
echo "  Quick start:"
echo ""
echo -e "  ${YLW}# PentestGPT autonomous mode:${NC}"
echo -e "  cd pentestgpt && make config && make connect"
echo -e "  pentestgpt --target [IP] --no-telemetry"
echo ""
echo -e "  ${YLW}# VulnGPT analyzer:${NC}"
echo -e "  cd vulngpt && python3 main.py --target [IP]"
echo ""
echo -e "  ${YLW}# ThreatGPT / STRIDE-GPT:${NC}"
echo -e "  cd stride-gpt && streamlit run app.py"
echo -e "  # Then open http://localhost:8501"
echo ""
echo -e "  ${YLW}# Full playbook:${NC}"
echo -e "  cat playbooks/pentestgpt-integration.md"
echo ""
