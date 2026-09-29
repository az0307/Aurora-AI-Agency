# Hermes + OpenBot: start them, open them

The one paste-in block that brings everything up is in [MEGA.md](./MEGA.md).

This page covers how to start Hermes and OpenBot, the links to open each one, and the phone
commands. Each piece lives in the repo, so nothing here is a one-off.

## 0. What has to exist first

Neither agent can start until these are in Bitwarden. Ship them from the phone with
`./bootstrap.sh --ship-only`.

| Needed for | Key (Bitwarden → `secrets.env`) | Where to get it |
|---|---|---|
| Both (the brain) | `LITELLM_MASTER_KEY` (starts `sk-`) + one model key, e.g. `OPENROUTER_API_KEY` | You make the first one yourself. Get the model key at openrouter.ai → Keys. This is task **T004**. |
| Hermes | `TELEGRAM_BOT_TOKEN` + `TELEGRAM_ALLOWED_USERS` (your numeric id) | Telegram: @BotFather → `/newbot` for the token, @userinfobot for your id. This is task **T007**. |
| OpenBot | `INTELLIGENCE_API_KEY` (`cpk-…`) | `npx copilotkit@latest project select` |

You also need two things on the phone side:
- The **Tailscale app** on the phone, switched on.
- **MagicDNS + HTTPS Certificates** enabled at login.tailscale.com/admin/dns.

## 1. Start them (any one of these)

| From | Do |
|---|---|
| Phone menu | `a` → **🚀 Start Hermes + OpenBot** |
| Phone home screen | **start-ai** widget |
| Any Termux prompt | `ssh -t aurora-01 aurora ai` |
| On the server | `aurora ai` |

`aurora ai` runs three steps in order:
1. It starts the router, unless it's already healthy.
2. It starts Hermes and OpenBot, health-checking each.
3. It prints your links.

It is safe to run again. A missing key skips only that one stack, and it tells you which key is missing.

## 2. Open them

| What | Link | Phone button / command |
|---|---|---|
| **Hermes, chat** | `https://t.me/<your bot>`. The server looks the bot name up when Hermes starts. | `a` → ✈️, the **hermes-chat** widget, or `aurora tg` |
| **Hermes, dashboard** | `http://127.0.0.1:9119` (after the tunnel) | `a` → 📊, the **hermes-dashboard** widget, or `aurora hdash` |
| **Hermes, full terminal UI** | — | `a` → 🤖, or `ssh -t aurora-01 docker exec -it hermes hermes` |
| **OpenBot** (web chat) | `https://aurora-01.<tailnet>.ts.net:3020` | `a` → 🌐, the **openbot** widget, or `aurora openbot` |
| **Control panel** (both, plus n8n, models, logs) | `https://aurora-01.<tailnet>.ts.net:8600` | the **assistant** widget |
| **Every link** | — | `a` → 🔗, or `ssh -t aurora-01 aurora links` |

**Where the real links live.** Once each stack starts, the server records its real link in
`/opt/aurora/state/links`. That file is not secret. The phone buttons read it, so you never
type the tailnet name.

## 3. Termux commands, copy and paste

```sh
a                                   # the menu (everything below is in it)
aurora ai                           # start router → Hermes → OpenBot, then show links
aurora tg                           # open Hermes in Telegram
aurora openbot                      # open OpenBot in the browser
aurora hdash                        # tunnel + open the Hermes dashboard
aurora claude                       # Claude Code ON the server, driven from the Claude app → Code
pkill -f 9119:127.0.0.1:9119        # close the dashboard tunnel
aurora logs                         # follow Hermes' logs (Ctrl-C to stop)
aurora restart                      # reload Hermes' keys from secrets.env and restart it
ssh -t aurora-01 aurora links       # print every saved link
ssh -t aurora-01 bash /opt/aurora/check.sh   # full read-only health check
aurora widgets                      # (re)install the home-screen buttons, incl. the 4 new ones
```

After you pull this change on the phone:
- Run `aurora widgets` so the new buttons (start-ai, openbot, hermes-chat, hermes-dashboard)
  appear in Termux:Widget.
- On the server, run `aurora update`.

## 4. Things that were not considered before (and what's done about them)

1. **The Hermes dashboard link could never work over Tailscale.**
   - The problem: Hermes rejects any request whose Host header isn't the address it's bound to.
     That is its guard against DNS-rebinding. So `https://<box>:9119` failed with "Invalid Host header".
   - The fix: the dashboard stays loopback-only, since it also holds API keys. The phone reaches it
     through its own SSH tunnel.
   - The control panel and start-page tiles now say so.
2. **The control panel crashed as soon as Tailscale was on.**
   - The problem: its config put double-quoted values inside a double-quoted nginx string, so
     nginx refused to start (`[emerg] unexpected "a"`). This was reproduced with the real image.
   - The fix: the string is now single-quoted.
   - It also carries the Telegram link, so there's a **Chat with Hermes** tile, which hides itself
     until the bot exists.
3. **Tailnet links were skipped when Tailscale runs in Docker.**
   - The problem: `stacks/tailscale` runs Tailscale as a container (Tailscale's
     [standalone Docker setup](https://tailscale.com/docs/features/containers/docker/how-to/connect-docker-standalone)),
     but the scripts only looked for a host install. OpenBot, the control panel, the start page,
     Kuma and Dockge silently fell back to 127.0.0.1.
   - The fix: every `tailscale` call now uses the host CLI if there is one, else
     `docker exec tailscale tailscale …`. The container uses host networking, so its `serve`
     publishes the host's 127.0.0.1 ports, and the serve config survives restarts in its
     `./state` volume.
   - `aurora ai` now starts Tailscale first when it isn't running.
4. **OpenBot uses CopilotKit's cloud service** (`INTELLIGENCE_API_KEY`), so chats pass through a
   third party.
   - Don't paste client personal information into OpenBot.
   - For client work use Hermes on a paid model chain (`general`, `code`, …, never a `-free` one).
5. **OpenBot is in single-user mode.** Anyone on your tailnet who opens it *is you*. That's fine
   while the tailnet is just your devices. Switch it to OAuth before you share the tailnet.
6. **Hermes answers only the people in `TELEGRAM_ALLOWED_USERS`.** Leave
   `GATEWAY_ALLOW_ALL_USERS=false`. The bot can run commands and spend your credits.
7. **Memory: the box has 8 GB.** router + n8n + Hermes + OpenBot fit. Don't also run Ollama or the
   computer-use desktop at the same time, and `stacks-up.sh openbot` warns if they're up.
8. **The dashboard tunnel keeps running in the background.** That costs a little battery. Close it
   with `pkill -f 9119:127.0.0.1:9119`, or it ends when Termux is killed.
9. **Links can only be opened from your own devices.** Everything is tailnet-only: no Funnel, no
   public port, and Telegram connects outbound. A phone without Tailscale on can still use
   Telegram, but not the web links.
10. **Nothing here can start from a cloud session.** The server is reachable only from your
   tailnet, so the first `aurora ai` has to be run by you, from the phone.
