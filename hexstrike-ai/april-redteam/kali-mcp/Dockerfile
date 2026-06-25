# ─────────────────────────────────────────────────────────────
# Kali MCP — SSH+PTY+tmux Kali Linux container
# Based on kalilinux/kali-rolling for tool availability
# ─────────────────────────────────────────────────────────────

FROM kalilinux/kali-rolling:latest

LABEL maintainer="0x4m4"
LABEL description="Kali MCP Server — SSH+PTY bridge for AI pentesting"

ARG KALI_USER=kali
ARG KALI_PASSWORD=changeme
ENV KALI_USER=${KALI_USER}

# ── System update ─────────────────────────────────────────────
RUN apt-get update && apt-get upgrade -y

# ── Core tools ────────────────────────────────────────────────
RUN apt-get install -y --no-install-recommends \
    # SSH server
    openssh-server \
    # Terminal multiplexer
    tmux \
    # Python for MCP server
    python3 python3-pip python3-venv \
    # Core pentest tools
    nmap masscan \
    metasploit-framework \
    sqlmap \
    gobuster dirb \
    nikto \
    hydra \
    netcat-traditional \
    curl wget \
    git \
    # Network tools
    netdiscover arp-scan \
    whois dnsutils \
    tcpdump wireshark-common \
    # Web tools
    wfuzz \
    # Wordlists
    seclists wordlists \
    # Utils
    jq vim nano \
    file binutils \
    # Password tools
    hashcat john \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Optional: HexStrike AI tools ─────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    hexstrike-ai \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 2>/dev/null || true

# ── Python MCP dependencies ───────────────────────────────────
RUN pip3 install --break-system-packages \
    mcp \
    fastmcp \
    paramiko \
    asyncssh \
    requests \
    flask

# ── Create kali user ─────────────────────────────────────────
RUN useradd -m -s /bin/bash ${KALI_USER} \
    && echo "${KALI_USER}:${KALI_PASSWORD}" | chpasswd \
    && usermod -aG sudo ${KALI_USER}

# ── SSH configuration ─────────────────────────────────────────
RUN mkdir -p /var/run/sshd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && echo "AllowUsers ${KALI_USER}" >> /etc/ssh/sshd_config

# ── Workspace ────────────────────────────────────────────────
RUN mkdir -p /home/${KALI_USER}/workspace /opt/tools \
    && chown -R ${KALI_USER}:${KALI_USER} /home/${KALI_USER}/workspace

# ── Copy MCP server script ───────────────────────────────────
COPY mcp_server.py /home/${KALI_USER}/mcp_server.py
RUN chown ${KALI_USER}:${KALI_USER} /home/${KALI_USER}/mcp_server.py

# ── Tmux default config ───────────────────────────────────────
RUN echo 'set -g history-limit 50000\nset -g mouse on\nset -g default-terminal "screen-256color"' \
    > /home/${KALI_USER}/.tmux.conf \
    && chown ${KALI_USER}:${KALI_USER} /home/${KALI_USER}/.tmux.conf

# ── Entrypoint ────────────────────────────────────────────────
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22 8000

ENTRYPOINT ["/entrypoint.sh"]
