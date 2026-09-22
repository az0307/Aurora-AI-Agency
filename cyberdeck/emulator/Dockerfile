# Emulated S10 target: a Kali rootfs that stands in for the NetHunter chroot,
# with the mock Termux commands on PATH so the on-device provisioning scripts
# run to completion without a phone.
#
# Build for the phone's real architecture (arm64) to catch arch-specific
# breakage, or leave default (host) for fast iteration:
#   docker build --platform=linux/arm64 -t cyberdeck-emu emulator/
FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive \
    EMULATED=1 \
    CYBERDECK_AUTHORIZED=yes \
    HOME=/root

# Minimal base so the scripts have something to build on; the scripts install
# the rest themselves (that is what we are testing).
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends bash ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# Put the mock Termux commands first on PATH.
COPY mock-termux/ /opt/mock-termux/
ENV PATH=/opt/mock-termux:$PATH

WORKDIR /cyberdeck
COPY . /cyberdeck/emulator/
# The repo's lib/ and scripts/ are mounted at runtime by run-emulator.sh.

CMD ["bash"]
