# Termux + tmux setup (same steps on both phones)

Do this after the phone-specific prep in [S10.md](./S10.md) or [RENO11.md](./RENO11.md)
(those cover the battery/background settings that stop Android killing Termux).

The config files live in [`termux/`](./termux/) and [`server/`](./server/), and were tested:
both tmux configs load with no errors, TPM installs every plugin, and the Catppuccin status
bar renders.

> **The fast way:** run the setup script for your phone. It does steps 1–7 below for you, with
> progress, colours and a health check at the end:
> `bash ~/aurora/infra/phones/setup/setup-reno11.sh` or `…/setup-s10.sh`
> (see [README.md](./README.md) for the three commands that come before it).
> The steps below are what the script does, if you'd rather do it by hand.

## 1. Install the apps (F-Droid)

Termux, Termux:API, Termux:Widget, Termux:Styling. Links in [APPS.md](./APPS.md).
Open **Termux:API** once so Android registers it. Then open **Termux**.

## 2. First run: packages

Copy-paste into Termux one block at a time:

```sh
termux-setup-storage            # tap Allow: gives Termux a ~/storage link to your files
pkg update && pkg upgrade -y
pkg install -y openssh mosh tmux git gh termux-api fzf nano curl python nodejs-lts android-tools
```

`android-tools` gives you `adb` on the phone itself (used once for the S10's background fix).

## 3. SSH key for this phone

```sh
ssh-keygen -t ed25519 -C "$(getprop ro.product.model)"   # press Enter through the prompts
cat ~/.ssh/id_ed25519.pub                                  # copy this line
```

**Getting the key onto the server, no laptop needed:**
- **The phone you create the server from (the Reno):** nothing to do. `bootstrap.sh` puts
  this phone's key on the server.
- **The other phone (the S10):** its setup script copies its public key to the clipboard.
  Send it to the Reno (Telegram "Saved Messages", LocalSend, or a Bitwarden note), copy it
  there, and on the Reno run **`aurora-addkey`**. It adds the key from the clipboard to the
  server.

**Each phone gets its own key.** If a phone is lost, delete just its line from
`~/.ssh/authorized_keys` on the server.

## 4. Get the configs onto the phone

The repo is private, so sign in to GitHub first:

```sh
gh auth login                    # GitHub.com → HTTPS → Login with a web browser → paste the code
gh repo clone az0307/Aurora-AI-Agency ~/aurora
cd ~/aurora/infra/phones/termux

cp tmux.conf ~/.tmux.conf
mkdir -p ~/.termux && cp termux.properties ~/.termux/termux.properties
cat bashrc >> ~/.bashrc
mkdir -p ~/.ssh && cp ssh_config ~/.ssh/config && chmod 600 ~/.ssh/config
mkdir -p ~/.shortcuts && cp shortcuts/*.sh ~/.shortcuts/ && chmod +x ~/.shortcuts/*.sh
termux-reload-settings
```

## 5. Font (so the tmux theme's icons show)

```sh
curl -fLo ~/.termux/font.ttf https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/patched-fonts/JetBrainsMono/Ligatures/JetBrainsMonoNerdFontMono-Regular.ttf
termux-reload-settings
```

(Or long-press the Termux screen → **More → Style** → pick a font/colour scheme with
Termux:Styling. The Nerd Font above is the one that has the icons.)

## 6. tmux plugins

```sh
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
tmux                                  # the theme shows once plugins are installed:
# press Ctrl-a then Shift-i (capital I). Wait for "TMUX environment reloaded".
```

Plugins installed: **tmux-sensible** (sane defaults), **Catppuccin v2.3.1** (theme),
**tmux-battery** (battery % in the bar, via Termux:API), **tmux-yank** (copy → Android
clipboard), **tmux-resurrect + tmux-continuum** (sessions saved every 15 min and restored
when you reopen), **tmux-fzf** (fuzzy menu of sessions/windows/commands).

From now on every new Termux tab drops straight into the `phone` tmux session (set in
`bashrc`; run `NO_TMUX=1 bash` if you ever want a plain shell).

## 7. Reach the server

With the **Tailscale** app connected:

```sh
ssh aurora-01          # plain SSH over Tailscale
aurora                 # mosh + the server's own tmux session "main" (survives network drops)
```

**Home-screen buttons:** long-press the home screen → Widgets → **Termux:Widget** → drag it
out. It lists the scripts from `~/.shortcuts`:

| Button | Does |
|---|---|
| `aurora-server` | opens the server's tmux session |
| `hermes-logs` | follows the Hermes bot's logs |
| `server-status` | containers, RAM, disk |
| `restart-hermes` | restarts the bot (after editing its settings) |

## 8. On the server (once, from either phone)

```sh
ssh aurora-01
sudo apt-get install -y mosh tmux git
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
cp /opt/aurora/phones/server/tmux.conf ~/.tmux.conf
tmux    # then Ctrl-a Shift-i to install plugins
```

(`bootstrap.sh` copies all of `infra/` to `/opt/aurora`. If that folder isn't there, copy
the file from the phone instead: `scp ~/aurora/infra/phones/server/tmux.conf aurora-01:.tmux.conf`.) mosh uses UDP 60000–61000. Over Tailscale that just works; nothing to open on the
Hetzner firewall.

## tmux cheat sheet (both phone and server)

`Ctrl-a` is the prefix: press it, let go, then the key.

| Keys | Action |
|---|---|
| `Ctrl-a c` | new window (tab) |
| `Ctrl-a 1..9` / `Alt-1..3` | go to window N |
| `Ctrl-a -` / `Ctrl-a \|` | split stacked / side by side |
| `Alt-←↑↓→` | move between panes (Alt + arrows on the extra-keys row) |
| `Ctrl-a z` | zoom current pane full-screen (again to un-zoom) |
| `Ctrl-a d` | detach (everything keeps running) |
| `Ctrl-a [` | scroll/copy mode (or just swipe up); `q` to leave |
| `Ctrl-a r` | reload config |
| `Ctrl-a Shift-i` / `Shift-u` | install / update plugins |
| `Ctrl-a Ctrl-s` / `Ctrl-a Ctrl-r` | save / restore sessions now |
| `Ctrl-a F` | fuzzy menu (tmux-fzf) |
| phone only: `Ctrl-a A` | new window connected to the server |
| server only: `Ctrl-a L` / `Ctrl-a D` | Hermes logs / live container list |

**tmux inside tmux** (phone tmux → server tmux): `Ctrl-a` goes to the phone's tmux. Press
**`Ctrl-a` twice** to send it to the server's tmux (e.g. `Ctrl-a Ctrl-a c` = new window on the
server). The extra-keys row has a **tmux** button that sends one `Ctrl-a`.
