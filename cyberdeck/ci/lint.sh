#!/usr/bin/env bash
# lint.sh — shellcheck every shell script in the subsystem.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
if ! command -v shellcheck >/dev/null 2>&1; then
  echo "[!] shellcheck not installed. Install: apt-get install shellcheck" >&2
  exit 127
fi
mapfile -t files < <(find "$root" -name '*.sh' -not -path '*/node_modules/*')
# Include the extensionless mock-termux commands too.
mapfile -t mocks < <(find "$root/emulator/mock-termux" -type f)
echo "[*] Linting ${#files[@]} scripts + ${#mocks[@]} mock commands"
shellcheck -S warning "${files[@]}" "${mocks[@]}"
echo "[+] shellcheck clean"
