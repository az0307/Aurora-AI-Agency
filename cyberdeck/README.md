# cyberdeck — Samsung S10 mobile pentest rig

Provisions a **Samsung Galaxy S10** into a pocket security-testing workstation
(**Termux + Kali NetHunter**) using **idempotent one-shot scripts**, plus a
local **emulator** so those scripts can be written and tested without touching
the phone.

> Provisioning only. Use the result **only** against systems you own or are
> authorized to test — see [`docs/SAFETY.md`](docs/SAFETY.md).

## Layout

| Path | Role |
|------|------|
| `lib/common.sh` | Shared helpers: logging, `EMULATED` detection, `device_only` wrapper, authorization gate |
| `scripts/00-termux-bootstrap.sh` | Base Termux packages, storage, workspace |
| `scripts/10-nethunter-install.sh` | Rootless Kali NetHunter chroot (official installer) |
| `scripts/20-pentest-toolkit.sh` | Operator toolkit **inside** the Kali chroot |
| `scripts/30-ssh-cyberdeck.sh` | Headless SSH access (key-only) |
| `scripts/99-verify.sh` | PASS/FAIL post-install check |
| `emulator/` | Local S10 stand-in: Kali Docker target + mock Termux commands + runner |
| `ci/lint.sh` | `shellcheck` over every script |
| `docs/` | `SETUP.md` (on-device) and `SAFETY.md` (authorization/legal) |

## On the phone
See [`docs/SETUP.md`](docs/SETUP.md). Short version, inside Termux:

```bash
cp .env.example .env && nano .env
bash scripts/00-termux-bootstrap.sh
bash scripts/10-nethunter-install.sh
nethunter -- bash scripts/20-pentest-toolkit.sh
bash scripts/30-ssh-cyberdeck.sh
bash scripts/99-verify.sh
```

## Emulating the S10 (develop scripts without a phone)

The trick to "one-shot scripts that actually work" is testing them somewhere
before they hit the device. The emulator does that two ways:

```bash
# 1) fast inner loop — mock Termux commands on PATH, EMULATED=1, no Docker:
emulator/run-emulator.sh dry

# 2) arch-accurate full run — a Kali rootfs standing in for the NetHunter
#    chroot, optionally emulating the phone's arm64 via qemu:
emulator/run-emulator.sh docker           # host arch (fast)
emulator/run-emulator.sh docker --arm64   # emulate the S10's arm64

# lint everything:
emulator/run-emulator.sh lint
```

**How the emulation works.** On a real S10 the scripts call Termux-only
commands (`pkg`, `termux-setup-storage`, `tsu`, `proot-distro`) and device-only
steps (`sshd`, `termux-wake-lock`). The emulator supplies:
- `emulator/mock-termux/*` — shims that map `pkg`→`apt-get` and no-op the
  device-only commands, so scripts run to completion on plain Linux; and
- `EMULATED=1`, which makes `device_only ...` in `lib/common.sh` print-and-skip
  the steps that only make sense on hardware.

So the same script is exercised end-to-end in CI/emulator and runs for real on
the phone, unchanged.

## Config
Copy `.env.example` → `.env` (never commit `.env`). Notable vars:
`CYBERDECK_AUTHORIZED_KEY` (your laptop pubkey), `CYBERDECK_SSH_PORT`,
`TOOLKIT_EXTRA`, and `CYBERDECK_AUTHORIZED=yes` for non-interactive runs.
