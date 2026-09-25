# Hostinger VPS

The agency box runs on a Hostinger KVM VPS. `../bootstrap.sh` drives Hostinger's official
API ([developers.hostinger.com](https://developers.hostinger.com), spec v1.54), so it all
works from the phone: no hPanel clicking except the token and a payment method.

| File | What |
|---|---|
| `provision.sh` | the Hostinger part of `bootstrap.sh`: find / set up / buy / adopt the VPS, firewall |
| `post-install.sh` | the base setup Hostinger runs once after installing Ubuntu (their version of cloud-init) |

## Plans and prices

From hostinger.com on 2026-09-25, in USD per month excluding GST. **The whole term is charged
up front.** The dry run reads the live prices from your account before anything is bought.

| Plan | vCPU | RAM | NVMe | 24-month term | Renews at | Fits the AUD $39 cap? |
|---|---|---|---|---|---|---|
| KVM 1 | 1 | 4 GB | 50 GB | $6.49 | $11.99 | yes, but 4 GB is too tight for this stack |
| **KVM 2** (default) | 2 | 8 GB | 100 GB | **$8.99** (≈AUD $380 up front) | $14.99 (≈AUD $26) | **yes** |
| KVM 4 | 4 | 16 GB | 200 GB | $12.99 (≈AUD $550 up front) | $28.99 (≈AUD $51) | first term yes, renewal **no** |
| KVM 8 | 8 | 32 GB | 400 GB | $25.99 | $49.99 | no |

AUD figures use a deliberately high 1.60 AUD/USD plus 10% GST, so real charges should come
in a little lower. KVM 4 is worth it if you want local models (Ollama) and the computer-use
desktop running at the same time. The script refuses it unless you add
`ALLOW_RENEWAL_OVER_CAP=1`, meaning you'll downgrade or cancel before it renews.

**Locations:** Hostinger VPS locations are France, Germany, Lithuania, the UK, India,
Indonesia, Malaysia, the USA and Brazil. There's **nothing in Australia or Singapore**, so the
script prefers Jakarta (`ID`), then Kuala Lumpur (`MY`), then Mumbai (`IN`). Change the order
with `HOSTINGER_DC_PREFER="MY ID"`.

## What `bootstrap.sh` does on Hostinger

1. **Finds your VPS.** In order:
   - **reuse**: a running VPS named `aurora-01`. Nothing is bought; the firewall is
     re-checked and the files are shipped again.
   - **setup**: a VPS you bought in hPanel that isn't installed yet. It installs Ubuntu 24.04
     with the post-install script and your SSH key. No charge.
   - **buy**: no VPS yet. Budget check, then you type **`buy`**, and it buys
     `HOSTINGER_PLAN` for `HOSTINGER_TERM` months with your default payment method.
   - **adopt**: `HOSTINGER_VM_ID=<id>` points at a VPS that's already running with some
     other setup. It attaches your key, runs the post-install script over SSH as root (it
     asks first, because that turns off root and password logins), then continues as normal.
2. **Budget check** (buy only). It shows the upfront charge, the monthly equivalent and the
   renewal price. It refuses if the monthly or renewal price is over `BUDGET_AUD`, and it
   refuses if there's no usable payment method.
3. **Post-install script**: uploaded to your account as `aurora-post-install`, with your
   phone's public key filled in. It creates the `aurora` user (key-only, passwordless sudo,
   docker group), turns off root and password SSH, and installs ufw, fail2ban, automatic
   security updates, Docker + Compose, mosh, tmux and the shell tools. It then writes
   `/var/lib/aurora/post-install.done`. The log is `/post_install.log` on the VPS.
4. **Firewall** `aurora-01-fw`: Hostinger's firewall drops all inbound traffic except the
   rules you add. The script adds **TCP 22** (SSH) and **UDP 41641** (Tailscale direct
   connections), activates it and syncs it. Docker-published ports can't get past it.
   After Tailscale works, delete the TCP 22 rule (SETUP.md §8).
5. Waits for the base setup, then **ships** `infra/` and your secrets to `/opt/aurora`.
   `HOSTINGER_API_TOKEN` is never shipped.

**Payment still processing?** If Hostinger answers "202 payment processing", the script
stops and leaves a note in `~/.aurora-hostinger-order-pending`. While that note exists it
**won't buy again**. When the VPS shows in hPanel, run `./bootstrap.sh` again and it sets
that VPS up. If the order failed, delete the note.

## Knobs (env or `secrets.env`)

| Variable | Default | |
|---|---|---|
| `HOSTINGER_API_TOKEN` | — | <https://hpanel.hostinger.com/profile/api> |
| `HOSTINGER_PLAN` | `KVM 2` | catalog plan name (quote it in `secrets.env`: `"KVM 2"`) |
| `HOSTINGER_TERM` | `24` | months to prepay: 1, 12, 24 (and 48 if your account offers it) |
| `HOSTINGER_DC_PREFER` | `ID MY IN` | country codes, first available wins |
| `HOSTINGER_DC_ID` / `HOSTINGER_TEMPLATE_ID` / `HOSTINGER_VM_ID` | auto | pin exact ids |
| `BUDGET_AUD` | `39` | monthly cap |
| `FX_TO_AUD` | USD 1.60 · EUR 1.75 · GBP 2.05 | AUD per 1 unit of the catalog currency |
| `TAX_RATE` | `0.10` | GST added to catalog prices |
| `ALLOW_RENEWAL_OVER_CAP` | `0` | `1` to allow a plan whose renewal is over the cap |

## How it was tested (2026-09-25)

- **API flow:** against a mock of the Hostinger API that checks every request against
  Hostinger's official OpenAPI spec (path, method, JSON body schema) and whose own
  responses are checked against the spec. All tested paths passed with **zero spec
  violations**: dry run, buy, reuse, setup, adopt, payment still processing (and the
  second-purchase block), a plan whose renewal is over the cap, no payment method, a bad
  token, a term that doesn't exist, and typing the wrong word.
- **`post-install.sh`:** run for real in a fresh Ubuntu 24.04 container, twice. Everything
  installed (Docker 29.8 + Compose, fish, mosh, tmux…), and the second run changed nothing.
  `sshd -T` showed root and password login off. If no key is filled in, it copies the key
  Hostinger attached to root. It doesn't lock SSH down unless a key is in place.
- **Not tested:** a real purchase (that needs your token and money) and Hostinger's own
  firewall behaviour.

## Managing it afterwards

- **hPanel** → <https://hpanel.hostinger.com/vps>: console, snapshots, weekly backups,
  recovery mode, firewall.
- **Hostinger MCP** (`hostinger-api-mcp` 1.63.3, 401 tools) lets Claude do the same from a
  laptop. It can buy and wipe VPSes, so keep it off the server itself. Config:
  [../mcp/.mcp.json.example](../mcp/.mcp.json.example).
- **Health:** `bash /opt/aurora/check.sh` on the box, or `a` → Check the server on the phone.
