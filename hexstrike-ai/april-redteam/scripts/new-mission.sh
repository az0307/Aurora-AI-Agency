#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# new-mission.sh — Initialize a new engagement workspace
# Usage: ./scripts/new-mission.sh [NAME] [TARGET] [TYPE]
# Types: web | network | ad | mobile | cloud | wireless |
#        ctf | bugbounty | osint | social | container | cicd
# ─────────────────────────────────────────────────────────────

set -euo pipefail
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; BLU='\033[0;34m'; NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="${1:-mission-$(date +%Y%m%d-%H%M)}"
TARGET="${2:-unknown}"
TYPE="${3:-web}"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
LOOT="$ROOT_DIR/loot/$NAME"

log()  { echo -e "${GRN}[+]${NC} $*"; }
warn() { echo -e "${YLW}[!]${NC} $*"; }
info() { echo -e "${BLU}[*]${NC} $*"; }

# ── Validation ────────────────────────────────────────────────
VALID_TYPES="web network ad mobile cloud wireless ctf bugbounty osint social container cicd"
if ! echo "$VALID_TYPES" | grep -qw "$TYPE"; then
    echo -e "${RED}Unknown type: $TYPE${NC}"
    echo "Valid: $VALID_TYPES"
    exit 1
fi

if [[ -d "$LOOT" ]]; then
    warn "Mission '$NAME' already exists at $LOOT"
    read -r -p "Overwrite? [y/N]: " ans
    [[ "$ans" == "y" ]] || exit 0
fi

# ── Playbook mapping ──────────────────────────────────────────
declare -A PLAYBOOK_MAP
PLAYBOOK_MAP[web]="web-app-full"
PLAYBOOK_MAP[network]="network-pentest"
PLAYBOOK_MAP[ad]="ad-attack"
PLAYBOOK_MAP[mobile]="mobile-pentest"
PLAYBOOK_MAP[cloud]="cloud-aws"
PLAYBOOK_MAP[wireless]="wireless-rf"
PLAYBOOK_MAP[ctf]="ctf-htb"
PLAYBOOK_MAP[bugbounty]="bug-bounty"
PLAYBOOK_MAP[osint]="autogpt-osint"
PLAYBOOK_MAP[social]="social-engineering"
PLAYBOOK_MAP[container]="container-k8s"
PLAYBOOK_MAP[cicd]="cicd-pipeline"
PLAYBOOK="${PLAYBOOK_MAP[$TYPE]:-web-app-full}"

# ── Directory structure ───────────────────────────────────────
info "Creating engagement workspace..."
mkdir -p "$LOOT"/{osint,recon,scans,threat_model,exploits,screenshots,evidence,monitoring,passwords}
touch "$LOOT"/{osint,recon,scans,threat_model,exploits,screenshots,evidence,monitoring,passwords}/.gitkeep

# ── mission.md ────────────────────────────────────────────────
cat > "$LOOT/mission.md" << MEOF
# MISSION: $NAME
**Created:** $DATE $TIME
**Target:** $TARGET
**Type:** $TYPE
**Status:** Active
**Playbook:** playbooks/$PLAYBOOK.md

---

## Authorization

**Client:**
**Contact name:**
**Contact phone:**
**Emergency stop:**
**Authorization ref:**
**Get-out-of-jail letter:** loot/$NAME/auth_letter.pdf

Authorization checklist:
- [ ] Written authorization confirmed
- [ ] Scope document reviewed and signed
- [ ] Rules of engagement agreed
- [ ] Emergency contact numbers saved
- [ ] Testing window confirmed

---

## Scope

### In Scope

| Asset | Type | Notes |
|-------|------|-------|
| $TARGET | Primary target | |

### Out of Scope

| Asset | Reason |
|-------|--------|
| (add out-of-scope assets here) | |

### Rules of Engagement
- Rate limiting: [MAX REQUESTS/SEC]
- Destructive testing: [YES/NO]
- Social engineering: [IN SCOPE / OUT OF SCOPE]
- Testing window: [HOURS / ANY TIME]

---

## Timeline

| Phase | Date | Status |
|-------|------|--------|
| Threat modeling | | Planned |
| OSINT / passive recon | | Planned |
| Attack planning | | Planned |
| Active recon | | Planned |
| Vulnerability scan | | Planned |
| Manual testing | | Planned |
| Exploitation | | Planned |
| Reporting | | Planned |

---

## Active Findings Summary

| ID | Severity | Title | Asset | Status |
|----|---------|-------|-------|--------|
| (populated from findings.md) | | | | |

---

## Notes

_Running notes — update throughout engagement._

MEOF

# ── findings.md ───────────────────────────────────────────────
cat > "$LOOT/findings.md" << FEOF
# FINDINGS LOG — $NAME
# Started: $DATE | Target: $TARGET | Type: $TYPE
# Update this file as findings are confirmed — do NOT batch at end

---

## CRITICAL

