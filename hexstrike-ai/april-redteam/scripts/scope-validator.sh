#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# scope-validator.sh — Validate target is in authorized scope
# Called by HexStrike + Kali MCP before any active scan
# Usage: ./scripts/scope-validator.sh [TARGET] [MISSION]
#        Returns 0 (authorized) or 1 (blocked)
# ─────────────────────────────────────────────────────────────

set -euo pipefail
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; NC='\033[0m'

TARGET="${1:-}"
MISSION="${2:-}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ── Always-blocked targets (regardless of scope) ──────────────
ALWAYS_BLOCK=(
    "0.0.0.0"
    "127.0.0.1"
    "localhost"
    "169.254.169.254"    # Cloud metadata (allow only if explicitly stated)
    "::1"
)

err_block() {
    echo -e "${RED}[BLOCKED]${NC} $*" >&2
    exit 1
}
warn() { echo -e "${YLW}[WARN]${NC} $*" >&2; }
ok()   { echo -e "${GRN}[AUTH]${NC} $*"; }

if [[ -z "$TARGET" ]]; then
    echo "Usage: $0 [TARGET_IP_OR_DOMAIN] [MISSION_NAME]"
    echo "Example: $0 target.com acme-webapp"
    exit 1
fi

# ── Check always-blocked list ─────────────────────────────────
for blocked in "${ALWAYS_BLOCK[@]}"; do
    if [[ "$TARGET" == "$blocked" ]]; then
        err_block "$TARGET is in always-blocked list"
    fi
done

# ── Check if enforcement is enabled ───────────────────────────
if [[ "${ENFORCE_AUTH_CHECK:-true}" != "true" ]]; then
    warn "Authorization check DISABLED (ENFORCE_AUTH_CHECK=false)"
    warn "This is a security risk — only disable for lab environments"
    ok "$TARGET — ENFORCEMENT DISABLED"
    exit 0
fi

# ── Load mission scope ────────────────────────────────────────
if [[ -n "$MISSION" ]]; then
    SCOPE_FILE="$ROOT_DIR/loot/$MISSION/mission.md"
    
    if [[ ! -f "$SCOPE_FILE" ]]; then
        err_block "Mission '$MISSION' not found — run: make new-mission NAME=$MISSION"
    fi
    
    # Extract scope from mission.md (lines after "In Scope" table)
    SCOPE_ENTRIES=$(grep -A50 "In Scope" "$SCOPE_FILE" 2>/dev/null | \
                    grep '^\|' | \
                    grep -v 'Asset\|----' | \
                    awk -F'|' '{print $2}' | \
                    tr -d ' ' || echo "")
    
    # Check if target matches any scope entry
    AUTHORIZED=false
    while IFS= read -r scope_entry; do
        [[ -z "$scope_entry" ]] && continue
        
        # Exact match
        if [[ "$TARGET" == "$scope_entry" ]]; then
            AUTHORIZED=true
            break
        fi
        
        # Wildcard domain match (*.example.com → sub.example.com)
        if [[ "$scope_entry" == \*.* ]]; then
            domain="${scope_entry#*.}"
            if [[ "$TARGET" == *".$domain" || "$TARGET" == "$domain" ]]; then
                AUTHORIZED=true
                break
            fi
        fi
        
        # CIDR range check (basic - checks if target IP is in subnet)
        if [[ "$scope_entry" == *"/"* ]] && command -v python3 &>/dev/null; then
            in_range=$(python3 -c "
import ipaddress, sys
try:
    net = ipaddress.ip_network('$scope_entry', strict=False)
    addr = ipaddress.ip_address('$TARGET')
    print('yes' if addr in net else 'no')
except:
    print('no')
" 2>/dev/null)
            if [[ "$in_range" == "yes" ]]; then
                AUTHORIZED=true
                break
            fi
        fi
    done <<< "$SCOPE_ENTRIES"
    
    if [[ "$AUTHORIZED" != "true" ]]; then
        echo -e "${RED}══════════════════════════════════════════════${NC}" >&2
        echo -e "${RED}  OUT OF SCOPE — SCAN BLOCKED                 ${NC}" >&2
        echo -e "${RED}══════════════════════════════════════════════${NC}" >&2
        echo -e "  Target: ${RED}$TARGET${NC}" >&2
        echo -e "  Mission: $MISSION" >&2
        echo "" >&2
        echo "  Authorized scope:" >&2
        while IFS= read -r entry; do
            [[ -n "$entry" ]] && echo "    → $entry" >&2
        done <<< "$SCOPE_ENTRIES"
        echo "" >&2
        echo "  To add this target: update loot/$MISSION/mission.md" >&2
        echo "  Confirm with client that it is authorized" >&2
        exit 1
    fi
    
    ok "$TARGET is authorized in scope: $MISSION"
    
    # Log to audit trail
    AUDIT_LOG="${AUDIT_LOG_PATH:-$ROOT_DIR/logs/audit.log}"
    mkdir -p "$(dirname "$AUDIT_LOG")"
    echo "$(date -Iseconds) | SCOPE_CHECK | PASS | target=$TARGET | mission=$MISSION | user=$(whoami)" >> "$AUDIT_LOG"
    
    exit 0

else
    # No mission specified — prompt for manual confirmation
    echo -e "${YLW}══════════════════════════════════════════════${NC}"
    echo -e "${YLW}  NO MISSION SPECIFIED — MANUAL AUTH REQUIRED ${NC}"
    echo -e "${YLW}══════════════════════════════════════════════${NC}"
    echo ""
    echo "  Target: $TARGET"
    echo ""
    echo "  Confirm authorization to scan this target."
    echo "  By proceeding you confirm:"
    echo "    □ You own this system, OR"
    echo "    □ You have explicit written authorization to test it"
    echo ""
    read -r -p "  Type 'I AUTHORIZE' to proceed: " confirm
    
    if [[ "$confirm" != "I AUTHORIZE" ]]; then
        echo -e "${RED}[BLOCKED]${NC} Authorization not confirmed" >&2
        exit 1
    fi
    
    ok "$TARGET — manually authorized by operator"
    
    AUDIT_LOG="${AUDIT_LOG_PATH:-$ROOT_DIR/logs/audit.log}"
    mkdir -p "$(dirname "$AUDIT_LOG")"
    echo "$(date -Iseconds) | SCOPE_CHECK | MANUAL_AUTH | target=$TARGET | user=$(whoami)" >> "$AUDIT_LOG"
    
    exit 0
fi
