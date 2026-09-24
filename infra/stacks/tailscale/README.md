# Tailscale — private access to everything on the box

Joins the box to your tailnet. After that you open the UIs from any of your devices over
Tailscale's encrypted network. No public ports, no Cloudflare needed for *your own* access.
(Anything the **public** must reach, such as a website form posting to an n8n webhook,
still needs a public path: Tailscale Funnel on that one path, or a Cloudflare Tunnel.)

## Start

1. Install Tailscale on your phone/laptop and sign in.
2. [Admin console](https://login.tailscale.com/admin/settings/keys) → **Generate auth key**
   (pre-approved) → put it in `.env` as `TS_AUTHKEY`.
3. `docker compose up -d`, then `docker exec tailscale tailscale status`: the box shows up
   as `aurora-01`.
4. In the admin console, enable **MagicDNS** and **HTTPS certificates** (DNS page) so the
   UIs get real `https://aurora-01.<tailnet>.ts.net` addresses.

## Publish the UIs to your tailnet (private, HTTPS)

Each line maps a tailnet HTTPS port to a loopback-only service. The mapping is saved in
`./state` and survives restarts.

```sh
ts() { docker exec tailscale tailscale "$@"; }
ts serve --bg --https=443  http://127.0.0.1:5678   # n8n            https://aurora-01.<tailnet>.ts.net
ts serve --bg --https=4000 http://127.0.0.1:4000   # LiteLLM router  (…:4000/ui)
ts serve --bg --https=9119 http://127.0.0.1:9119   # Hermes dashboard
ts serve --bg --https=3001 http://127.0.0.1:3001   # Uptime Kuma
ts serve status
```

Only devices on your tailnet can open these. `ts serve reset` removes them all.

## SSH over Tailscale, then close public SSH

The tailnet IP is on the host, so plain SSH works through it:

```sh
ssh aurora@aurora-01          # MagicDNS name, over the tailnet
```

Once that works **from a second terminal**, remove the SSH rule from the Hetzner cloud
firewall (`aurora-01-fw`). The box then has **zero** public inbound ports. If you lock
yourself out, the Hetzner web console still works.

Don't enable `--ssh` (Tailscale SSH) in this container: it would land you in the
container's shell, not the host's.

## Public webhooks (only if needed)

For the official WhatsApp Cloud API or a public n8n webhook, expose just that one path
publicly with Funnel, e.g. n8n webhooks only:

```sh
ts funnel --bg --https=8443 --set-path=/webhook http://127.0.0.1:5678/webhook
```

Funnel must be allowed in the tailnet policy. Everything else stays private.
