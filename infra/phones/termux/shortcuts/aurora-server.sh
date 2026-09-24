#!/data/data/com.termux/files/usr/bin/bash
# Termux:Widget button: open the server's tmux session (mosh if available, else ssh).
mosh aurora-01 -- tmux new -A -s main || ssh -t aurora-01 tmux new -A -s main
