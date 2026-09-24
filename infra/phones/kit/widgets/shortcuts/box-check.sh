#!/data/data/com.termux/files/usr/bin/bash
# Termux:Widget: full server check (read-only)
export PATH="$HOME/aurora/infra/phones/kit/bin:$PATH"
ssh -t "${AURORA_SERVER:-aurora-01}" "bash /opt/aurora/check.sh"; echo; read -rp "Enter to close" _
