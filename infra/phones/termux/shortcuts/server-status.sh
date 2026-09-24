#!/data/data/com.termux/files/usr/bin/bash
# Termux:Widget button: what's running on the server + disk/RAM, then wait for Enter.
ssh -t aurora-01 'docker ps --format "table {{.Names}}\t{{.Status}}"; echo; free -h; df -h / | tail -1; echo; read -p "Enter to close"'
