# Smart / progressive terminal cockpit

Goal: a terminal that autocorrects, suggests as you type, and has panes / widgets / buttons
— both on your laptop and on the VPS. Three tiers.

## A. Local emulator (your laptop → the VPS)

Pick one:

| Emulator | Best for | Notes |
|---|---|---|
| **Wave Terminal** ⭐ open-source | widgets + buttons + inline graphics | Block-based workspace, graphical widgets, AI chat, remote mode. The open-source pick that matches "buttons/widgets". |
| **Warp** (freemium) | best AI in a terminal | NL→command, command blocks, saved workflows, autosuggest that reads your dir/project. Most polished, but partly cloud. |
| **Ghostty** open-source | raw speed / native feel | No AI layer; pair with the shell sugar below for suggestions. |

Recommendation: **Wave** if the widget/button workspace is the point; **Warp** if you want
the strongest built-in AI; **Ghostty + shell sugar** if you want fast + fully local.

## B. Shell sugar (install on the VPS *and* laptop)

This is where "autocorrect + suggestive + smart" actually comes from. The
`cloud-init.yaml` installs these on every box; run the same on your laptop.

| Tool | Gives you | Install (Ubuntu/Debian) |
|---|---|---|
| **fish** (or zsh) | best out-of-box autosuggestions + syntax highlight | `apt install fish` — or zsh + plugins below |
| `zsh-autosuggestions` + `zsh-syntax-highlighting` | fish-style suggestions on zsh | clone into `~/.zsh/` and source in `.zshrc` |
| **Starship** | fast, informative prompt | `curl -sS https://starship.rs/install.sh \| sh` |
| **Atuin** | searchable, synced shell history with a TUI | `curl --proto '=https' --tlsv1.2 -LsSf https://setup.atuin.sh \| sh` (add `-s -- --non-interactive` for scripts; self-host the sync server too) |
| **zoxide** | smart `cd` that learns your paths | `apt install zoxide` |
| **thefuck** *(or `pay-respects`)* | **autocorrect** the previous command | `apt install thefuck` / cargo install pay-respects |
| **Zellij** | multiplexer with status bar, floating panes, plugins = "widgets/buttons" | download binary / `cargo install zellij` |
| `fzf`, `ripgrep`, `fd`, `bat`, `eza`, `tealdeer` | fuzzy find, fast grep/find, better cat/ls, tldr | `apt install fzf ripgrep fd-find bat eza tealdeer` |

Minimal `~/.bashrc`/`~/.zshrc` wiring (also written by cloud-init):

```sh
eval "$(starship init "$(basename "$SHELL")")"
eval "$(zoxide init "$(basename "$SHELL")")"
eval "$(atuin init "$(basename "$SHELL")")"
eval "$(thefuck --alias)"          # then: type `fuck` after a bad command
alias ls='eza' cat='bat' cd='z'
```

Fish equivalent uses `starship init fish | source`, etc. Fish gives autosuggestions and
syntax highlighting with **no plugins**, which is why it's the low-effort default on servers.

## C. Server-side browser terminal (headless, in-dashboard)

For driving a box from any browser without a native client:

- **ttyd** serving **Zellij** → a full multiplexed terminal as a web tile, embeddable in the
  Homepage dashboard.
- Reach it **only through Cloudflare Access** (never expose ttyd's port publicly).
- Wave Terminal's remote mode is an alternative if you standardize on Wave.

```sh
# ttyd is READ-ONLY by default — `-W` enables browser input. Bind to loopback and
# publish via Cloudflare Tunnel + Access only (never expose 7681 publicly).
ttyd -p 7681 -i 127.0.0.1 -W zellij
```

## How this ties into the AI agents

The agent CLIs in [`AGENTS.md`](./AGENTS.md) run *inside* this cockpit. Zellij's panes let
you watch an agent (e.g. Claude Code or OpenHands) in one pane while `atuin`/`fzf` drive
another, and ttyd makes the same session reachable from your phone through Access.
