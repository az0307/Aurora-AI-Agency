# Aurora phone kit

The phone side of Aurora: one menu (`a`), voice and phone commands (Needle), pictures and
video, Bitwarden, and home-screen buttons. It's installed by the phone setup script
(step "kit"), or on its own:

```sh
bash ~/aurora/infra/phones/kit/bin/aurora-kit install   # menu, Needle, widgets, quick bar
aurora-kit bitwarden                                    # optional: Bitwarden CLI
aurora-kit doctor                                       # check it all
```

Reopen Termux, then type **`a`**.

![The menu and the model guide](../../docs/img/tui-menu.png)

## Commands

| Command | Does |
|---|---|
| `a` / `aurora` | the menu. `aurora check`, `aurora image`… run one item directly |
| `aurora-ask "…"` | ask Hermes; `-m code` picks a model, `-s` speaks the answer |
| `aurora-needle "torch on"` | phone command on the phone (Needle); anything else → Hermes. `--voice` listens first, `--dry-run` only shows |
| `aurora-gen image "…"` / `video "…"` | Hermes makes it on the server, and it's copied to Pictures/Aurora or Movies/Aurora |
| `aurora-models` | which model is best for what, with prices (Enter copies `/model …`) |
| `aurora-secrets check` / `fill` | Bitwarden folder "Aurora" → `infra/secrets.env` (mode 600) |
| `aurora-widgets install` / `new NAME 'CMD' [--task\|--boot]` / `list` / `remove` | home-screen buttons, silent buttons, boot scripts |
| `aurora-kit install` / `needle` / `bitwarden` / `doctor` | install and check |
| `server` | the server's tmux over mosh (was `aurora` before the kit) |

## Files

| Path | What |
|---|---|
| `bin/` | the commands above |
| `data/models.tsv` | the model guide's data (edit to add your own notes) |
| `data/needle-tools.json` | what Needle may do on the phone |
| `widgets/shortcuts/` | buttons that open a terminal → `~/.shortcuts/` |
| `widgets/tasks/` | silent buttons → `~/.shortcuts/tasks/` |
| `widgets/boot/` | runs at phone start → `~/.termux/boot/` (the pinned Voice / Ask / Status notification) |

## Tested (2026-09-24, in a Termux stand-in with a fake server)

- **Needle:** 15 requests on the real `needle3` model. Phone commands ran locally (torch,
  battery, volume, brightness, vibrate duration, clipboard, open URL, location, Wi-Fi,
  speak). Open questions went to Hermes.
- **Ask and generate:** questions reached Hermes as data (a malicious model name is
  refused). The image was copied back and opened.
- **Bitwarden:** fill wrote only the vault's keys, kept the template defaults, escaped
  values with spaces and `$`, set mode 600, and locked the vault again.
- **Widgets:** install, new, list, remove; bad names refused.
- **Menu:** real fzf in a 46-column terminal; the numbered fallback works without fzf.

Not tested here: the real Termux:API calls and Android speech-to-text (they need a
phone), and the real server.
