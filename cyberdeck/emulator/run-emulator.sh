#!/usr/bin/env bash
# run-emulator.sh — develop and smoke-test the S10 provisioning scripts locally.
#
#   ./run-emulator.sh lint            # shellcheck every script (no Docker)
#   ./run-emulator.sh dry             # run scripts in-process with mocks, no Docker
#   ./run-emulator.sh docker          # full run inside the Kali emulator container
#   ./run-emulator.sh docker --arm64  # same, emulating the phone's arm64 arch
#
# 'dry' is the fast inner loop: it puts the mock Termux commands on PATH and
# runs each provisioning script with EMULATED=1, so device-only steps are
# skipped and pkg/proot-distro are shimmed. No phone, no root, no network for
# the device-only parts.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/.." && pwd)"
mode="${1:-dry}"; shift || true

case "$mode" in
  lint)
    exec "$root/ci/lint.sh"
    ;;
  dry)
    export EMULATED=1 CYBERDECK_AUTHORIZED=yes
    export PATH="$here/mock-termux:$PATH"
    export HOME="${CYBERDECK_EMU_HOME:-$(mktemp -d)}"
    echo "[*] Emulated HOME=$HOME  PATH prefixed with mock-termux"
    for s in 00-termux-bootstrap 10-nethunter-install 30-ssh-cyberdeck 99-verify; do
      echo; echo "===== scripts/$s.sh ====="
      # In 'dry' mode the mock pkg still calls apt; if apt is absent (plain
      # host) the script's own error handling reports it. Use PROVISION_DRYRUN
      # to stop before any package manager call.
      bash "$root/scripts/$s.sh" || echo "[!] $s.sh exited non-zero (inspect above)"
    done
    ;;
  docker)
    plat=""
    [ "${1:-}" = "--arm64" ] && plat="--platform=linux/arm64"
    echo "[*] Building emulator image $plat"
    docker build $plat -t cyberdeck-emu "$here"
    echo "[*] Running full provisioning flow inside the emulator"
    docker run --rm $plat -e EMULATED=1 -e CYBERDECK_AUTHORIZED=yes \
      -v "$root:/cyberdeck:ro" -w /cyberdeck cyberdeck-emu \
      bash -lc 'PATH=/opt/mock-termux:$PATH scripts/00-termux-bootstrap.sh && \
                PATH=/opt/mock-termux:$PATH scripts/10-nethunter-install.sh && \
                scripts/20-pentest-toolkit.sh && \
                PATH=/opt/mock-termux:$PATH scripts/99-verify.sh'
    ;;
  *)
    echo "usage: $0 {lint|dry|docker [--arm64]}" >&2; exit 2 ;;
esac
