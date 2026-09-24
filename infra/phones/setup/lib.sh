#!/data/data/com.termux/files/usr/bin/bash
# lib.sh — shared helpers for the phone setup scripts: colours, progress bar, resumable
# steps, retries, logging, prompts. Sourced by setup-phone.sh; not run directly.

# --- Colours (auto-off when not a terminal or NO_COLOR is set) ----------------------------
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_RESET=$'\e[0m'; C_BOLD=$'\e[1m'; C_DIM=$'\e[2m'
  C_RED=$'\e[31m'; C_GREEN=$'\e[32m'; C_YELLOW=$'\e[33m'; C_BLUE=$'\e[34m'
  C_MAGENTA=$'\e[35m'; C_CYAN=$'\e[36m'
else
  C_RESET=; C_BOLD=; C_DIM=; C_RED=; C_GREEN=; C_YELLOW=; C_BLUE=; C_MAGENTA=; C_CYAN=
fi

SETUP_HOME="${SETUP_HOME:-$HOME/.aurora-setup}"
SETUP_LOG="$SETUP_HOME/setup.log"
SETUP_STATE="$SETUP_HOME/done"
mkdir -p "$SETUP_HOME"; touch "$SETUP_STATE" "$SETUP_LOG"

STEP_TOTAL=0
STEP_NUM=0
FAILED_STEPS=()

log()  { printf '%s %s\n' "$(date '+%F %T')" "$*" >> "$SETUP_LOG"; }
info() { printf '  %s•%s %s\n' "$C_BLUE" "$C_RESET" "$*"; log "INFO $*"; }
ok()   { printf '  %s✓%s %s\n' "$C_GREEN" "$C_RESET" "$*"; log "OK   $*"; }
warn() { printf '  %s!%s %s\n' "$C_YELLOW" "$C_RESET" "$*"; log "WARN $*"; }
err()  { printf '  %s✗%s %s\n' "$C_RED" "$C_RESET" "$*"; log "ERR  $*"; }
hint() { printf '    %s%s%s\n' "$C_DIM" "$*" "$C_RESET"; }

banner() {
  printf '\n%s%s' "$C_MAGENTA" "$C_BOLD"
  printf '╭──────────────────────────────────────────────╮\n'
  printf '│  %-44s│\n' "$1"
  [ -n "${2:-}" ] && printf '│  %s%-44s%s%s%s│\n' "$C_RESET$C_DIM" "$2" "$C_RESET" "$C_MAGENTA" "$C_BOLD"
  printf '╰──────────────────────────────────────────────╯%s\n' "$C_RESET"
}

# Progress bar sized for a phone screen (~40 columns wide).
progress() {
  local n=$1 total=$2 width=20 filled pct
  [ "$total" -gt 0 ] || total=1
  filled=$(( n * width / total )); pct=$(( n * 100 / total ))
  printf '%s[' "$C_CYAN"
  printf '%*s' "$filled" '' | tr ' ' '█'
  printf '%*s' "$(( width - filled ))" '' | tr ' ' '░'
  printf ']%s %3d%%  %s(%d/%d)%s\n' "$C_RESET" "$pct" "$C_DIM" "$n" "$total" "$C_RESET"
}

# step <id> "<title>" <function>  — runs once; re-running the script skips finished steps.
step() {
  local id=$1 title=$2 fn=$3
  STEP_NUM=$(( STEP_NUM + 1 ))
  printf '\n%s%s▶ %s%s\n' "$C_BOLD" "$C_CYAN" "$title" "$C_RESET"
  progress "$(( STEP_NUM - 1 ))" "$STEP_TOTAL"
  if grep -qx "$id" "$SETUP_STATE" && [ -z "${FORCE:-}" ]; then
    ok "already done (FORCE=1 to redo)"
    return 0
  fi
  log "STEP $id: $title"
  if "$fn"; then
    echo "$id" >> "$SETUP_STATE"
    ok "done"
  else
    err "step failed: $title  (details: $SETUP_LOG)"
    FAILED_STEPS+=("$title")
  fi
}

