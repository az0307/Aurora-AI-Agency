# Phone apps — what to install, from where, on which phone

Every link below was checked on 2026-09-24. **F-Droid** = <https://f-droid.org> (free,
open-source store). **Obtainium** installs and auto-updates apps straight from GitHub
releases. **Play** = Google Play, only where no good open-source build exists.

> ⚠️ **Termux and its add-ons must all come from the same place** (all F-Droid, or all
> GitHub). Never mix a Play Store Termux with F-Droid add-ons: the signatures differ and
> they won't talk to each other. The Play Store Termux is outdated; don't use it.

✅ = install on that phone · ➖ = optional there · ❌ = skip

## 1. Store / updater (install first)

| App | Get it | What for | S10 | Reno 11 |
|---|---|---|---|---|
| **F-Droid** | [f-droid.org](https://f-droid.org/packages/org.fdroid.fdroid/) (download the APK from the site) | the open-source app store | ✅ | ✅ |
| **Droid-ify** | [F-Droid](https://f-droid.org/packages/com.looker.droidify/) | faster, nicer F-Droid client (optional) | ➖ | ➖ |
| **Aurora Store** | [F-Droid](https://f-droid.org/packages/com.aurora.store/) | install Play Store apps (Telegram, Claude, GitHub…) without a Google account, or with one | ✅ | ✅ |
| **IzzyOnDroid repo** | one tap: `fdroidrepos://apt.izzysoft.de/fdroid/repo` (F-Droid asks to add it) | a big extra F-Droid repo of open-source apps | ✅ | ✅ |
| **Obtainium** | [F-Droid](https://f-droid.org/packages/dev.imranr.obtainium.fdroid/) · [GitHub](https://github.com/ImranR98/Obtainium) | install/update apps from GitHub releases | ✅ | ✅ |

## 2. Terminal (Termux family — all from F-Droid)

| App | Get it | What for | S10 | Reno 11 |
|---|---|---|---|---|
| **Termux** | [F-Droid](https://f-droid.org/packages/com.termux/) | Linux shell: ssh, mosh, tmux, git, Python, Node | ✅ | ✅ |
| **Termux:API** | [F-Droid](https://f-droid.org/packages/com.termux.api/) | lets scripts use battery, clipboard, notifications, torch… (also needed for the tmux battery module + copy to clipboard) | ✅ | ✅ |
| **Termux:Widget** | [F-Droid](https://f-droid.org/packages/com.termux.widget/) | home-screen buttons that run scripts (e.g. "connect to server") | ✅ | ✅ |
| **Termux:Styling** | [F-Droid](https://f-droid.org/packages/com.termux.styling/) | fonts (Nerd Font for the tmux theme icons) and colours | ✅ | ✅ |
| **Termux:Boot** | [F-Droid](https://f-droid.org/packages/com.termux.boot/) | runs `~/.termux/boot/` scripts at startup (the setup installs one: wake-lock + tmux ready) | ✅ | ✅ |
| **Termux:Float** | [F-Droid](https://f-droid.org/packages/com.termux.window/) | a floating terminal window over other apps | ✅ | ✅ |
| **Termux:GUI** | [F-Droid](https://f-droid.org/packages/com.termux.gui/) | lets scripts show real Android dialogs, buttons and lists | ➖ | ✅ |
| **Termux:Tasker** | [F-Droid](https://f-droid.org/packages/com.termux.tasker/) | run Termux scripts from Tasker / automation apps | ➖ | ➖ |
| **Termux:X11** | [GitHub](https://github.com/termux/termux-x11) via Obtainium | a Linux desktop on the phone (not on F-Droid) | ❌ | ➖ (Reno has the RAM) |
| **Termius** | [Play](https://play.google.com/store/apps/details?id=com.server.auditor.ssh.client) | polished SSH app with saved hosts + snippets; alternative to Termux for quick SSH | ➖ | ➖ |
| **ConnectBot** | [F-Droid](https://f-droid.org/packages/org.connectbot/) | lightweight open-source SSH client | ➖ | ➖ |

## 3. Network + security

| App | Get it | What for | S10 | Reno 11 |
|---|---|---|---|---|
| **Tailscale** | [F-Droid](https://f-droid.org/packages/com.tailscale.ipn/) · [Play](https://play.google.com/store/apps/details?id=com.tailscale.ipn) | private network to your server (n8n, router, dashboards, SSH) | ✅ | ✅ |
| **Bitwarden** | add repo `https://mobileapp.bitwarden.com/fdroid/repo` in F-Droid · [GitHub](https://github.com/bitwarden/android) via Obtainium · [Play](https://play.google.com/store/apps/details?id=com.x8bit.bitwarden) | passwords + API keys (not in main F-Droid) | ✅ | ✅ |
| **Aegis** | [F-Droid](https://f-droid.org/packages/com.beemdevelopment.aegis/) | 2FA codes (Hostinger, GitHub, Google, Cloudflare…), encrypted backups | ✅ | ✅ |
| **KeePassDX** | [F-Droid](https://f-droid.org/packages/com.kunzisoft.keepass.libre/) | offline password vault (only if you want one besides Bitwarden) | ❌ | ❌ |

## 4. Talk to your agents + get alerts

| App | Get it | What for | S10 | Reno 11 |
|---|---|---|---|---|
| **Telegram** | [Play](https://play.google.com/store/apps/details?id=org.telegram.messenger) · [telegram.org/android](https://telegram.org/android) (official APK) | chat with Hermes (typed + voice notes) | ✅ | ✅ |
| **ntfy** | [F-Droid](https://f-droid.org/packages/io.heckel.ntfy/) | push alerts from Uptime Kuma / n8n / the server | ✅ | ✅ |
| **Claude** | [Play](https://play.google.com/store/apps/details?id=com.anthropic.claude) | Claude + Claude Code on the web, on your phone | ✅ | ✅ |
| **GitHub** | [Play](https://play.google.com/store/apps/details?id=com.github.android) | review/merge PRs, read issues | ✅ | ✅ |
| **Thunderbird** | [F-Droid](https://f-droid.org/packages/net.thunderbird.android/) | email, if you want an open-source client | ➖ | ➖ |

## 5. Keyboard (predictive text + terminal keys)

| App | Get it | What for | S10 | Reno 11 |
|---|---|---|---|---|
| **HeliBoard** | [F-Droid](https://f-droid.org/packages/helium314.keyboard/) | open-source keyboard with **word prediction, autocorrect and gesture typing** (add a dictionary in its settings), no data sent anywhere | ✅ | ✅ |
| **Unexpected Keyboard** | [F-Droid](https://f-droid.org/packages/juloo.keyboard2/) | tiny keyboard **built for terminals**: Ctrl, Esc, Tab and arrows on swipes; switch to it inside Termux | ✅ | ✅ |
| **FlorisBoard** | [F-Droid](https://f-droid.org/packages/dev.patrickgold.florisboard/) | alternative modern keyboard with suggestions (pick this *or* HeliBoard) | ➖ | ➖ |

Tip: keep HeliBoard as your normal keyboard, and in Termux long-press the keyboard switcher
to swap to Unexpected Keyboard. In Termux, the shell's own predictions (grey text) do the
autocomplete; keyboard autocorrect there just gets in the way.

## 6. Files, editing, moving stuff between devices

| App | Get it | What for | S10 | Reno 11 |
|---|---|---|---|---|
| **Material Files** | [F-Droid](https://f-droid.org/packages/me.zhanghai.android.files/) | file manager that can open Termux's home folder | ✅ | ✅ |
| **Acode** | [F-Droid](https://f-droid.org/packages/com.foxdebug.acode/) | code editor (edit configs before pushing them) | ➖ | ✅ |
| **LocalSend** | [F-Droid](https://f-droid.org/packages/org.localsend.localsend_app/) | send files phone ↔ laptop ↔ phone over Wi-Fi | ✅ | ✅ |
| **Neo Backup** | [F-Droid](https://f-droid.org/packages/com.machiav3lli.backup/) | app backups (needs root; skip if not rooted) | ❌ | ❌ |
| **Open Camera** | [F-Droid](https://f-droid.org/packages/net.sourceforge.opencamera/) | camera with manual controls (optional) | ➖ | ➖ |

## Suggested roles for the two phones

- **Reno 11: daily driver / cockpit.** It has more RAM and a newer Android. Everything in
  sections 1–4, plus Acode and Termux:X11 if you want a desktop.
- **S10: always-on "ops phone".** Keep it on a charger with Tailscale, ntfy, Telegram and
  Termux. It's the phone that buzzes when something breaks, and your backup way into the
  server.

From a computer you can also mirror either phone's screen with
[scrcpy](https://github.com/Genymobile/scrcpy) (USB or Wi-Fi, no app needed on the phone).
