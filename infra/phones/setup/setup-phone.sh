#!/data/data/com.termux/files/usr/bin/bash
# setup-phone.sh — sets up Termux on your phone for the Aurora server, end to end.
# Don't run this directly; run setup-s10.sh or setup-reno11.sh (they set the phone profile).
#   bash setup-reno11.sh          # full setup (safe to re-run; finished steps are skipped)
#   bash setup-phone.sh doctor    # just check everything
#   FORCE=1 bash setup-s10.sh     # redo every step
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PHONES="$(cd "$HERE/.." && pwd)"
# shellcheck source=lib.sh
. "$HERE/lib.sh"

PHONE_ID="${PHONE_ID:-phone}"
PHONE_LABEL="${PHONE_LABEL:-Android phone}"
WITH_GUI="${WITH_GUI:-ask}"            # Termux:X11 + XFCE desktop: yes | no | ask
PHANTOM_FIX="${PHANTOM_FIX:-toggle}"   # adb (Android 12) | toggle (Android 14+)
SERVER="${SERVER:-aurora-01}"

FDROID=https://f-droid.org/packages
PKGS=(openssh mosh tmux git gh termux-api android-tools jq curl wget gawk tar
      zsh zsh-completions starship zoxide fzf eza bat ripgrep fd tealdeer
      python nodejs-lts nano neovim htop ncdu proot-distro termux-am)
ZSH_PLUGINS=(zsh-users/zsh-autosuggestions zsh-users/zsh-syntax-highlighting
             zsh-users/zsh-completions zsh-users/zsh-history-substring-search Aloxaf/fzf-tab)

# --------------------------------------------------------------------------------------
s_preflight() {
  [ -n "${PREFIX:-}" ] && [ -d "${PREFIX:-/nonexistent}" ] || { err "This must run inside Termux."; return 1; }
  local arch; arch=$(uname -m); info "CPU: $arch · Android $(getprop ro.build.version.release 2>/dev/null || echo ?) · $(getprop ro.product.model 2>/dev/null || echo phone)"
  [ "$arch" = aarch64 ] || warn "Expected aarch64; $arch may miss some packages."
  if [ -n "${TERMUX_VERSION:-}" ]; then ok "Termux $TERMUX_VERSION"; else warn "Can't read the Termux version; make sure it's from F-Droid/GitHub, not Play."; fi
  if [ ! -d "$HOME/storage" ]; then
    info "Asking for storage access (tap Allow)…"
    termux-setup-storage || true; sleep 2
  fi
  [ -d "$HOME/storage" ] && ok "storage access" || warn "no storage access yet (optional)"
}