_No critical findings yet._

---

## HIGH

_No high findings yet._

---

## MEDIUM

_No medium findings yet._

---

## LOW

_No low findings yet._

---

## INFORMATIONAL

_No informational findings yet._

---

## Finding Template (copy for each new finding)

### [FN] [TITLE]

- **Date found:** $DATE
- **Asset:** [URL / IP:PORT]
- **Severity:** [Critical/High/Medium/Low]
- **CVSS:** [SCORE] ([VECTOR])
- **Tool:** [HexStrike / Kali MCP / Manual / PentestGPT / VulnGPT]
- **Evidence:** screenshots/[filename].png
- **Status:** [New / Confirmed / Exploited / Documented]
- **Notes:** [Brief technical notes]

FEOF

# ── hosts.txt ─────────────────────────────────────────────────
cat > "$LOOT/hosts.txt" << HEOF
# DISCOVERED HOSTS — $NAME
# Format: IP | HOSTNAME | OS | OPEN_PORTS | NOTES
$TARGET | | | |
HEOF

# ── notes.json (Shadow Graph seed for PentestAgent) ───────────
cat > "$LOOT/notes.json" << JEOF
{
  "mission": "$NAME",
  "target": "$TARGET",
  "type": "$TYPE",
  "created": "$DATE",
  "credentials": [],
  "vulnerabilities": [],
  "findings": [],
  "artifacts": [],
  "hosts": [
    {
      "ip": "$TARGET",
      "hostname": "",
      "os": "",
      "services": [],
      "notes": ""
    }
  ],
  "attack_paths": [],
  "loot_path": "loot/$NAME/"
}
JEOF

# ── Validate scope immediately ────────────────────────────────
if [[ -x "$ROOT_DIR/scripts/scope-validator.sh" ]] && [[ "$TYPE" != "osint" ]]; then
    "$ROOT_DIR/scripts/scope-validator.sh" "$TARGET" "$NAME" 2>/dev/null || \
        warn "Scope validation skipped — add target to mission.md In Scope table"
fi

# ── Audit log ─────────────────────────────────────────────────
mkdir -p "$ROOT_DIR/logs"
echo "$(date -Iseconds) | NEW_MISSION | name=$NAME | target=$TARGET | type=$TYPE | user=$(whoami)" \
    >> "$ROOT_DIR/logs/audit.log"

# ── Output ────────────────────────────────────────────────────
echo ""
echo -e "${GRN}══════════════════════════════════════════════${NC}"
echo -e "${GRN}  MISSION INITIALIZED: $NAME${NC}"
echo -e "${GRN}══════════════════════════════════════════════${NC}"
echo ""
echo -e "  Target:  ${YLW}$TARGET${NC}"
echo -e "  Type:    ${YLW}$TYPE${NC}"
echo -e "  Loot:    ${YLW}loot/$NAME/${NC}"
echo -e "  Playbook:${YLW}playbooks/$PLAYBOOK.md${NC}"
echo ""
echo "  Files created:"
echo "    loot/$NAME/mission.md    ← Fill in scope + auth details"
echo "    loot/$NAME/findings.md   ← Update as you find things"
echo "    loot/$NAME/notes.json    ← Shadow Graph seed"
echo ""
echo -e "  ${BLU}Checklist before testing:${NC}"
echo "    □ Fill in authorization section of mission.md"
echo "    □ Confirm scope table is accurate"
echo "    □ Save emergency contact phone numbers"
echo ""
echo -e "  ${YLW}Claude Code prompt:${NC}"
echo ""
echo "  ┌─────────────────────────────────────────────────────"
case "$TYPE" in
    ctf)
        echo "  │ Authorized lab — working on $TARGET"
        echo "  │ Mission: $NAME"
        echo "  │ Load playbooks/ctf-htb.md and begin."
        echo "  │ Use PentestGPT autonomous mode first."
        ;;
    bugbounty)
        echo "  │ Authorized bug bounty researcher."
        echo "  │ Target: $TARGET | Program: [ADD URL]"
        echo "  │ Mission: $NAME"
        echo "  │ Load playbooks/bug-bounty.md."
        echo "  │ Start with AutoGPT passive OSINT."
        ;;
    osint)
        echo "  │ Passive OSINT on $TARGET — no active scanning."
        echo "  │ Mission: $NAME"
        echo "  │ Load playbooks/autogpt-osint.md."
        echo "  │ Save all output to loot/$NAME/osint/"
        ;;
    *)
        echo "  │ Authorized $TYPE penetration test."
        echo "  │ Target: $TARGET | Auth: [ADD REF]"
        echo "  │ Mission: $NAME"
        echo "  │ Load playbooks/$PLAYBOOK.md."
        echo "  │ Run PentestThinkingMCP planning first."
        echo "  │ Store all findings to loot/$NAME/"
        ;;
esac
echo "  └─────────────────────────────────────────────────────"
echo ""
