#!/data/data/com.termux/files/usr/bin/bash
# Silent button: server check as a notification
export PATH="$HOME/aurora/infra/phones/kit/bin:$PATH"
s=$(ssh -o ConnectTimeout=10 "${AURORA_SERVER:-aurora-01}" "bash /opt/aurora/check.sh" 2>&1 | sed "s/\x1b\[[0-9;]*m//g" | tail -1)
termux-notification --id aurora-status --title "Aurora server" --content "${s:-unreachable}"
