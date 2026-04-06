#!/usr/bin/env bash
# HexStrike AI — Kali Linux Setup Script
# Run as: sudo bash setup-kali.sh
set -euo pipefail
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'
banner() { echo -e "\n${CYAN}${BOLD}▸ $1${NC}"; }
ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
err()  { echo -e "  ${RED}✗${NC} $1"; exit 1; }

echo -e "${CYAN}${BOLD}\n╔══════════════════════════════════════════╗\n║   HexStrike AI — Kali Setup Script       ║\n╚══════════════════════════════════════════╝\n${NC}"
[[ $EUID -ne 0 ]] && err "Run as root: sudo bash setup-kali.sh"

banner "System dependencies"
apt-get update -q
apt-get install -y -q nmap masscan nikto sqlmap hashcat metasploit-framework ttyd curl wget git build-essential python3 python3-pip 2>/dev/null || true
ok "System packages installed"

banner "Node.js 20"
if ! command -v node &>/dev/null || [[ "$(node -v)" != v20* ]]; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - -q
  apt-get install -y nodejs -q
fi
ok "Node $(node -v)"

banner "OpenCode"
command -v opencode &>/dev/null && ok "already installed" || (curl -fsSL https://opencode.ai/install | bash || warn "install manually")

banner "cloudflared"
command -v cloudflared &>/dev/null && ok "already installed" || (wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && dpkg -i cloudflared-linux-amd64.deb && rm cloudflared-linux-amd64.deb && ok "installed")

banner "HexStrike backend"
INSTALL_DIR="/opt/hexstrike"
mkdir -p "$INSTALL_DIR"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -d "$SCRIPT_DIR/../server" ]] && cp -r "$SCRIPT_DIR/../server/." "$INSTALL_DIR/" && ok "Server files copied" || warn "Copy server files to $INSTALL_DIR manually"
cd "$INSTALL_DIR"
[[ -f package.json ]] && npm install --silent && ok "Dependencies installed"
[[ -f .env ]] || cat > .env <<EOF
PORT=3001
KALI_SSH_HOST=localhost
KALI_SSH_PORT=22
KALI_SSH_USER=kali
KALI_SSH_PASS=
KALI_SSH_KEY=/home/kali/.ssh/id_rsa
HEXSTRIKE_MCP_URL=http://localhost:8889
FRONTEND_URL=*
ALLOWED_IPS=
EOF
warn "Edit $INSTALL_DIR/.env with your SSH credentials"

banner "Systemd services"
cat > /etc/systemd/system/hexstrike-api.service <<SVC
[Unit]
Description=HexStrike AI Backend
After=network.target
[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=/usr/bin/node --loader ts-node/esm/transpile-only index.ts
Restart=on-failure
[Install]
WantedBy=multi-user.target
SVC
cat > /etc/systemd/system/hexstrike-ttyd.service <<SVC
[Unit]
Description=HexStrike ttyd Shell
After=network.target
[Service]
ExecStart=/usr/bin/ttyd --port 7681 --base-path /shell --writable bash
Restart=on-failure
[Install]
WantedBy=multi-user.target
SVC
systemctl daemon-reload
systemctl enable --now hexstrike-ttyd
ok "Services created"

banner "SSH key"
KALI_HOME="/home/kali"
[[ -f "$KALI_HOME/.ssh/id_rsa" ]] && ok "exists" || (mkdir -p "$KALI_HOME/.ssh" && ssh-keygen -t rsa -b 4096 -f "$KALI_HOME/.ssh/id_rsa" -N "" -C "hexstrike" -q && cat "$KALI_HOME/.ssh/id_rsa.pub" >> "$KALI_HOME/.ssh/authorized_keys" && chmod 600 "$KALI_HOME/.ssh/authorized_keys" && chown -R kali:kali "$KALI_HOME/.ssh" && ok "generated")

MYIP=$(hostname -I | awk '{print $1}')
echo -e "\n${GREEN}${BOLD}DONE${NC}"
echo -e "  API:      http://$MYIP:3001"
echo -e "  Shell:    http://$MYIP:7681/shell"
echo -e "  Next:     edit $INSTALL_DIR/.env, then systemctl restart hexstrike-api"
echo -e "  Tunnel:   cloudflared tunnel --url http://localhost:3001"
