#!/bin/bash
#
# Debian 12 Headless Server Post-Install Hardening Script
# Run this as root after first login (or via sudo)
# Usage: sudo bash debian12-postinstall.sh
#
# WARNING: This script makes significant changes. Review before running.
# Test in a VM first!

set -euo pipefail

# ── Preflight checks ──────────────────────────────────────────────────────────
if [[ "$(id -u)" -ne 0 ]]; then
    echo "ERROR: Must be run as root (sudo bash $0)." >&2
    exit 1
fi
if ! grep -qi "bookworm\|debian 12" /etc/os-release 2>/dev/null; then
    echo "WARNING: This script targets Debian 12 (Bookworm). Detected OS may differ." >&2
fi

# ========================== CONFIGURATION ==========================
NEW_HOSTNAME="srv01"                    # Change to your desired hostname
ADMIN_USER=""                           # Leave empty to skip user creation (use existing)
TIMEZONE="Etc/UTC"                      # e.g. Australia/Melbourne, America/New_York
SSH_PORT=22                             # Change to e.g. 2222 for obscurity (also update ufw)
ENABLE_COCKPIT=false                    # Set to true to install Cockpit web UI
# ===================================================================

echo "=== Debian 12 Headless Server Post-Install Script ==="
echo "Starting at $(date)"
echo

# 1. Update sources.list
echo "[1/12] Updating APT sources.list..."
cat > /etc/apt/sources.list << 'EOF'
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware

deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware

deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
deb-src http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
EOF

# 2. Full upgrade
echo "[2/12] Running full system upgrade..."
apt update
apt full-upgrade -y
apt autoremove -y --purge
apt clean

# 3. Install essential packages
echo "[3/12] Installing essential packages..."
apt install -y \
    sudo vim nano htop curl wget git ca-certificates gnupg lsb-release \
    net-tools iputils-ping dnsutils systemd-timesyncd ufw fail2ban \
    unattended-upgrades apt-listchanges

# 4. Create admin user if specified and not exists
if [[ -n "$ADMIN_USER" ]]; then
    if id "$ADMIN_USER" &>/dev/null; then
        echo "[4/12] User $ADMIN_USER already exists. Adding to sudo group..."
        usermod -aG sudo "$ADMIN_USER"
    else
        echo "[4/12] Creating admin user: $ADMIN_USER"
        adduser --gecos "" --disabled-password "$ADMIN_USER"
        usermod -aG sudo "$ADMIN_USER"
        echo ">>> Set a password for $ADMIN_USER after setup: sudo passwd $ADMIN_USER"
    fi
else
    echo "[4/12] Skipping user creation (ADMIN_USER not set). Ensure your user is in sudo group."
fi

# 5. Set hostname
echo "[5/12] Setting hostname to $NEW_HOSTNAME..."
hostnamectl set-hostname "$NEW_HOSTNAME"
sed -i "s/127.0.1.1.*/127.0.1.1\t$NEW_HOSTNAME/" /etc/hosts || true

# 6. Timezone & NTP
echo "[6/12] Setting timezone to $TIMEZONE and enabling NTP..."
timedatectl set-timezone "$TIMEZONE"
timedatectl set-ntp true

# 7. Harden SSH
echo "[7/12] Hardening SSH configuration..."

# Pre-flight: ensure at least one authorized_keys exists before disabling password auth
if ! find /home -maxdepth 3 -name authorized_keys -size +0c 2>/dev/null | grep -q .; then
    echo "WARNING: No populated authorized_keys found under /home."
    echo "         Copy your SSH public key FIRST to avoid lockout:"
    echo "         ssh-copy-id -p $SSH_PORT youruser@$NEW_HOSTNAME"
    echo "Press ENTER to continue anyway (Ctrl-C to abort)..."
    read -r
fi

cp /etc/ssh/sshd_config "/etc/ssh/sshd_config.bak.$(date +%F_%T)" 2>/dev/null || true

cat > /etc/ssh/sshd_config << EOF
# Debian 12 Headless Hardened SSH Config (generated $(date))
Port $SSH_PORT
AddressFamily any
ListenAddress 0.0.0.0
ListenAddress ::

PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
UsePAM yes

MaxAuthTries 3
MaxSessions 5
LoginGraceTime 20
ClientAliveInterval 300
ClientAliveCountMax 2

# AllowUsers youruser     # Uncomment and set your admin user(s)

SyslogFacility AUTH
LogLevel VERBOSE

X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server
DebianBanner no
EOF

if ! sshd -t; then
    echo "[!] sshd_config syntax check FAILED — restoring backup" >&2
    BACKUP=$(ls -t /etc/ssh/sshd_config.bak.* 2>/dev/null | head -1)
    [[ -n "$BACKUP" ]] && cp "$BACKUP" /etc/ssh/sshd_config
    exit 1
fi
systemctl restart ssh
systemctl enable ssh

echo ">>> IMPORTANT: SSH is now key-only. Make sure you have copied your SSH public key!"
echo "    Example from your workstation: ssh-copy-id -p $SSH_PORT youruser@$NEW_HOSTNAME"

# 8. Configure UFW
echo "[8/12] Configuring UFW firewall..."
ufw --force reset || true
ufw default deny incoming
ufw default allow outgoing
ufw allow "$SSH_PORT"/tcp comment 'SSH access'
ufw --force enable
ufw reload

# 9. Unattended-upgrades
echo "[9/12] Configuring automatic security updates..."
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

dpkg-reconfigure -plow unattended-upgrades || true
systemctl enable --now unattended-upgrades

# 10. Fail2ban
echo "[10/12] Configuring Fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5
backend = systemd

[sshd]
enabled = true
port = $SSH_PORT
maxretry = 4
bantime = 24h
EOF

systemctl enable --now fail2ban

# 11. Optional Cockpit
if [[ "$ENABLE_COCKPIT" == "true" ]]; then
    echo "[11/12] Installing Cockpit web management UI..."
    apt install -y cockpit cockpit-bridge cockpit-system
    systemctl enable --now cockpit.socket
    ufw allow 9090/tcp comment 'Cockpit'
else
    echo "[11/12] Skipping Cockpit (ENABLE_COCKPIT=false)"
fi

# 12. Final cleanup & status
echo "[12/12] Final cleanup and status check..."
apt autoremove -y
apt clean

echo
echo "=== Post-install complete! ==="
echo
echo "Recommended next steps:"
echo "  1. From your workstation, test SSH key login:"
echo "     ssh -p $SSH_PORT yourusername@$NEW_HOSTNAME"
echo
echo "  2. Verify services:"
echo "     sudo systemctl status ssh ufw fail2ban unattended-upgrades"
echo "     sudo ufw status"
echo "     sudo fail2ban-client status"
echo
echo "  3. Reboot to apply all changes cleanly:"
echo "     sudo reboot"
echo
echo "Script finished at $(date)"