# Kali on aurora-01, and "joining" it to Hermes

> ⚠️ **Authorized use only.** Run security tools only against systems you own or have written
> permission to test. This is for your own labs and engagements.

## Container, not a VM (on this host)

`aurora kali` (or `cd stacks/ondemand && docker compose --profile kali up -d`) starts the
**Kali rolling container** defined in `docker-compose.yml`. On a Hetzner **Cloud** CX box you
cannot run a real Kali *VM*: nested virtualization isn't available there. A true VM needs a
Hetzner **dedicated / bare-metal** server running Proxmox (or a local machine). So on aurora-01:

- **Container (here, now):** fast, disposable, shares the host kernel. Good for `nmap`, `nikto`,
  `sqlmap`, `ffuf`, web/recon tooling. Kernel-level and some wireless tools won't work.
- **Real VM (elsewhere):** a bare-metal + Proxmox box, joined to the same Tailscale tailnet.
  The same "join to Hermes" idea applies — Hermes reaches it over the tailnet.

The container ships bare (metapackages are multi-GB). Install what a job needs:
```sh
aurora kali
docker exec -it ondemand-kali-1 bash -lc 'apt update && apt install -y nmap'
# stop it when done:
cd /opt/aurora/stacks/ondemand && docker compose --profile kali down
```
It has no published ports, drops all capabilities except `NET_RAW`/`NET_ADMIN`, and never
auto-restarts — you bring it up deliberately.

## "Joined to Hermes"

Hermes drives the container through the **Docker MCP** (it can `exec` commands in it), the same
way you would by hand. That's the join: you ask Hermes in chat to run a tool in `ondemand-kali-1`,
and it runs there and reports back. Keep this behind your own approval — it is not wired to run
unattended, and it shouldn't be.

To set it up:
1. Enable the Docker MCP for Hermes (it's in `infra/mcp/.mcp.json.example`, marked **server-only**).
2. Start Kali with `aurora kali`.
3. In chat, scope every request to authorized targets and to the `ondemand-kali-1` container.

If you later stand up a real Kali VM on bare metal, put it on the tailnet and point Hermes at
it over SSH instead of `docker exec`; everything else is the same.
