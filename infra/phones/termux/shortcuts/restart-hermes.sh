#!/data/data/com.termux/files/usr/bin/bash
# Termux:Widget button: reload Hermes' keys from /opt/aurora/secrets.env and restart it (after
# adding/rotating a key and shipping it). A restart alone would keep the old key in data/.env.
ssh aurora-01 "bash /opt/aurora/stacks-up.sh hermes --env-only && cd /opt/aurora/stacks/hermes && docker compose restart gateway" && termux-toast "Hermes restarted with current keys"
