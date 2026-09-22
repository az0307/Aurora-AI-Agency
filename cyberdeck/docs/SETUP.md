# Cyberdeck — S10 setup (on the real device)

Prereqs on the phone:
- **Termux** and **Termux:API** from **F-Droid** (not the Play Store build).
- ~8 GB free storage for the NetHunter rootfs + toolkit.
- (Rooted path only) Magisk installed and an unlocked bootloader.

## Order of operations
Copy this `cyberdeck/` folder to the phone (e.g. `git clone` in Termux, or
`scp` from your laptop), then from inside Termux:

```bash
cd cyberdeck
cp .env.example .env && nano .env       # add CYBERDECK_AUTHORIZED_KEY

bash scripts/00-termux-bootstrap.sh     # base Termux packages + workspace
bash scripts/10-nethunter-install.sh    # rootless Kali NetHunter chroot
nethunter                               # drop into the Kali chroot (alias: nh)
  bash scripts/20-pentest-toolkit.sh    # install the toolkit INSIDE Kali
  exit
bash scripts/30-ssh-cyberdeck.sh        # headless SSH access from your laptop
bash scripts/99-verify.sh               # PASS/FAIL sanity table
```

## Rootless vs rooted NetHunter
- **Rootless (default):** `10-nethunter-install.sh` runs Offensive Security's
  `install-nethunter-termux` — a Kali chroot inside Termux. No unlock, no root.
- **Rooted (full NetHunter):** flash the NetHunter kernel + app per
  <https://www.kali.org/docs/nethunter/> for HID/Wi-Fi-injection features. This
  repo stages only the chroot; follow the official kernel guide for your exact
  S10 model (Exynos vs Snapdragon differ).

## Develop scripts without the phone
See `../README.md` → **Emulating the S10**. Use `emulator/run-emulator.sh dry`
for the fast loop and `... docker --arm64` for an arch-accurate full run.
