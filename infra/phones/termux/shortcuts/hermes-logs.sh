#!/data/data/com.termux/files/usr/bin/bash
# Termux:Widget button: follow the Hermes bot's logs (Ctrl-C to stop).
ssh -t aurora-01 "cd /opt/aurora/stacks/hermes && docker compose logs -f --tail 100 gateway"
