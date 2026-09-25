#!/data/data/com.termux/files/usr/bin/bash
# Termux:Widget: type a question, Hermes answers here
export PATH="$HOME/aurora/infra/phones/kit/bin:$PATH"
aurora-ask; echo; read -rp "Enter to close" _
