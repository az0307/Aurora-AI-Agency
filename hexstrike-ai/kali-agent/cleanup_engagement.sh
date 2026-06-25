#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# KALI AGENT — ENGAGEMENT CLEANUP
# Securely removes pentest data after report delivery.
# 
# Usage: ./cleanup_engagement.sh ENG-2026-001
#    Or: ./cleanup_engagement.sh --all
# 
# ⚠️ This is DESTRUCTIVE. Data cannot be recovered after cleanup.
# AutoBoros.ai | 2026-03-27
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PENTEST_BASE="/tmp/pentest"

if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <engagement_id> [--confirm]${NC}"
    echo "   Or: $0 --all [--confirm]"
    echo ""
    echo "Active engagements:"
    if [ -d "$PENTEST_BASE" ]; then
        ls -d "${PENTEST_BASE}"/*/ 2>/dev/null | while read d; do
            eid=$(basename "$d")
            files=$(find "$d" -type f | wc -l)
            size=$(du -sh "$d" 2>/dev/null | cut -f1)
            echo "  ${eid} — ${files} files, ${size}"
        done
    else
        echo "  (none)"
    fi
    exit 1
fi

ENGAGEMENT_ID="$1"
CONFIRM="${2:-}"

cleanup_engagement() {
    local eid="$1"
    local edir="${PENTEST_BASE}/${eid}"

    if [ ! -d "$edir" ]; then
        echo -e "${YELLOW}[WARN] Directory not found: ${edir}${NC}"
        return 1
    fi

    local file_count=$(find "$edir" -type f | wc -l)
    local total_size=$(du -sh "$edir" 2>/dev/null | cut -f1)

    echo ""
    echo -e "${RED}═══════════════════════════════════════════${NC}"
    echo -e "${RED}  ENGAGEMENT CLEANUP: ${eid}${NC}"
    echo -e "${RED}═══════════════════════════════════════════${NC}"
    echo ""
    echo "  Directory:  ${edir}"
    echo "  Files:      ${file_count}"
    echo "  Size:       ${total_size}"
    echo ""

    # Show what will be deleted
    echo "  Contents:"
    find "$edir" -type f | head -20 | while read f; do
        echo "    $(basename "$f")"
    done
    [ "$file_count" -gt 20 ] && echo "    ... and $((file_count - 20)) more"
    echo ""

    # Check if reports were exported
    if [ -d "${edir}/reports" ]; then
        echo -e "${GREEN}  ✓ Reports directory found — ensure delivered before cleanup${NC}"
    fi
    if [ -d "${edir}/exports" ]; then
        echo -e "${GREEN}  ✓ Exports directory found — ensure synced before cleanup${NC}"
    fi

    if [ "$CONFIRM" != "--confirm" ]; then
        echo ""
        echo -e "${YELLOW}  Add --confirm to actually delete.${NC}"
        echo -e "${YELLOW}  Example: $0 ${eid} --confirm${NC}"
        return 0
    fi

    # Archive audit log before deletion (keep compliance trail)
    local archive_dir="${HOME}/.hexstrike/archives"
    mkdir -p "$archive_dir"

    if [ -f "${edir}/audit.jsonl" ]; then
        local archive_name="${eid}_audit_$(date +%Y%m%d%H%M%S).jsonl.gz"
        gzip -c "${edir}/audit.jsonl" > "${archive_dir}/${archive_name}"
        echo -e "${GREEN}  ✓ Audit log archived: ${archive_dir}/${archive_name}${NC}"
    fi

    if [ -f "${edir}/scope_audit.jsonl" ]; then
        local scope_archive="${eid}_scope_$(date +%Y%m%d%H%M%S).jsonl.gz"
        gzip -c "${edir}/scope_audit.jsonl" > "${archive_dir}/${scope_archive}"
        echo -e "${GREEN}  ✓ Scope log archived: ${archive_dir}/${scope_archive}${NC}"
    fi

    # Securely delete tool outputs (overwrite + remove)
    echo ""
    echo "  Securely removing files..."

    # Use shred if available (overwrites before delete)
    if command -v shred &>/dev/null; then
        find "$edir" -type f -exec shred -uzn 3 {} \; 2>/dev/null
        echo -e "${GREEN}  ✓ Files shredded (3-pass overwrite)${NC}"
    else
        # Fallback: normal delete
        rm -rf "$edir"
        echo -e "${YELLOW}  ⚠ Files deleted (shred not available — install coreutils for secure delete)${NC}"
    fi

    # Remove directory
    rm -rf "$edir" 2>/dev/null
    echo -e "${GREEN}  ✓ Directory removed: ${edir}${NC}"
    echo ""
    echo -e "${GREEN}  Cleanup complete for ${eid}${NC}"
    echo -e "${GREEN}  Audit logs preserved in: ${archive_dir}/${NC}"
}

if [ "$ENGAGEMENT_ID" = "--all" ]; then
    echo -e "${RED}Cleaning ALL engagements in ${PENTEST_BASE}${NC}"
    if [ -d "$PENTEST_BASE" ]; then
        for dir in "${PENTEST_BASE}"/*/; do
            [ -d "$dir" ] || continue
            eid=$(basename "$dir")
            cleanup_engagement "$eid"
        done
    fi
else
    cleanup_engagement "$ENGAGEMENT_ID"
fi
