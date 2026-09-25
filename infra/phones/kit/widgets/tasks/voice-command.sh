#!/data/data/com.termux/files/usr/bin/bash
# Silent button: speak a command. Phone commands run on the phone (Needle); anything else goes to Hermes and the answer is spoken
export PATH="$HOME/aurora/infra/phones/kit/bin:$PATH"
aurora-needle --voice