s_apps() {
  info "Install these from F-Droid. Each link opens in your browser/F-Droid, then press Enter."
  local apps=(
    "Termux:API|$FDROID/com.termux.api/"
    "Termux:Boot (start on boot)|$FDROID/com.termux.boot/"
    "Termux:Widget (home-screen buttons)|$FDROID/com.termux.widget/"
    "Termux:Styling (fonts, colours)|$FDROID/com.termux.styling/"
    "Termux:Float (floating terminal)|$FDROID/com.termux.window/"
    "Termux:GUI (native Android UI from scripts)|$FDROID/com.termux.gui/"
    "Termux:Tasker (automation, optional)|$FDROID/com.termux.tasker/"
    "Tailscale|$FDROID/com.tailscale.ipn/"
    "ntfy (alerts)|$FDROID/io.heckel.ntfy/"
    "Aegis (2FA codes)|$FDROID/com.beemdevelopment.aegis/"
    "Obtainium (apps from GitHub)|$FDROID/dev.imranr.obtainium.fdroid/"
    "Aurora Store (Play apps without Google account)|$FDROID/com.aurora.store/"
    "HeliBoard (keyboard with prediction)|$FDROID/helium314.keyboard/"
    "Unexpected Keyboard (terminal keyboard)|$FDROID/juloo.keyboard2/"
    "LocalSend (send files between phones)|$FDROID/org.localsend.localsend_app/"
  )
  local a name url i=0
  for a in "${apps[@]}"; do
    i=$((i+1)); name=${a%%|*}; url=${a#*|}
    printf '  %s%2d/%d%s %s\n' "$C_BOLD" "$i" "${#apps[@]}" "$C_RESET" "$name"
    if ask "Open its page now?" y; then open_url "$url"; pause "Installed (or skipping)? Enter to continue"; fi
  done
  info "Extra F-Droid repos (one tap each; F-Droid asks to add them):"
  open_url "fdroidrepos://apt.izzysoft.de/fdroid/repo"; hint "↑ IzzyOnDroid: many more open-source apps"
  pause
  open_url "fdroidrepos://mobileapp.bitwarden.com/fdroid/repo"; hint "↑ Bitwarden's own repo → then install Bitwarden"
  pause
  info "Telegram (chat with Hermes): Aurora Store or https://telegram.org/android"
  info "Open Termux:API, Termux:Boot and Termux:Widget ONCE each so Android registers them."
  pause "Done opening them? Enter"
}

s_packages() {
  run "Updating package lists" retry 3 pkg update -y || return 1
  run "Upgrading installed packages" retry 3 env DEBIAN_FRONTEND=noninteractive pkg upgrade -y -o Dpkg::Options::=--force-confnew || return 1
  local p missing=()
  for p in "${PKGS[@]}"; do dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p"); done
  if [ ${#missing[@]} -eq 0 ]; then ok "all ${#PKGS[@]} packages already installed"; return 0; fi
  info "Installing ${#missing[@]} packages: ${missing[*]}"
  run "Installing packages" retry 3 pkg install -y "${missing[@]}"
}

s_gui() {
  local want=$WITH_GUI
  if [ "$want" = ask ]; then ask "Install the Linux desktop (Termux:X11 + XFCE, ~1.5 GB)?" n && want=yes || want=no; fi
  if [ "$want" != yes ]; then info "Skipped the desktop (run with WITH_GUI=yes FORCE=1 later)."; return 0; fi
  info "Termux:X11 isn't on F-Droid: install it from GitHub (Obtainium → add https://github.com/termux/termux-x11)"
  open_url "https://github.com/termux/termux-x11/releases"
  pause "Termux:X11 app installed? Enter"
  run "Adding the X11 package repo" retry 3 pkg install -y x11-repo || return 1
  run "Installing Termux:X11 + XFCE desktop" retry 3 pkg install -y termux-x11-nightly xfce4 || return 1
  mkdir -p "$HOME/.shortcuts"
  cat > "$HOME/.shortcuts/desktop.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# Termux:Widget button: start the XFCE desktop in the Termux:X11 app.
termux-x11 :1 -xstartup "dbus-launch --exit-with-session xfce4-session" &
sleep 2; am start -n com.termux.x11/com.termux.x11.MainActivity >/dev/null 2>&1
EOF
  chmod +x "$HOME/.shortcuts/desktop.sh"
  ok "desktop widget added: 'desktop'"
}

s_shell() {
  mkdir -p "$HOME/.zsh/plugins"
  local r name
  for r in "${ZSH_PLUGINS[@]}"; do
    name=${r#*/}
    if [ -d "$HOME/.zsh/plugins/$name/.git" ]; then
      run "Updating $name" git -C "$HOME/.zsh/plugins/$name" pull -q --ff-only || true
    else
      run "Getting $name" retry 3 git clone -q --depth 1 "https://github.com/$r" "$HOME/.zsh/plugins/$name" || return 1
    fi
  done
  mkdir -p "$HOME/.config"
  [ -f "$HOME/.config/starship.toml" ] || cat > "$HOME/.config/starship.toml" <<'EOF'
# Compact prompt for a narrow phone screen.
add_newline = false
format = "$directory$git_branch$git_status$cmd_duration$line_break$character"
[directory]
truncation_length = 2
[cmd_duration]
min_time = 3000
EOF
  if [ "$(basename "$(readlink -f "$HOME/.termux/shell" 2>/dev/null || echo "${SHELL:-}")")" != zsh ]; then
    run "Making zsh the default shell" chsh -s zsh || return 1
  fi
  ok "smart shell: suggestions, syntax colours, typo correction, fuzzy completion"
}

s_dotfiles() {
  local T="$PHONES/termux" f
  for f in "$HOME/.tmux.conf" "$HOME/.zshrc" "$HOME/.termux/termux.properties" "$HOME/.ssh/config"; do
    [ -f "$f" ] && [ ! -f "$f.before-aurora" ] && cp "$f" "$f.before-aurora" && hint "backed up $(basename "$f") → $(basename "$f").before-aurora"
  done
  mkdir -p "$HOME/.termux" "$HOME/.ssh" "$HOME/.shortcuts" "$HOME/.shortcuts/tasks" "$HOME/.termux/boot"
  cp "$T/tmux.conf" "$HOME/.tmux.conf"
  cp "$T/zshrc" "$HOME/.zshrc"
  cp "$T/termux.properties" "$HOME/.termux/termux.properties"
  cp "$T/ssh_config" "$HOME/.ssh/config" && chmod 600 "$HOME/.ssh/config"
  cp "$T"/shortcuts/*.sh "$HOME/.shortcuts/" && chmod +x "$HOME"/.shortcuts/*.sh
  cp "$T"/boot/*.sh "$HOME/.termux/boot/" && chmod +x "$HOME"/.termux/boot/*.sh
  ok "configs installed (tmux, zsh, Termux keys, ssh, widgets, boot)"
  if [ ! -s "$HOME/.termux/font.ttf" ]; then
    run "Downloading JetBrainsMono Nerd Font" retry 3 curl -fsSLo "$HOME/.termux/font.ttf" \
      https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/patched-fonts/JetBrainsMono/Ligatures/JetBrainsMonoNerdFontMono-Regular.ttf || return 1
  fi
  have termux-reload-settings && termux-reload-settings || true
}

s_tmux() {
  if [ ! -d "$HOME/.tmux/plugins/tpm" ]; then
    run "Getting tmux plugin manager" retry 3 git clone -q --depth 1 https://github.com/tmux-plugins/tpm "$HOME/.tmux/plugins/tpm" || return 1
  fi
  # Install plugins headlessly: a throwaway tmux server loads the config, TPM installs.
  run "Installing tmux plugins" bash -c '
    tmux -L aurora-setup -f "$HOME/.tmux.conf" new -d -s setup &&
    tmux -L aurora-setup run-shell "$HOME/.tmux/plugins/tpm/bin/install_plugins";
    rc=$?; tmux -L aurora-setup kill-server 2>/dev/null; exit $rc' || return 1
  ok "plugins: $(ls "$HOME/.tmux/plugins" | tr '\n' ' ')"
}

s_sshkey() {
  local key="$HOME/.ssh/id_ed25519"
  have ssh-keygen || { err "ssh-keygen missing: run the packages step (pkg install openssh)"; return 1; }
  mkdir -p "$HOME/.ssh" && chmod 700 "$HOME/.ssh"
  if [ ! -f "$key" ]; then
    run "Creating this phone's SSH key" ssh-keygen -q -t ed25519 -N "" -C "$PHONE_ID-$(getprop ro.product.model 2>/dev/null | tr ' ' _)" -f "$key" || return 1
  fi
  printf '\n  %sThis phone'"'"'s public key:%s\n  %s\n\n' "$C_BOLD" "$C_RESET" "$(cat "$key.pub")"
  have termux-clipboard-set && termux-clipboard-set < "$key.pub" && ok "copied to the clipboard"
  hint "It's used by bootstrap.sh (if you create the server from this phone), or"
  hint "paste it into your other phone and run: aurora-addkey"
}

s_tailscale() {
  info "Tailscale app: sign in, then turn on 'Always-on VPN' when Android offers."
  open_url "$FDROID/com.tailscale.ipn/"
  pause "Tailscale connected? Enter"
  if ping -c 1 -W 3 "$SERVER" >/dev/null 2>&1; then ok "$SERVER reachable over Tailscale"
  else warn "$SERVER not reachable yet (fine if the server isn't created yet; see ../../SETUP.md)"; fi
}

s_phantom() {
  if [ "$PHANTOM_FIX" = adb ]; then
    info "Android 12: turning off the process killer takes one ADB command, run from this phone."
    hint "1) Settings → About phone → Software information → tap Build number 7 times"
    hint "2) Settings → Developer options → Wireless debugging → ON (on Wi-Fi)"
    hint "3) Split screen: this Termux + Wireless debugging → 'Pair device with pairing code'"
    if [ -n "${ASSUME_YES:-}" ]; then warn "needs your input: run this step interactively"; return 1; fi
    local pip='' pport='' pcode='' cport=''
    prompt pip   "Pairing IP (e.g. 192.168.1.23):" '^[0-9]{1,3}(\.[0-9]{1,3}){3}$' || { err "no IP entered"; return 1; }
    prompt pport "Pairing port:" '^[0-9]{2,5}$'                                     || { err "no port entered"; return 1; }
    prompt pcode "6-digit code:" '^[0-9]{6}$'                                       || { err "no code entered"; return 1; }
    run "Pairing adb with this phone" adb pair "$pip:$pport" "$pcode" || return 1
    prompt cport "Port shown on the main Wireless debugging screen:" '^[0-9]{2,5}$' || { err "no port entered"; return 1; }
    run "Connecting adb" adb connect "$pip:$cport" || return 1
    run "Raising the phantom process limit" adb -s "$pip:$cport" shell \
      "/system/bin/device_config put activity_manager max_phantom_processes 2147483647" || return 1
    local v; v=$(adb -s "$pip:$cport" shell "/system/bin/device_config get activity_manager max_phantom_processes" 2>/dev/null | tr -d '\r')
    [ "$v" = 2147483647 ] && ok "max_phantom_processes = $v" || { err "value reads '$v'"; return 1; }
    hint "You can turn Wireless debugging off now. Repeat this step (FORCE=1) if sessions die again."
  else
    info "Android 14+: Settings → About device → Version → tap Build number 7 times,"
    info "then Settings → Additional settings → Developer options → 'Disable child process restrictions' ON."
    hint "Keep Developer options ON (turning them off re-enables the killer)."
    pause "Done? Enter"
  fi
}

s_background() {
  info "Stop Android putting Termux, Tailscale, ntfy and Telegram to sleep:"
  if [ "$PHONE_ID" = s10 ]; then
    hint "Settings → Battery and device care → Battery → Background usage limits"
    hint "  • 'Put unused apps to sleep' OFF  • Never sleeping apps: + Termux, Tailscale, ntfy, Telegram"
    hint "Settings → Apps → Termux → Battery → Unrestricted (same for Tailscale, ntfy)"
  else
    hint "Settings → Apps → App management → [app] → Battery usage:"
    hint "  Allow background activity ON · Allow auto launch ON (Termux, Tailscale, ntfy, Telegram)"
    hint "Recent apps → Termux card → Lock"
  fi
  have termux-wake-lock && termux-wake-lock && ok "Termux wake-lock on (notification: 'Release wakelock' to undo)"
  pause "Done? Enter"
}

s_kit() {
  # Menu (`a`), Needle voice/phone commands, widgets + quick bar. Bitwarden CLI is separate.
  bash "$PHONES/kit/bin/aurora-kit" install
}

doctor() {
  banner "Aurora phone check - $PHONE_LABEL"
  local pass=0 fail=0
  c() { if eval "$2" >/dev/null 2>&1; then ok "$1"; pass=$((pass+1)); else err "$1"; hint "$3"; fail=$((fail+1)); fi; }
  c "Termux:API responds"            "timeout 8 termux-battery-status"        "install Termux:API from F-Droid and open it once"
  c "zsh is the default shell"       "[ \"\$(basename \"\$(readlink -f ~/.termux/shell 2>/dev/null || echo \$SHELL)\")\" = zsh ]" "chsh -s zsh, then reopen Termux"
  c "zsh plugins present"            "[ -d ~/.zsh/plugins/zsh-autosuggestions ] && [ -d ~/.zsh/plugins/zsh-syntax-highlighting ]" "re-run the setup"
  c "tmux + plugins"                 "have tmux && [ -d ~/.tmux/plugins/tmux ]" "re-run: FORCE=1 … (tmux step)"
  c "Nerd Font"                      "[ -s ~/.termux/font.ttf ]"               "re-run the setup (dotfiles step)"
  c "SSH key"                        "[ -f ~/.ssh/id_ed25519 ]"                "ssh-keygen -t ed25519"
  c "Widgets in ~/.shortcuts"        "ls ~/.shortcuts/*.sh"                    "copy termux/shortcuts/*.sh"
  c "Boot script"                    "[ -x ~/.termux/boot/10-aurora.sh ]"      "copy termux/boot/10-aurora.sh"
  c "$SERVER reachable (Tailscale)"  "ping -c1 -W3 $SERVER"                    "Tailscale app connected? server created?"
  c "Aurora kit (menu, Needle)"     "command -v fzf && [ -x ~/.local/share/needle/needle ]" "bash ~/aurora/infra/phones/kit/bin/aurora-kit install"
  c "SSH login to $SERVER"           "ssh -o BatchMode=yes -o ConnectTimeout=6 $SERVER true" "add this phone's key on the server (aurora-addkey from another phone)"
  printf '\n  %s%d passed%s, %s%d need attention%s\n' "$C_GREEN" "$pass" "$C_RESET" "$C_YELLOW" "$fail" "$C_RESET"
}

main() {
  banner "Aurora phone setup - $PHONE_LABEL" "Resumable - log: ~/.aurora-setup/setup.log"
  STEP_TOTAL=12
  step preflight   "Check Termux"                         s_preflight
  step apps        "Apps: Termux add-ons, Tailscale, stores, keyboards" s_apps
  step packages    "Packages (ssh, mosh, tmux, zsh, tools)" s_packages
  step shell       "Smart shell (prediction, colours, correction)" s_shell
  step dotfiles    "Configs, widgets, boot script, font"  s_dotfiles
  step tmux        "tmux plugins"                         s_tmux
  step gui         "Linux desktop (optional)"             s_gui
  step sshkey      "SSH key for this phone"               s_sshkey
  step tailscale   "Tailscale (private network to the server)" s_tailscale
  step background  "Keep apps alive in the background"    s_background
  step phantom     "Android process-killer fix"           s_phantom
  step kit         "Aurora kit: menu, Needle, widgets, quick bar" s_kit
  summary
  doctor
  printf '\n%s  Close Termux completely and reopen it to start the new shell + tmux.%s\n' "$C_BOLD" "$C_RESET"
  hint "Then long-press the home screen → Widgets → Termux:Widget for the buttons."
  hint "Type  a  for the Aurora menu (everything: Hermes, voice, pictures, the server)."
  hint "Next: tailscale check anytime with 'doctor'; create/connect the server via ../../SETUP.md"
}

case "${1:-}" in
  doctor)    doctor ;;
  tailscale) s_tailscale ;;
  *)         main ;;
esac
