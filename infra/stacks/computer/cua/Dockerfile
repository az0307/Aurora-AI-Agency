# Cua desktop — a disposable Linux desktop (XFCE on Xvfb) that agents drive through Cua Driver's
# MCP server (https://github.com/trycua/cua, MIT). You watch/take over in noVNC. See ../docker-compose.yml.
FROM debian:12-slim

ARG CUA_VERSION=0.30.4
# sha256 of cua-driver-rs-${CUA_VERSION}-linux-x86_64-binary.tar.gz from the release's checksums.txt
ARG CUA_SHA256=fff2016e0dea320df9be3aa52fc942c4ea4ca651df32cf3e950119bbc3097d29

ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8
RUN apt-get update && apt-get install -y --no-install-recommends \
      xvfb xfce4 xfce4-terminal dbus-x11 at-spi2-core libxi6 x11-utils \
      x11vnc novnc websockify firefox-esr mousepad \
      ca-certificates curl procps fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -s /bin/bash agent

# Pinned release, checksum-verified; telemetry off before the binary ever runs.
RUN curl -fsSL -o /tmp/cua.tgz \
      "https://github.com/trycua/cua/releases/download/cua-driver-rs-v${CUA_VERSION}/cua-driver-rs-${CUA_VERSION}-linux-x86_64-binary.tar.gz" \
 && echo "${CUA_SHA256}  /tmp/cua.tgz" | sha256sum -c - \
 && mkdir -p /opt/cua-driver && tar xzf /tmp/cua.tgz -C /opt/cua-driver && rm /tmp/cua.tgz \
 && ln -s /opt/cua-driver/cua-driver /usr/local/bin/cua-driver \
 && install -d -o agent -g agent /home/agent/.cua-driver \
 && printf '{\n  "telemetry_enabled": false\n}\n' > /home/agent/.cua-driver/config.json \
 && chown agent:agent /home/agent/.cua-driver/config.json

COPY --chmod=755 start.sh /usr/local/bin/start-desktop
USER agent
WORKDIR /home/agent
ENV DISPLAY=:1 CUA_DRIVER_RS_TELEMETRY_ENABLED=false CUA_TELEMETRY_ENABLED=false
EXPOSE 6080
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=5 \
  CMD cua-driver status >/dev/null 2>&1 || exit 1
CMD ["start-desktop"]
