# Debian 12 (Bookworm) Headless Server Setup Guide

**Complete step-by-step guide for a minimal, secure, production-ready headless Debian 12 server (2026 edition)**

This guide covers:
- Minimal netinst installation (no desktop, optimized for remote/headless use)
- Post-install security hardening
- SSH key-only access
- Firewall (UFW)
- Automatic security updates
- Fail2ban
- Essential tools

**Target audience**: Sysadmins, homelab users, developers setting up VPS, bare-metal servers, or VMs (Proxmox, KVM, VirtualBox, etc.).

**Warnings**:
- Always test in a virtual machine first.
- Have console/IPMI/iLO/ physical access or a way to discover the IP for the first login.
- This is a base server setup. Adapt for specific workloads (web server, Docker host, NAS, etc.).

---

## 1. Preparation (on your workstation)

### Download Debian 12 Netinst ISO (Recommended for minimal installs)

1. Go to the official site: [https://www.debian.org/distrib/netinst](https://www.debian.org/distrib/netinst)
2. Download the latest **amd64 netinst** ISO (e.g., `debian-12.5.0-amd64-netinst.iso` or newer point release).
3. **Verify the download** (strongly recommended):

```bash
# On Linux/macOS
wget https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/SHA256SUMS
wget https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/SHA256SUMS.sign
# Import Debian release signing key and verify GPG signature
gpg --keyserver keyring.debian.org --recv-keys DF9B3C838BE5D8208DF766C7129A3F0C6F9AA905
gpg --verify SHA256SUMS.sign SHA256SUMS
# Verify ISO checksum
sha256sum -c SHA256SUMS 2>&1 | grep OK
```

### Create Bootable USB

**Linux**:
```bash
sudo dd if=debian-12.x.x-amd64-netinst.iso of=/dev/sdX bs=4M status=progress conv=fsync
# Replace /dev/sdX with your USB device (check with `lsblk`)
```

**Windows**: Use [Rufus](https://rufus.ie/) → Select ISO → DD Image mode → Write.

**macOS**: Similar to Linux `dd` (unmount first).

---

## 2. Base Installation (Headless Optimized)

Boot from the USB.

### Key Choices During Installer (Text Mode Recommended)

1. **Language / Location / Keyboard** — Choose appropriately.
2. **Hostname** — e.g., `srv01` or `debian-server`
3. **Domain name** — Leave blank or set your domain.
4. **Root password** — Set a strong one (you can disable root SSH later).
5. **User account** — **Create a normal user** (e.g., `admin` or your username). The installer will add it to the `sudo` group automatically in recent Debian versions.
6. **Partitioning**:
   - Guided – use entire disk (simple)
   - Or Guided with LVM
   - Advanced: Encrypted LUKS (great for security but requires passphrase on every reboot or keyfile setup)
7. **Software selection** (Critical for headless!):
   - **Deselect everything** except:
     - `[x] SSH server`
     - `[x] standard system utilities`
   - Do **NOT** select any desktop environment, print server, mail server, etc.
8. **Mirror** — Choose `deb.debian.org` or a fast local mirror.
9. **GRUB** — Install to MBR / EFI as appropriate.
10. Finish installation and reboot (remove USB when prompted).

After reboot, the system will boot to a text login prompt (headless by design).

---

## 3. First Login & Network Discovery

### Find the Server's IP Address

From another machine on the same LAN:

```bash
# Option 1: Check your router's DHCP client list (web UI)
# Option 2: Use nmap or arp-scan
sudo nmap -sn 192.168.1.0/24          # Adjust subnet
# or
sudo apt install arp-scan
sudo arp-scan --localnet
```

Or temporarily attach a monitor/keyboard.

### Login

```bash
ssh yourusername@SERVER_IP
# or console login as root or your user
```

Switch to root if needed:
```bash
su -
# or
sudo -i
```

---

## 4. Post-Installation Configuration & Hardening

Run these commands **as root** (or prefix with `sudo` if using your user).

### 4.1 Update Package Sources (Full Bookworm Repos)

```bash
cat > /etc/apt/sources.list << 'EOF'
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware

deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware

deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
deb-src http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
EOF
```

### 4.2 Full System Update

```bash
apt update
apt full-upgrade -y
apt autoremove -y
apt clean
```

### 4.3 Install Essential Packages

```bash
apt install -y \
    sudo \
    vim \
    nano \
    htop \
    curl \
    wget \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    net-tools \
    iputils-ping \
    dnsutils \
    systemd-timesyncd
```

### 4.4 Verify/Create Sudo User (if not already done)

```bash
# Check current user
whoami
id

# If needed, create user and add to sudo
adduser admin
usermod -aG sudo admin

# Test from the new user later:
# sudo -v
```

### 4.5 Configure Timezone & NTP (systemd-timesyncd is lightweight and sufficient)

```bash
timedatectl set-timezone Etc/UTC          # Change to your zone, e.g. Australia/Melbourne
timedatectl set-ntp true
timedatectl status
```

### 4.6 Harden SSH (Key Authentication + Disable Passwords/Root)

**On your local workstation** (generate key if you don't have one):

```bash
ssh-keygen -t ed25519 -C "your@email.com" -f ~/.ssh/id_ed25519_debian_server
```

**Copy the key to the server** (run on workstation):

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_debian_server.pub yourusername@SERVER_IP
```

**On the server**, harden the SSH configuration:

```bash
# Backup first
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%F)

# Create hardened config (edit as needed)
cat > /etc/ssh/sshd_config << 'EOF'
# Debian 12 Headless Server Hardened SSH Config
Port 22
AddressFamily any
ListenAddress 0.0.0.0
ListenAddress ::

# Authentication
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
UsePAM yes

# Security & Limits
MaxAuthTries 3
MaxSessions 5
LoginGraceTime 20
ClientAliveInterval 300
ClientAliveCountMax 2

# Allow only specific users (uncomment and adjust)
# AllowUsers admin deploy

# Logging
SyslogFacility AUTH
LogLevel VERBOSE

# Other good defaults
X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server

# Debian banner (optional)
DebianBanner no
EOF

# Validate config
sshd -t

# Restart SSH
systemctl restart ssh
systemctl enable ssh
```

**Test new SSH login from your workstation** (before closing current session!):

```bash
ssh -i ~/.ssh/id_ed25519_debian_server yourusername@SERVER_IP
```

If successful, you can close the old session.

### 4.7 Configure Firewall (UFW - Simple & Effective)

```bash
apt install -y ufw

ufw default deny incoming
ufw default allow outgoing
ufw allow ssh comment 'SSH access'
# Optional: Allow from specific IP only
# ufw allow from 203.0.113.50 to any port 22 proto tcp comment 'Admin IP'

ufw --force enable
ufw status verbose
```

### 4.8 Enable Automatic Security Updates (Unattended-Upgrades)

```bash
apt install -y unattended-upgrades apt-listchanges

dpkg-reconfigure -plow unattended-upgrades
# Choose "Yes" when asked to automatically download and install stable updates
```

Edit for more control (recommended):

```bash
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
};

Unattended-Upgrade::Package-Blacklist {
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::InstallOnShutdown "false";
Unattended-Upgrade::Mail "root";
Unattended-Upgrade::MailReport "on-change";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Remove-Unused-Dependencies "false";
Unattended-Upgrade::Automatic-Reboot "false";   # Set true + time if desired
Unattended-Upgrade::Automatic-Reboot-Time "02:00";
EOF
```

Enable the service:

```bash
systemctl enable --now unattended-upgrades
```

### 4.9 Install & Configure Fail2Ban (Brute-Force Protection)

Even with SSH keys, it's excellent for cleaning logs and protecting other services.

```bash
apt install -y fail2ban

# Create local jail config
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5
backend = systemd

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s
maxretry = 4
bantime = 24h
EOF

systemctl enable --now fail2ban
fail2ban-client status
fail2ban-client status sshd
```

### 4.10 Set Hostname (if not done perfectly during install)

```bash
hostnamectl set-hostname srv01.example.com
hostnamectl
```

Update `/etc/hosts` accordingly.

### 4.11 Optional but Recommended: Install Cockpit (Web-based Server Management)

If you want a nice web UI for monitoring/logs/storage/users (accessible via browser on port 9090):

```bash
apt install -y cockpit cockpit-bridge cockpit-system
systemctl enable --now cockpit.socket
ufw allow 9090/tcp comment 'Cockpit web UI'
```

Access: `https://SERVER_IP:9090` (login with your sudo user).

For pure CLI/headless purists, skip this.

### 4.12 Reboot and Final Verification

```bash
reboot
```

After reboot, verify from your workstation:

```bash
ssh yourusername@SERVER_IP
sudo systemctl status ssh ufw fail2ban unattended-upgrades
sudo ufw status
sudo fail2ban-client status
timedatectl
```

---

## 5. Next Steps & Recommendations

### Security Best Practices (Ongoing)

- Keep the system updated (`sudo apt update && sudo apt full-upgrade`).
- Regularly check `sudo unattended-upgrades --dry-run --debug` or logs in `/var/log/unattended-upgrades/`.
- Use `sudo journalctl -u ssh` and fail2ban logs.
- Consider `logwatch` or centralized logging (ELK, Loki, etc.) for production.
- For high-security: Enable AppArmor (usually already active), auditd, or use SELinux (more complex on Debian).
- Regularly audit open ports: `sudo ss -tuln` and `sudo ufw status`.
- Use Ansible, Terraform, or scripts for reproducible setups on multiple servers.

### Common Workload Additions

| Workload          | Packages / Notes                                      |
|-------------------|-------------------------------------------------------|
| Docker / Podman   | `docker.io` or official Docker repo + `docker-compose` |
| Web Server        | `nginx` or `apache2` + certbot (Let's Encrypt)       |
| Database          | `postgresql` or `mariadb-server`                     |
| Monitoring        | `prometheus-node-exporter`, Cockpit, Netdata         |
| File Sharing      | `samba`, `nfs-kernel-server`, or `nextcloud`         |
| Virtualization    | Proxmox (install on top) or KVM/libvirt              |

### Fully Automated / Preseeded Install (Advanced)

For true zero-touch headless installs (great for many servers or remote locations), use:

- Debian **preseed.cfg** (see official docs)
- Tools like [github.com/philpagel/debian-headless](https://github.com/philpagel/debian-headless) to remaster the ISO with preseed + SSH/serial console support from the very first boot.

---

## Summary of Key Security Features Implemented

- Minimal package selection during install
- SSH key authentication only + root login disabled
- UFW firewall (deny incoming by default)
- Automatic security updates via unattended-upgrades
- Fail2ban for brute-force mitigation
- Non-free firmware available if needed for hardware
- Time synchronization enabled
- Essential monitoring/troubleshooting tools installed

You now have a clean, secure, and maintainable Debian 12 headless server foundation.

**Happy sysadminning!**

---

*Guide synthesized from official Debian documentation, community best practices (OSTechNix, HowtoForge, Debian Wiki, hardening guides 2025-2026), and real-world production experience. Last updated: June 2026.*

*Test thoroughly. Adapt to your threat model and compliance requirements.*