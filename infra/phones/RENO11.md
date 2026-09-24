# OPPO Reno 11 — the daily driver / cockpit

**What it is:** 2024 phone, 8 or 12 GB RAM, arm64. The Reno 11 5G uses a MediaTek Dimensity
7050. It shipped with **ColorOS 14 (Android 14)**; check **Settings → About device** for the
exact model and whether it has updated to ColorOS 15 (Android 15). The steps are the same.

**Its job:** your main phone for managing everything: Termux + tmux into the server,
Telegram with Hermes, Bitwarden, GitHub, Claude, and Acode for quick config edits.

ColorOS menu names change a little between versions. If a path doesn't match, use the
Settings search (🔍) for the bold word.

## Step 1 — Update

**Settings → Software update → Download.** Newer ColorOS has fewer background-kill problems
and current security patches.

## Step 2 — Install the apps

From [APPS.md](./APPS.md), Reno 11 column ✅:
F-Droid → Obtainium → Termux, Termux:API, Termux:Widget, Termux:Styling → Tailscale →
Bitwarden → Aegis → ntfy → Telegram → Claude → GitHub → Material Files → Acode → LocalSend.
Optional: Termux:X11 (from GitHub via Obtainium) for a Linux desktop.

When ColorOS asks about installing from F-Droid ("Install unknown apps"), allow it **for
F-Droid and Obtainium only**.

## Step 3 — Stop ColorOS killing the background apps (important)

ColorOS closes background apps hard. For **Termux, Termux:API, Tailscale, ntfy and Telegram**:

1. **Settings → Apps → App management → [app] → Battery usage**
   - **Allow background activity: on**
   - **Allow foreground activity: on**
   - **Allow auto launch: on**
2. **Settings → Battery → More settings** → turn **off** "Optimise battery use" for those
   apps, or set them to **Don't optimise**, depending on the version.
3. Open **Recent apps**, long-press (or tap ⋮ on) the Termux card → **Lock**. The padlock
   keeps it from being cleared.
4. **Settings → Battery → Power saving mode: off** while you need Termux or alerts running.
   Power saving stops background apps.

## Step 4 — Android 14+ "phantom process killer" fix (important, and easy here)

Android kills background processes started by Termux (tmux, ssh, mosh); you'd see
`[Process completed (signal 9)]`. On Android 14 and later there's a **switch** for it:

1. **Settings → About device → Version** → tap **Build number** 7 times → Developer options
   on. ColorOS may ask for your PIN.
2. **Settings → Additional settings → Developer options** → turn on **Disable child process
   restrictions**.
3. **Leave Developer options ON.** Turning Developer options off turns this protection back
   on automatically.

(If the switch isn't there, use the ADB method from [S10.md](./S10.md) step 4 but with this
command instead:
`adb shell "settings put global settings_enable_monitor_phantom_procs false"`.)

## Step 5 — Tailscale, alerts, bot

1. **Tailscale** → sign in (same account) → turn on **Always-on VPN** when Android offers.
   Check that `aurora-01` appears.
2. **ntfy** → subscribe to the same topic as the S10. Keep it lower priority here if the S10
   is your "wake me up" phone.
3. **Telegram** → your Hermes bot. Try `/model search` and send a voice note.
4. **Bitwarden** → sign in, turn on **Settings → Autofill services → Bitwarden** so logins
   fill in the browser and apps.
5. **Aegis** → move your 2FA codes here (Hetzner, GitHub, Google, Tailscale, Cloudflare),
   and turn on encrypted **automatic backups**.

## Step 6 — Termux + tmux

Follow [TERMUX.md](./TERMUX.md) steps 2–7. Reno-specific notes:
- With 8–12 GB RAM you can keep several tmux windows open: one to the server (`aurora`),
  one local, and one for `gh` / git.
- **Landscape + split screen:** rotate the phone and `Ctrl-a |` gives two panes side by side
  (logs on one side, shell on the other).
- Put the **aurora-server** widget on your first home screen.

## Step 7 — Everyday management from this phone

| I want to… | Do this |
|---|---|
| ask the agent anything / give it a task | Telegram → Hermes (type or voice note) |
| see if everything's up | Tailscale on → Chrome → `https://aurora-01.<tailnet>.ts.net:3001` (Uptime Kuma) |
| edit an n8n workflow | Tailscale on → Chrome → `https://aurora-01.<tailnet>.ts.net` (n8n) |
| see model spend / router | Chrome → `https://aurora-01.<tailnet>.ts.net:4000/ui` |
| check containers / restart the bot | Termux:Widget → `server-status` / `restart-hermes` |
| read bot logs | Termux:Widget → `hermes-logs` |
| full shell on the server | Termux → `aurora` (mosh + tmux, survives switching Wi-Fi ↔ 5G) |
| review / merge a PR | GitHub app |
| code with Claude | Claude app, or Claude Code on the web |
| find a password or API key | Bitwarden |
| pay/billing, resize server | Chrome → <https://console.hetzner.com> (no official app) |

(Those `https://aurora-01…` addresses work after the `tailscale serve` lines in
[../stacks/tailscale/README.md](../stacks/tailscale/README.md).)

## Done checklist

- [ ] Termux, Tailscale, ntfy, Telegram: background activity + auto launch allowed, Termux locked in Recents
- [ ] Developer options → **Disable child process restrictions** on (and Developer options left on)
- [ ] `aurora` opens the server tmux, and survives turning Wi-Fi off and on
- [ ] Uptime Kuma and n8n open over Tailscale in Chrome
- [ ] Bitwarden autofill on; Aegis backups on
