# Phones — manage everything from your S10 and Reno 11

## Order (about 1–1.5 hours per phone, the S10 and Reno can be done side by side)

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
| `termux/bashrc` | auto-attach tmux; `aurora`, `ah`, `aps`, `arestart-hermes` shortcuts |
| `termux/ssh_config` | `aurora-01` over Tailscale, keep-alives, connection reuse |
| `termux/shortcuts/*.sh` | Termux:Widget buttons: server tmux, Hermes logs, server status, restart Hermes |
| `server/tmux.conf` | same keys on the server + CPU/RAM/uptime, windows for logs and containers |

Both tmux configs were loaded in a real tmux with TPM: all plugins install, no startup
errors, theme renders.

## How it all connects

```
S10 / Reno 11 ── Tailscale ──► aurora-01 (Hetzner)
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
