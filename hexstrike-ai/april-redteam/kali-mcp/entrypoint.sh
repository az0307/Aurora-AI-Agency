#!/bin/bash
# ─────────────────────────────────────────────────────────────
# kali-mcp entrypoint.sh
# Starts SSH daemon + MCP server
# ─────────────────────────────────────────────────────────────

set -euo pipefail

KALI_USER="${KALI_USER:-kali}"
MCP_PORT="${MCP_PORT:-8000}"

echo "[*] Kali MCP Container starting..."
echo "[*] User: $KALI_USER | MCP Port: $MCP_PORT"

# ── Generate SSH host keys if missing ─────────────────────────
if [[ ! -f /etc/ssh/ssh_host_rsa_key ]]; then
    echo "[*] Generating SSH host keys..."
    ssh-keygen -A
fi

# ── Ensure kali user .ssh dir exists ─────────────────────────
mkdir -p /home/${KALI_USER}/.ssh
chmod 700 /home/${KALI_USER}/.ssh
chown ${KALI_USER}:${KALI_USER} /home/${KALI_USER}/.ssh

# ── Workspace perms ───────────────────────────────────────────
mkdir -p /home/${KALI_USER}/workspace /opt/tools
chown -R ${KALI_USER}:${KALI_USER} /home/${KALI_USER}/workspace

# ── Start SSH daemon in background ───────────────────────────
echo "[*] Starting SSH daemon on port 22..."
/usr/sbin/sshd -D &
SSH_PID=$!

# Wait for sshd to be ready
sleep 2
echo "[+] SSH daemon started (PID: $SSH_PID)"

# ── Start MCP server as kali user ────────────────────────────
echo "[*] Starting Kali MCP server on port $MCP_PORT..."
exec su -c "cd /home/${KALI_USER} && python3 mcp_server.py" ${KALI_USER}
