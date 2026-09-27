#!/data/data/com.termux/files/usr/bin/bash
# Termux:Widget: open the Aurora Assistant control panel (Tailscale must be ON).
# Set AURORA_TS to your box's full tailnet name, e.g. aurora-01.tailXXXX.ts.net
[ -n "${AURORA_TS:-}" ] && [ -f "$HOME/.aurora_ts" ] && AURORA_TS=$(cat "$HOME/.aurora_ts")
: "${AURORA_TS:=$(cat "$HOME/.aurora_ts" 2>/dev/null)}"
if [ -n "$AURORA_TS" ]; then
  termux-open-url "https://$AURORA_TS:8600" 2>/dev/null || xdg-open "https://$AURORA_TS:8600"
else
  echo "Set your tailnet name first:  echo aurora-01.tailXXXX.ts.net > ~/.aurora_ts"
  echo; read -rp "Enter to close" _
fi
