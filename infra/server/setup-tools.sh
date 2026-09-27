#!/usr/bin/env bash
# setup-tools.sh — one-time setup of the operator tools ON THE SERVER (run as `aurora`).
#
#   bash /opt/aurora/server/setup-tools.sh            # install everything (idempotent)
#   bash /opt/aurora/server/setup-tools.sh --refresh  # just re-install scripts/configs/icons
#                                                      # (what `aurora update` runs)
#
# Installs:
#   - apt: whiptail fzf jq rsync git (menu + helpers), adb (S10 over the tailnet; see
#     phones/FLASHING.md), Node.js 22 if missing (NodeSource)
#   - npm (global): opencode-ai (OpenCode), @anthropic-ai/claude-code (Claude Code)
#   - /usr/local/bin/aurora        the menu (TUI): status, start/stop, logs, agents, links, update
#   - /usr/local/bin/aurora-agent  runs an agent with the router + n8n keys in its env only
#   - ~/.config/opencode/opencode.json  OpenCode → LiteLLM router + Playwright/n8n MCP
#   - ~/work/.mcp.json             Claude Code's MCP servers (Playwright, n8n) for ~/work
#   - desktop icons for the RDP (XFCE) session, if a desktop is installed
# Existing configs you've edited are kept; the new version lands next to them as *.new.
# No secrets are written anywhere by this script.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
REFRESH=0; [ "${1:-}" = --refresh ] && REFRESH=1
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

# place SRC DEST — install a config, but never clobber one the user has changed.
place() {
  mkdir -p "$(dirname "$2")"
  if [ -f "$2" ] && ! cmp -s "$1" "$2"; then cp "$1" "$2.new"; say "kept your $2 (new version: $2.new)"
  else cp "$1" "$2"; fi
}

if [ "$REFRESH" = 0 ]; then
  say "apt packages"
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq whiptail fzf jq rsync git curl ca-certificates >/dev/null
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq adb >/dev/null 2>&1 \
    || sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq android-tools-adb >/dev/null 2>&1 || true

  if ! command -v node >/dev/null || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 20 ]; then
    say "Node.js 22 (NodeSource)"
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - >/dev/null
    sudo apt-get install -y -qq nodejs >/dev/null
  fi

  say "OpenCode + Claude Code (npm, global)"
  # opencode-ai is the real OpenCode package (the bare `opencode` name is something else).
  sudo npm install -g --silent opencode-ai @anthropic-ai/claude-code
fi

say "aurora menu + aurora-agent → /usr/local/bin"
sudo install -m 755 "$SRC/aurora" /usr/local/bin/aurora
sudo install -m 755 "$SRC/aurora-agent" /usr/local/bin/aurora-agent

say "agent configs"
place "$SRC/opencode.json" "$HOME/.config/opencode/opencode.json"
place "$SRC/claude-mcp.json" "$HOME/work/.mcp.json"

if command -v xfce4-terminal >/dev/null || [ -d "$HOME/Desktop" ]; then
  say "desktop icons (RDP session)"
  apps="$HOME/.local/share/applications"; mkdir -p "$apps" "$HOME/Desktop"
  term="xfce4-terminal --maximize -x"; command -v xfce4-terminal >/dev/null || term="x-terminal-emulator -e"
  icon() {  # icon FILE NAME EXEC ICON
    printf '[Desktop Entry]\nType=Application\nName=%s\nExec=%s\nIcon=%s\nTerminal=false\nCategories=Utility;\n' \
      "$2" "$3" "$4" > "$apps/$1.desktop"
    install -m 755 "$apps/$1.desktop" "$HOME/Desktop/$1.desktop"
  }
  icon aurora-control "Aurora Control" "$term aurora" utilities-terminal
  icon aurora-opencode "OpenCode" "$term aurora-agent opencode" accessories-text-editor
  icon aurora-claude "Claude Code" "$term aurora-agent claude" accessories-text-editor
  icon aurora-hermes-chat "Hermes chat" "$term docker exec -it hermes hermes" internet-chat
  icon aurora-n8n "n8n" "xdg-open http://127.0.0.1:5678" web-browser
  icon aurora-openbot "OpenBot" "xdg-open http://127.0.0.1:3020" web-browser
  icon aurora-hermes-web "Hermes dashboard" "xdg-open http://127.0.0.1:9119" web-browser
  icon aurora-router "Router (models)" "xdg-open http://127.0.0.1:4000/ui" web-browser
  icon aurora-kuma "Uptime" "xdg-open http://127.0.0.1:3001" web-browser
  # XFCE asks once before launching a new desktop file; mark ours trusted where gio can.
  for f in "$HOME"/Desktop/aurora-*.desktop; do gio set "$f" metadata::trusted true 2>/dev/null || true; done
fi

cat <<'EOF'

Done. Type `aurora` for the menu (or use the desktop icons in RDP).
First time only:
  aurora maintain tune    → swap, Docker log limits, nightly backups, lazydocker/btop
  aurora-agent claude     → /login (opens a link: finish it on your phone), then /plugin to browse
  aurora-agent opencode   → uses the router; /models to switch chains (free tiers: never client data)
EOF
