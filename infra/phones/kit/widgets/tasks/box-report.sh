#!/data/data/com.termux/files/usr/bin/bash
# Silent Termux:Widget: run the report, toast the headline
r=$(ssh "${AURORA_SERVER:-aurora-01}" "aurora maintain report" 2>&1 | tail -1)
command -v termux-toast >/dev/null && termux-toast "$r" || echo "$r"