# retry <n> <cmd...> — for flaky mobile networks.
retry() {
  local n=$1; shift
  local i=1
  until "$@" >> "$SETUP_LOG" 2>&1; do
    [ "$i" -ge "$n" ] && return 1
    warn "attempt $i failed, retrying in $(( i * 3 ))s…"
    sleep $(( i * 3 )); i=$(( i + 1 ))
  done
}

# Run a command, show a spinner while it works, keep output in the log.
run() {
  local label=$1; shift
  if [ ! -t 1 ]; then  # no terminal (piped/logged): no spinner
    if ( "$@" >> "$SETUP_LOG" 2>&1 ); then ok "$label"; return 0; else err "$label"; return 1; fi
  fi
  printf '  %s…%s %s' "$C_DIM" "$C_RESET" "$label"
  ( "$@" >> "$SETUP_LOG" 2>&1 ) &
  local pid=$! frames='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏' i=0
  while kill -0 "$pid" 2>/dev/null; do
    printf '\r  %s%s%s %s' "$C_CYAN" "${frames:i++%${#frames}:1}" "$C_RESET" "$label"
    sleep 0.15
  done
  if wait "$pid"; then printf '\r  %s✓%s %s\n' "$C_GREEN" "$C_RESET" "$label"; return 0
  else printf '\r  %s✗%s %s\n' "$C_RED" "$C_RESET" "$label"; return 1; fi
}

ask() {  # ask "Question" default(y/n) -> returns 0 for yes
  local q=$1 def=${2:-y} a prompt='[Y/n]'
  [ "$def" = n ] && prompt='[y/N]'
  [ -n "${ASSUME_YES:-}" ] && return 0
  printf '  %s?%s %s %s ' "$C_YELLOW" "$C_RESET" "$q" "$prompt"
  read -r a </dev/tty || a=
  a=${a:-$def}
  [[ "$a" =~ ^[Yy] ]]
}

# prompt <var> "Question" <regex> — asks until the answer matches (or empty = give up).
prompt() {
  local __var=$1 __q=$2 __re=${3:-.} __a=
  while :; do
    printf '  %s?%s %s ' "$C_YELLOW" "$C_RESET" "$__q"
    read -r __a </dev/tty 2>/dev/null || { __a=; printf '\n'; }
    [ -z "$__a" ] && { printf -v "$__var" '%s' ''; return 1; }
    [[ "$__a" =~ $__re ]] && { printf -v "$__var" '%s' "$__a"; return 0; }
    warn "that doesn't look right, try again (or leave empty to skip)"
  done
}

pause() { [ -n "${ASSUME_YES:-}" ] && return 0; printf '  %s↵%s %s' "$C_YELLOW" "$C_RESET" "${1:-Press Enter to continue}"; read -r _ </dev/tty || true; }

have() { command -v "$1" >/dev/null 2>&1; }

open_url() {  # open a link in the phone's browser / F-Droid, or print it
  if have termux-open-url; then termux-open-url "$1" >/dev/null 2>&1 || true; fi
  hint "$1"
}

summary() {
  printf '\n'
  progress "$STEP_TOTAL" "$STEP_TOTAL"
  if [ ${#FAILED_STEPS[@]} -eq 0 ]; then
    printf '%s%s  All steps finished.%s\n' "$C_GREEN" "$C_BOLD" "$C_RESET"
  else
    printf '%s%s  %d step(s) need attention:%s\n' "$C_YELLOW" "$C_BOLD" "${#FAILED_STEPS[@]}" "$C_RESET"
    for s in "${FAILED_STEPS[@]}"; do err "$s"; done
    hint "Fix, then run the same script again: finished steps are skipped."
  fi
  hint "Full log: $SETUP_LOG"
}
