#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# healthcheck.sh — Verify all stack services are running
# ─────────────────────────────────────────────────────────────

set -euo pipefail

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; NC='\033[0m'

pass() { echo -e "  ${GRN}✓${NC}  $*"; }
fail() { echo -e "  ${RED}✗${NC}  $*"; FAILED=1; }
warn() { echo -e "  ${YLW}?${NC}  $*"; }

FAILED=0

echo ""
echo "══════════════════════════════════════"
echo "  APRIL 2026 RED TEAM STACK — HEALTH"
echo "══════════════════════════════════════"
echo ""

# ── HexStrike ─────────────────────────────────────────────────
echo "HexStrike AI:"
if curl -sf http://localhost:8888/health &>/dev/null; then
  RESP=$(curl -sf http://localhost:8888/health)
  pass "API responding — $RESP"
else
  fail "API not responding on :8888"
fi

if curl -sf http://localhost:8888/api/tools/list &>/dev/null; then
  COUNT=$(curl -sf http://localhost:8888/api/tools/list | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('tools', d.get('data', []))))" 2>/dev/null || echo "?")
  pass "Tools endpoint OK — ~$COUNT tools loaded"
else
  warn "Tools endpoint not responding (may be loading)"
fi

# ── Kali MCP ─────────────────────────────────────────────────
echo ""
echo "Kali MCP:"
if curl -sf http://localhost:8000/health &>/dev/null 2>&1 || \
   nc -z localhost 8000 &>/dev/null 2>&1; then
  pass "Kali MCP reachable on :8000"
else
  fail "Kali MCP not reachable on :8000"
fi

if nc -z localhost 2222 &>/dev/null 2>&1; then
  pass "Kali SSH reachable on :2222"
else
  warn "Kali SSH not reachable on :2222 (may not be enabled)"
fi

# ── Redis ─────────────────────────────────────────────────────
echo ""
echo "Redis:"
if docker exec rt-redis redis-cli ping &>/dev/null 2>&1; then
  pass "Redis responding (PONG)"
else
  fail "Redis not responding"
fi

# ── Postgres ─────────────────────────────────────────────────
echo ""
echo "PostgreSQL:"
if docker exec rt-postgres pg_isready -U rt -d redteam &>/dev/null 2>&1; then
  pass "PostgreSQL ready"
else
  fail "PostgreSQL not ready"
fi

# ── Grafana ──────────────────────────────────────────────────
echo ""
echo "Grafana:"
if curl -sf http://localhost:3000/api/health &>/dev/null; then
  pass "Grafana responding on :3000"
else
  warn "Grafana not responding on :3000 (optional service)"
fi

# ── Claude Code ──────────────────────────────────────────────
echo ""
echo "Claude Code:"
if command -v claude &>/dev/null; then
  VERSION=$(claude --version 2>/dev/null || echo "installed")
  pass "claude CLI available — $VERSION"
else
  warn "claude CLI not found — install: npm install -g @anthropic-ai/claude-code"
fi

if [[ -f "$HOME/.config/claude/claude.json" ]]; then
  SERVERS=$(python3 -c "import json; d=json.load(open('$HOME/.config/claude/claude.json')); print(len(d.get('mcpServers', {})))" 2>/dev/null || echo "?")
  pass "claude.json found — $SERVERS MCP servers configured"
else
  warn "claude.json not found at ~/.config/claude/claude.json"
fi

# ── Environment ───────────────────────────────────────────────
echo ""
echo "Environment:"
if [[ -f ".env" ]]; then
  if grep -q "change-me" .env; then
    warn ".env exists but has unchanged placeholder values — review it!"
  else
    pass ".env exists and appears configured"
  fi
else
  fail ".env not found — copy from .env.example"
fi

# ── Final ────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════"
if [[ $FAILED -eq 0 ]]; then
  echo -e "  ${GRN}ALL CHECKS PASSED${NC}"
  echo ""
  echo -e "  Start Claude Code:"
  echo -e "  ${YLW}claude --dangerously-skip-permissions${NC}"
else
  echo -e "  ${RED}SOME CHECKS FAILED — review above${NC}"
  echo ""
  echo "  To restart the stack: docker compose restart"
  echo "  To view logs: docker compose logs -f hexstrike"
fi
echo "══════════════════════════════════════"
echo ""

exit $FAILED
