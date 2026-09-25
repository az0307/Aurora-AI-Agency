#!/data/data/com.termux/files/usr/bin/bash
# Termux:Boot: a pinned notification with quick buttons (voice, ask, menu). Works over any app, like a floating remote
export PATH="$HOME/aurora/infra/phones/kit/bin:$PATH"
[ -n "${AURORA_BAR_NOW:-}" ] || sleep 20   # at boot, let the network and Tailscale come up
K="$HOME/aurora/infra/phones/kit/bin"
termux-notification --id aurora-bar --ongoing --priority low \
  --title "Aurora" --content "Voice command · Ask Hermes · Server status" \
  --button1 "🎤 Voice"  --button1-action "$K/aurora-needle --voice" \
  --button2 "💬 Ask"    --button2-action "bash $HOME/.shortcuts/tasks/ask-hermes-quiet.sh" \
  --button3 "📋 Status" --button3-action "bash $HOME/.shortcuts/tasks/box-status.sh"
