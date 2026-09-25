# Phones — manage everything from your S10 and Reno 11

> Diagram of how the phones fit into everything: [../docs/VISUAL-GUIDE.md](../docs/VISUAL-GUIDE.md).

## Quick start: no laptop needed

On each phone:

1. In the phone's browser, open <https://f-droid.org> → **Download F-Droid** → install it
   (allow "install unknown apps" for your browser just for this). In F-Droid, install **Termux**.
2. Open Termux and paste:
   ```sh
   pkg update -y && pkg install -y git gh
   gh auth login                      # GitHub.com → HTTPS → Login with a web browser
   gh repo clone az0307/Aurora-AI-Agency ~/aurora
   ```
3. Run your phone's script:
   ```sh
   bash ~/aurora/infra/phones/setup/setup-reno11.sh     # on the OPPO Reno 11
   bash ~/aurora/infra/phones/setup/setup-s10.sh        # on the Galaxy S10
   ```
   It walks you through everything in 12 steps, with a progress bar and colours:
   - opens each app's F-Droid page for you (Termux add-ons, Tailscale, stores, keyboards)
   - installs the packages, the smart shell, tmux + plugins, configs, widgets, boot script, font
   - creates this phone's SSH key and copies it to the clipboard
   - sets up Tailscale and walks you through the background-app and process-killer fixes
   - installs the **Aurora kit**: the `a` menu, Needle voice/phone commands, widgets and the pinned quick bar ([kit/README.md](./kit/README.md))
   - ends with a health check (✓/✗)

   Then type **`a`** for the menu. How to use everything: [../GUIDE.md](../GUIDE.md).

   If it stops (network, a step you skipped), **run the same command again**: finished steps
   are skipped. `doctor` re-runs just the health check anytime.
4. Close Termux fully and reopen it. You're in zsh inside tmux, with predictions (grey text,
   → to accept), red highlighting for typos, "did you mean" correction and Tab menus.

**Do the Reno first.** It's the phone you'll create the server from (`../SETUP.md`), and it's
where you run `aurora-addkey` to let the S10 in.

## Order by hand (if you'd rather not use the scripts)

1. **[APPS.md](./APPS.md)**: what to install on each phone, with F-Droid / GitHub / Play links.
2. **Phone prep** (background settings and the Android process-killer fix):
   - **[S10.md](./S10.md)**: Galaxy S10, Android 12, always-on "ops phone".
   - **[RENO11.md](./RENO11.md)**: OPPO Reno 11, Android 14+, daily driver / cockpit.
3. **[TERMUX.md](./TERMUX.md)**: Termux, SSH keys, tmux + plugins, home-screen buttons,
   server tmux, cheat sheet (same on both phones).

## What's in here

| Path | What |
|---|---|
| `termux/tmux.conf` | phone tmux: `Ctrl-a` prefix, touch/mouse, status bar on top, Catppuccin v2.3.1, battery, yank → Android clipboard, resurrect + continuum, tmux-fzf |
| `termux/termux.properties` | two extra-key rows (ESC/CTRL/ALT/TAB/arrows, one-tap tmux prefix, zoom, new window) |
| `setup/setup-reno11.sh`, `setup/setup-s10.sh` | one-command setup per phone (progress, colours, resumable, health check); shared logic in `setup/setup-phone.sh` + `setup/lib.sh` |
| `termux/zshrc` | smart shell: history + completion predictions, syntax colours, typo correction, fuzzy Tab menu, ↑/↓ history search, `z` jumps, `aurora-addkey`, `doctor` |
| `termux/boot/10-aurora.sh` | Termux:Boot: wake-lock + tmux session ready after a reboot |
| `termux/bashrc` | the same shortcuts for bash, if you don't use zsh |
| `termux/ssh_config` | `aurora-01` over Tailscale, keep-alives, connection reuse |
| `termux/shortcuts/*.sh` | Termux:Widget buttons: server tmux, Hermes logs, server status, restart Hermes |
| `server/tmux.conf` | same keys on the server + CPU/RAM/uptime, windows for logs and containers |

Both tmux configs were loaded in a real tmux with TPM: all plugins install, no startup
errors, theme renders.

## How it all connects

```
S10 / Reno 11 ── Tailscale ──► aurora-01 (Hetzner CX33)
   │                               ├─ ssh / mosh → tmux "main"
   │                               ├─ n8n, Uptime Kuma, router UI (tailscale serve, HTTPS)
   │                               └─ Hermes bot ◄── Telegram / WhatsApp / Discord / Slack
   ├─ Telegram ───────────────► Hermes (typed + voice notes)
   ├─ ntfy ◄────────────────── alerts from Uptime Kuma / n8n
   └─ Bitwarden, Aegis ─────── your passwords, API keys and 2FA codes
```

If a phone is lost: delete its line in `~/.ssh/authorized_keys` on the server, remove it in
the [Tailscale admin](https://login.tailscale.com/admin/machines), and end its Telegram
session (Telegram → Settings → Devices).
