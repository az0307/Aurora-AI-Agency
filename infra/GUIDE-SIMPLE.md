# The Aurora computer, explained simply

*(A guide anyone can follow, even a 10-year-old.)*

## What is it?

Somewhere in Germany there's a computer called **aurora-01**. It never turns off. It runs
helpers that work for us all day and night:

| Helper | What it does | Think of it as… |
|---|---|---|
| **Hermes** | Answers messages on Telegram and does jobs | a robot assistant |
| **n8n** | Does the same steps every time something happens (like when a customer fills in a form) | a conveyor belt in a factory |
| **The router** | Picks which AI brain to ask | a phone operator connecting calls |
| **OpenBot** | Another AI helper, in a web page | a second robot |
| **OpenCode / Claude Code** | AI helpers that write and fix code | robot programmers |
| **Uptime** | Checks everything is still working | a smoke alarm |

## The secret tunnel (Tailscale)

The computer is **locked to strangers**. Only our own phones can reach it, through a private
tunnel called **Tailscale**.

➡️ **Rule 1: Tailscale must be ON (the key icon) before anything else works.**

## How to get in

**From the phone, with a picture (desktop):**
1. Turn Tailscale on.
2. Open the **Windows App** (the Remote Desktop app).
3. Tap **aurora-01**, then log in as `aurora` with the password from Bitwarden.
4. You'll see a desktop with icons. Double-tap one:
   - **Aurora Control**: the menu (below)
   - **n8n**, **OpenBot**, **Hermes dashboard**, **Uptime**: open in the web browser

**From the phone, as a start page (easiest):**
1. Turn Tailscale on.
2. Open the bookmark **Aurora** (`https://aurora-01.<tailnet>.ts.net:3002`).
3. Tap any tile. A green dot means that helper is awake.

**From the phone, with typing (Termux):**
1. Turn Tailscale on.
2. Open Termux and type `ssh aurora-01`.
3. Type `aurora` and press Enter.

## The `aurora` menu

Move with the arrow keys and press Enter to choose.

| Pick | What happens |
|---|---|
| **status** | Shows which helpers are awake, and how much memory is left |
| **start / stop / restart** | Wake a helper up, put it to sleep, or turn it off and on again |
| **logs** | Shows what a helper is saying (press Ctrl + C to stop watching) |
| **check** | A full health check. Green ✓ is good, red ✗ needs fixing |
| **docker** | A picture of every helper box (press `q` to quit) |
| **opencode / claude** | Talk to a robot programmer |
| **hermes** | Chat with Hermes right in the window |
| **maintain → report** | A big report. Copy it and send it to Claude if something's wrong |
| **maintain → backup** | Saves a copy of everything now (it also does this by itself every night) |
| **update** | Gets the newest version of our tools from GitHub |

## Golden rules

1. 🔑 **Never** type a password or key into a chat (not with Claude, not with anyone). Keys go only into the hidden prompt or Bitwarden.
2. 🧯 If something breaks, do **check** first. Try **restart** on the broken helper. Still broken? Send the **report** to Claude.
3. 🧑‍🤝‍🧑 Customer information (like Y.M.I Roofing's customers) must **only** go to the paid AI brains, never the ones with "free" in their name.
4. 🚫 Don't turn on anything called **Funnel**. That would unlock the computer to the whole internet.
5. 💾 A copy of everything is saved every night at 3:30 am, and the last 7 days are kept.
6. 📱 To change the S10's software, read [phones/FLASHING.md](./phones/FLASHING.md) with a grown-up first. Mistakes can break the phone.

## If you're stuck

| Problem | Try this |
|---|---|
| Nothing loads | Is Tailscale on? Turn it off and on again. |
| One website says "error" | `aurora` → **restart** → pick that helper. |
| Hermes doesn't answer on Telegram | `aurora` → **logs** → `hermes` → look for red words. |
| "Out of memory" / everything slow | `aurora` → **status**, then **stop** something you're not using (OpenBot is the biggest). |
| You're not sure | `aurora` → **maintain → report**, then send it to Claude. |
