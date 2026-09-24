#!/data/data/com.termux/files/usr/bin/sh
# Termux:Boot — runs when the phone starts (needs the Termux:Boot app, opened once).
# Keeps Termux awake and has the "phone" tmux session ready, so widgets and SSH work
# right after a reboot.
termux-wake-lock
tmux has-session -t phone 2>/dev/null || tmux new -d -s phone
