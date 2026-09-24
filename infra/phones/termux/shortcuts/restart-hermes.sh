#!/data/data/com.termux/files/usr/bin/bash
# Termux:Widget button: restart the Hermes bot (e.g. after editing its data/.env).
ssh aurora-01 "cd /opt/aurora/stacks/hermes && docker compose restart gateway" && termux-toast "Hermes restarted"
