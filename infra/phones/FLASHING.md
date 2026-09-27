# Flashing the S10 without a laptop: what the VPS can and can't do

**Short version:** the VPS can *prepare* everything and control the S10 while Android or
recovery is running, but it **cannot flash in Download mode**. That part needs a USB cable
into another device, and the Reno can be that device.

## Why

| S10 state | How you talk to it | Can the VPS (aurora-01) do it over Tailscale? |
|---|---|---|
| Android running (rooted) | ADB over the network, or SSH into Termux | **Yes:** push files, install APKs, flash Magisk modules, `dd` an image as root, reboot to recovery |
| Recovery (TWRP) | ADB, usually USB only | Only if your recovery has network ADB (most don't): treat it as **no** |
| Download mode (Odin) | Samsung's Odin protocol, **USB only** | **No.** Nothing reaches a phone in Download mode over a network |

## What to use for each job

1. **Downloading, checking and storing files** (firmware, TWRP, Magisk, NetHunter zips): do it **on the VPS**.
   - It has fast internet and plenty of disk. Keep everything in `~/flash/`.
   - Check each download: `sha256sum file`, and compare against the checksum on the download page.
2. **Anything while Android is running** (most jobs): **VPS → S10 over the tailnet.**
   ```sh
   # once, on the S10 (root, in Termux):  su -c 'setprop service.adb.tcp.port 5555; stop adbd; start adbd'
   # then on aurora-01:
   adb connect 100.120.155.118:5555           # S10's tailnet IP; accept the prompt on the phone
   adb push ~/flash/Magisk.apk /sdcard/Download/
   adb install ~/flash/some.apk
   adb reboot recovery
   ```
   ADB gives full control of the phone, so only ever connect it over the tailnet, never over
   the public internet. Turn it off afterwards:
   `su -c 'setprop service.adb.tcp.port -1; stop adbd; start adbd'`.
3. **Download-mode flashing (firmware, the first TWRP):** **Reno → S10 with a USB-C cable (OTG)**.
   - The Reno acts as the "computer" and runs a USB flashing app or tool.
   - Get the files onto the Reno from the VPS first: `scp aurora-01:flash/<file> ~/storage/downloads/`.
   - I haven't tested a specific Odin-protocol app on the Reno, so check the app's reviews for your S10 model before trusting it with a bootloader.
4. **The S10 flashing itself** (rooted, no second device needed):
   - TWRP's *Install* button, or Magisk's *Install → Direct install*, flashes zips and images from the phone's own storage.
   - Only use `dd` onto partitions if you know exactly which partition it is. Getting it wrong can brick the phone.

## Safety rules
- Back up first. With TWRP, use *Backup* and copy the backup to the VPS: `adb pull` or `scp`.
- Keep the phone above 50% charge. Never unplug a cable mid-flash.
- Use firmware for the **exact model** (for example SM-G973F vs G973U), and check it with `sha256sum`.
- One change at a time: reboot and check it works before the next.
