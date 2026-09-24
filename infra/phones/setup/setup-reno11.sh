#!/data/data/com.termux/files/usr/bin/bash
# OPPO Reno 11 (ColorOS 14/15, Android 14+) — the daily driver / cockpit.
#   bash ~/aurora/infra/phones/setup/setup-reno11.sh
export PHONE_ID=reno11
export PHONE_LABEL="OPPO Reno 11 - daily driver"
export PHANTOM_FIX=toggle     # Android 14+: Developer options → Disable child process restrictions
export WITH_GUI="${WITH_GUI:-ask}"  # enough RAM for the Linux desktop if you want it
exec bash "$(dirname "$0")/setup-phone.sh" "$@"
