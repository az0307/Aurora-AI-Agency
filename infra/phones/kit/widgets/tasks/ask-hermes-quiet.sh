#!/data/data/com.termux/files/usr/bin/bash
# Silent button: type a question, get the answer as a notification
export PATH="$HOME/aurora/infra/phones/kit/bin:$PATH"
q=$(termux-dialog text -t "Ask Hermes" | jq -r .text)
[ -n "$q" ] || exit 0
a=$(aurora-ask "$q" 2>&1 | head -c 3000)
termux-notification --title "Hermes" --content "$a"
