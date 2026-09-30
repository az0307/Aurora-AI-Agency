#!/bin/bash
# Boot order matters: X server → session bus → accessibility bus → desktop → VNC → Cua daemon.
set -u
export DISPLAY=:1
W=${CUA_WIDTH:-1280}; H=${CUA_HEIGHT:-800}
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1
Xvfb :1 -screen 0 "${W}x${H}x24" -nolisten tcp &
for _ in $(seq 1 50); do xdpyinfo >/dev/null 2>&1 && break; sleep 0.2; done

# One session bus for everything, saved so `docker exec` (the MCP bridge) can join it.
eval "$(dbus-launch --sh-syntax)"
printf 'export DBUS_SESSION_BUS_ADDRESS=%q\nexport DISPLAY=:1\n' "$DBUS_SESSION_BUS_ADDRESS" > "$HOME/.desktop-env"
/usr/libexec/at-spi-bus-launcher --launch-immediately &
startxfce4 >/tmp/xfce.log 2>&1 &

# VNC only inside the container (localhost); websockify is the one published port (noVNC).
x11vnc -display :1 -forever -shared -nopw -localhost -rfbport 5900 -quiet >/tmp/x11vnc.log 2>&1 &
websockify --web /usr/share/novnc 6080 localhost:5900 >/tmp/novnc.log 2>&1 &

sleep 3
# Standard permission mode: the whole container is the boundary (no host mounts, no socket).
exec cua-driver serve
