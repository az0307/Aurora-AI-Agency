#!/data/data/com.termux/files/usr/bin/bash
# Termux:Widget: bring the whole box up (staged; skips anything missing a key)
ssh -t "${AURORA_SERVER:-aurora-01}" "aurora up"; echo; read -rp "Enter to close" _
