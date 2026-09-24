#!/data/data/com.termux/files/usr/bin/bash
# Galaxy S10 (Android 12, One UI 4.1) — the always-on "ops phone".
#   bash ~/aurora/infra/phones/setup/setup-s10.sh
export PHONE_ID=s10
export PHONE_LABEL="Galaxy S10 - ops phone"
export PHANTOM_FIX=adb        # Android 12 has no toggle: one ADB command, run from the phone
export WITH_GUI="${WITH_GUI:-no}"   # 8 GB, older chip: skip the desktop by default
exec bash "$(dirname "$0")/setup-phone.sh" "$@"
