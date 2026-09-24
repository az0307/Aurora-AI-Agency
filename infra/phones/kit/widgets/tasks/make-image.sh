#!/data/data/com.termux/files/usr/bin/bash
# Silent button: describe a picture, it lands in your gallery
export PATH="$HOME/aurora/infra/phones/kit/bin:$PATH"
p=$(termux-dialog text -t "Describe the picture" | jq -r .text)
[ -n "$p" ] || exit 0
termux-toast "Making the image…"
if AURORA_NO_OPEN=1 aurora-gen image "$p" > "$HOME/.aurora-gen.log" 2>&1; then
  f=$(grep "^Saved:" "$HOME/.aurora-gen.log" | cut -d" " -f2-)
  termux-notification --title "Image ready" --content "$p" --image-path "$f" --action "termux-open \"$f\""
else termux-notification --title "Image failed" --content "$(tail -1 "$HOME/.aurora-gen.log")"; fi
