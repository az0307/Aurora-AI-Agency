#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# generate-report.sh — Assemble pentest report from loot/
# Extracts findings, stats, and creates a Claude Code prompt
# Usage: ./scripts/generate-report.sh [MISSION]
# ─────────────────────────────────────────────────────────────

set -euo pipefail
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; BLU='\033[0;34m'; NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MISSION="${1:-}"

log()  { echo -e "${GRN}[+]${NC} $*"; }
warn() { echo -e "${YLW}[!]${NC} $*"; }
info() { echo -e "${BLU}[*]${NC} $*"; }
err()  { echo -e "${RED}[-]${NC} $*" >&2; exit 1; }

if [[ -z "$MISSION" ]]; then
    echo "Usage: $0 [MISSION_NAME]"
    echo ""
    echo "Available missions:"
    find "$ROOT_DIR/loot/" -mindepth 1 -maxdepth 1 -type d | sort | while read d; do
        name=$(basename "$d")
        count=$(grep -c "^### \[F" "$d/findings.md" 2>/dev/null || echo "0")
        echo "  $name ($count findings)"
    done
    exit 1
fi

LOOT="$ROOT_DIR/loot/$MISSION"
[[ -d "$LOOT" ]] || err "Mission not found: $MISSION"

echo ""
echo -e "${BLU}══════════════════════════════════════════${NC}"
echo -e "${BLU}  REPORT GENERATOR — $MISSION${NC}"
echo -e "${BLU}══════════════════════════════════════════${NC}"
echo ""

# ── Copy template ─────────────────────────────────────────────
if [[ ! -f "$LOOT/report.md" ]]; then
    cp "$ROOT_DIR/loot/REPORT_TEMPLATE.md" "$LOOT/report.md"
    log "Report template copied"
fi

# ── Parse findings ────────────────────────────────────────────
FINDINGS_FILE="$LOOT/findings.md"
MISSION_FILE="$LOOT/mission.md"

CRITICAL=0; HIGH=0; MEDIUM=0; LOW=0; INFO=0; TOTAL=0

if [[ -f "$FINDINGS_FILE" ]]; then
    CRITICAL=$(grep -c "Severity.*Critical\|Critical.*Severity" "$FINDINGS_FILE" 2>/dev/null || echo 0)
    HIGH=$(grep -c "Severity.*High\|High.*Severity" "$FINDINGS_FILE" 2>/dev/null || echo 0)
    MEDIUM=$(grep -c "Severity.*Medium\|Medium.*Severity" "$FINDINGS_FILE" 2>/dev/null || echo 0)
    LOW=$(grep -c "Severity.*Low\|Low.*Severity" "$FINDINGS_FILE" 2>/dev/null || echo 0)
    TOTAL=$((CRITICAL + HIGH + MEDIUM + LOW))
fi

info "Findings parsed:"
echo "  Critical: $CRITICAL"
echo "  High:     $HIGH"
echo "  Medium:   $MEDIUM"
echo "  Low:      $LOW"
echo "  Total:    $TOTAL"
echo ""

# ── Loot inventory ────────────────────────────────────────────
SUBDOMAINS=$(wc -l < "$LOOT/recon/subdomains.txt" 2>/dev/null || echo 0)
HOSTS=$(wc -l < "$LOOT/hosts.txt" 2>/dev/null || echo 0)
SCREENSHOTS=$(ls "$LOOT/screenshots/" 2>/dev/null | wc -l || echo 0)

info "Loot inventory:"
echo "  Subdomains: $SUBDOMAINS"
echo "  Hosts: $HOSTS"
echo "  Screenshots: $SCREENSHOTS"
echo ""

# ── Generate Claude Code prompt ───────────────────────────────
PROMPT_FILE="$LOOT/REPORT_PROMPT.md"

cat > "$PROMPT_FILE" << PROMPTEOF
# Report Generation Prompt — $MISSION
# Copy this prompt to Claude Code to auto-populate the report

---

Generate a professional penetration test report for mission: **$MISSION**

## Available Data (all in loot/$MISSION/)

**findings.md** — all confirmed findings
**mission.md** — scope, authorization, timeline
**threat_model/threat_model_final.md** — STRIDE correlation
**scans/nuclei_output.json** — automated scan results
**scans/nmap_services.xml** — network discovery
**osint/company_profile.md** — intelligence gathered

## Statistics to Include

| Severity | Count |
|----------|-------|
| Critical | $CRITICAL |
| High     | $HIGH |
| Medium   | $MEDIUM |
| Low      | $LOW |
| **Total**| **$TOTAL** |

Attack surface: $SUBDOMAINS subdomains, $HOSTS live hosts

## Instructions

1. Read findings.md completely
2. Read mission.md for scope/auth details
3. Read threat_model/threat_model_final.md for STRIDE correlation
4. Populate loot/$MISSION/report.md using the REPORT_TEMPLATE structure:
   - Executive Summary: business-language summary, risk rating, top finding
   - Scope: confirmed from mission.md
   - Threat Model: STRIDE findings mapped to confirmed vulnerabilities
   - Technical Findings: each finding with CVSS, steps to reproduce, remediation
   - Risk Register: findings in priority matrix
   - Remediation Roadmap: timeline by severity
5. Make the executive summary boardroom-ready — no jargon
6. Every technical finding needs: evidence reference, specific fix code/config

## Output

Save final report to: loot/$MISSION/report.md
Generate stats summary to: loot/$MISSION/report_stats.json
PROMPTEOF

log "Claude Code prompt written to: $LOOT/REPORT_PROMPT.md"

# ── Initialize report with auto-filled fields ─────────────────
DATE=$(date +%Y-%m-%d)
REPORT_ID="RT-$(date +%Y)-$(printf '%03d' $RANDOM)"

sed -i "s/\[REPORT_DATE\]/$DATE/g" "$LOOT/report.md" 2>/dev/null || true
sed -i "s/RT-\[YEAR\]-\[NUMBER\]/$REPORT_ID/g" "$LOOT/report.md" 2>/dev/null || true
sed -i "s/\[N\] Critical/$CRITICAL/g" "$LOOT/report.md" 2>/dev/null || true
sed -i "s/\[N\] High/$HIGH/g" "$LOOT/report.md" 2>/dev/null || true
sed -i "s/\[N\] Medium/$MEDIUM/g" "$LOOT/report.md" 2>/dev/null || true
sed -i "s/\[N\] Low/$LOW/g" "$LOOT/report.md" 2>/dev/null || true

log "report.md auto-populated with finding counts"

# ── Next steps ────────────────────────────────────────────────
echo ""
echo -e "${GRN}══════════════════════════════════════════${NC}"
echo -e "${GRN}  REPORT INITIALIZED${NC}"
echo -e "${GRN}══════════════════════════════════════════${NC}"
echo ""
echo "Files ready:"
echo "  loot/$MISSION/report.md         ← Report skeleton"
echo "  loot/$MISSION/REPORT_PROMPT.md  ← Claude Code prompt"
echo ""
echo "Next step — in Claude Code:"
echo "  Read REPORT_PROMPT.md and execute it to populate the full report"
echo ""
warn "Report contains $TOTAL findings. Estimated write-up time with AI: 15-30 min"
