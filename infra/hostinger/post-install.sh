#!/bin/bash
# Hostinger post-install script: the same hardened base as ../hetzner/cloud-init.yaml,
# as a bash script, because Hostinger VPS runs "post-install scripts", not cloud-init.
#
# Hostinger saves it as /post_install and runs it once, as root, right after the OS
# installs. Output goes to /post_install.log. bootstrap.sh uploads it with your SSH
# public key filled in. It also runs it over SSH when adopting a VPS you already have.
# Safe to run again: every step checks before it changes anything.
#
# Provisions: user `aurora` (sudo, docker, key-only SSH), no root or password logins,
# ufw, fail2ban, automatic security updates, Docker + compose, mosh/tmux and shell
# extras. It writes /var/lib/aurora/post-install.done when finished.
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive

PUBKEY='<YOUR_SSH_PUBLIC_KEY>'
U=aurora
MARK=/var/lib/aurora/post-install.done
log() { echo "[aurora $(date +%T)] $*"; }
retry() { local n=0; until "$@"; do n=$((n+1)); [ $n -ge 4 ] && return 1; sleep $((n*10)); done; }
have_systemd() { [ -d /run/systemd/system ]; }
svc() { have_systemd && systemctl "$@"; }

log "start ($(. /etc/os-release; echo "$PRETTY_NAME"))"

# --- 1. Packages ------------------------------------------------------------------------
retry apt-get update -q
apt-get -y -q -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold upgrade || log "upgrade had errors (continuing)"
retry apt-get install -y -q ca-certificates curl gnupg git sudo openssh-server ufw fail2ban \
  unattended-upgrades fish zsh fzf ripgrep fd-find bat eza tealdeer zoxide mosh tmux jq \
  || log "some packages failed (continuing)"

# --- 2. The aurora user (key-only) ----------------------------------------------------------
shell=/usr/bin/fish; [ -x "$shell" ] || shell=/bin/bash
if ! id "$U" >/dev/null 2>&1; then
  useradd -m -s "$shell" "$U"
  log "created user $U"
fi
usermod -aG sudo "$U"
passwd -l "$U" >/dev/null 2>&1 || true
echo "$U ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-aurora
chmod 440 /etc/sudoers.d/90-aurora
if command -v visudo >/dev/null && ! visudo -cf /etc/sudoers.d/90-aurora >/dev/null; then
  rm -f /etc/sudoers.d/90-aurora; log "sudoers file invalid, removed"
fi

install -d -m 700 -o "$U" -g "$U" "/home/$U/.ssh"
AK="/home/$U/.ssh/authorized_keys"
touch "$AK"
case "$PUBKEY" in
  ssh-*|ecdsa-*|sk-*) grep -qxF "$PUBKEY" "$AK" || echo "$PUBKEY" >> "$AK" ;;
  *) log "no key filled in: copying root's keys (the one Hostinger attached)"
     [ -s /root/.ssh/authorized_keys ] && cat /root/.ssh/authorized_keys >> "$AK" ;;
esac
sort -u "$AK" -o "$AK"; chmod 600 "$AK"; chown "$U:$U" "$AK"

# --- 3. Config files --------------------------------------------------------------------
install -d /etc/ssh/sshd_config.d /etc/fail2ban/jail.d
cat > /etc/fail2ban/jail.d/sshd.local <<'EOF'
[sshd]
enabled = true
maxretry = 3
bantime = 1h
findtime = 10m
EOF
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
install -d -o "$U" -g "$U" "/home/$U/.config" "/home/$U/.config/fish"
cat > "/home/$U/.config/fish/config.fish" <<'EOF'
# Prompt / navigation / history / autocorrect (installed below)
if type -q starship; starship init fish | source; end
if type -q zoxide;   zoxide init fish  | source; end
if type -q atuin;    atuin init fish   | source; end
alias cat='batcat'
alias ls='eza'
abbr -a cd z
if type -q thefuck; thefuck --alias fix | source; end
EOF
chown "$U:$U" "/home/$U/.config/fish/config.fish"

# --- 4. Docker Engine + compose plugin ------------------------------------------------------
if ! command -v docker >/dev/null; then
  log "installing Docker"
  retry sh -c 'curl -fsSL https://get.docker.com | sh' || log "Docker install failed (re-run this script)"
fi
getent group docker >/dev/null && usermod -aG docker "$U"
svc enable --now docker || true

# --- 5. Host firewall (Hostinger's own firewall sits in front of this) ----------------------
if command -v ufw >/dev/null; then
  ufw default deny incoming >/dev/null
  ufw default allow outgoing >/dev/null
  ufw allow 22/tcp >/dev/null
  ufw allow 41641/udp >/dev/null   # Tailscale direct connections (faster than relays)
  ufw --force enable >/dev/null 2>&1 || log "ufw not enabled (no kernel support here?)"
fi

# --- 6. Terminal extras not in apt (best effort) ---------------------------------------------
su - "$U" -c 'command -v starship >/dev/null || curl -sS https://starship.rs/install.sh | sh -s -- -y' >/dev/null 2>&1 || true
su - "$U" -c "command -v atuin >/dev/null || curl --proto '=https' --tlsv1.2 -LsSf https://setup.atuin.sh | sh -s -- --non-interactive" >/dev/null 2>&1 || true
command -v zellij >/dev/null || (curl -fsSL https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz | tar -xz -C /usr/local/bin) || true
apt-get install -y -q thefuck >/dev/null 2>&1 || true

# --- 7. Lock SSH down, but only once the aurora key is in place (never lock yourself out) --
if grep -qE '^(ssh-|ecdsa-|sk-)' "$AK"; then
  cat > /etc/ssh/sshd_config.d/10-hardening.conf <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
X11Forwarding no
MaxAuthTries 3
EOF
  install -d -m 755 /run/sshd   # sshd -t needs it; it only exists once sshd has run
  if /usr/sbin/sshd -t 2>/dev/null; then
    svc restart ssh || svc restart sshd || true
    log "SSH locked down: key-only, no root login"
  else
    rm -f /etc/ssh/sshd_config.d/10-hardening.conf
    log "sshd config test failed; hardening NOT applied"
  fi
else
  log "WARNING: no SSH key for $U, so root/password login was left as it was"
fi
svc enable --now fail2ban || true

install -d /var/lib/aurora
date -Is > "$MARK"
log "done"
