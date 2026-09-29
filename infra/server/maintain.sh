#!/usr/bin/env bash
# maintain.sh — admin + upkeep for aurora-01 (runs ON THE SERVER; uses sudo where needed).
#
#   aurora maintain tune          # one-time system tuning (idempotent; asks before restarting Docker)
#   aurora maintain backup        # snapshot n8n DB + stack data + configs to /var/backups/aurora
#   aurora maintain prune         # free disk: old unused images/build cache, capped journals
#   aurora maintain upgrade STACK # backup, pull newer images, recreate that stack (or: all)
#   aurora maintain report        # full read-only health + upkeep report (paste it to Claude)
#   aurora maintain snapshot      # backup + report + a versions/health manifest = "this worked"
#   aurora maintain offsite       # encrypted copy of the backups to Cloudflare R2 (restic)
#   aurora maintain restore-test  # restore the latest off-box snapshot to a temp dir + verify it
#   aurora maintain nightly       # backup + offsite (what the 03:30 timer runs)
#
# `tune` sets up (each step is skipped if already done):
#   - Docker: log rotation (10 MB × 3 per container) + live-restore (containers keep running
#     while Docker itself restarts/updates)
#   - 4 GB swap + swappiness 10 (the 8 GB box slows down under a spike instead of OOM-killing)
#   - kernel: more inotify watches (agents/editors watch many files), gentler cache pressure
#   - journald capped at 300 MB
#   - systemd timers: nightly backup + offsite 03:30, weekly prune Sun 04:15 (server local time)
#   - admin tools: btop, ncdu, duf, lazydocker (Docker TUI), restic
#
# Backups land on the box (/var/backups/aurora, root-only, 7 kept), then `offsite` pushes an
# encrypted restic copy to Cloudflare R2 (7 daily / 4 weekly / 6 monthly). Offsite needs
# RESTIC_PASSWORD + R2_* in secrets.env (KEYS.md §5); without them it skips with a warning.
# Never touched: Docker volumes are only read, never pruned; secrets are never printed.
set -euo pipefail

ROOT="${AURORA_ROOT:-/opt/aurora}"
BACKUP_DIR="${AURORA_BACKUP_DIR:-/var/backups/aurora}"
KEEP="${AURORA_BACKUP_KEEP:-7}"
LAZYDOCKER_VERSION="${LAZYDOCKER_VERSION:-0.24.1}"
ASSUME_YES=0; for a in "$@"; do [ "$a" = --yes ] && ASSUME_YES=1; done

say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[33mWARN\033[0m %s\n' "$*"; }
die()  { printf '\033[31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }
as_root() { if [ "$(id -u)" = 0 ]; then "$@"; else sudo "$@"; fi; }

# Compose projects = the stack folder names (compose's default project name).
stacks_running() { docker ps --format '{{.Label "com.docker.compose.project"}}' | sort -u | grep -v '^$' || true; }

# ------------------------------------------------------------------------------- tune
tune() {
  say "Docker daemon: log rotation + live-restore"
  local cfg=/etc/docker/daemon.json want
  want='{"log-driver":"json-file","log-opts":{"max-size":"10m","max-file":"3"},"live-restore":true}'
  local cur='{}'; as_root test -s "$cfg" && cur=$(as_root cat "$cfg")
  local merged; merged=$(jq -S -n --argjson a "$cur" --argjson b "$want" '$a * $b')
  if [ "$(jq -S . <<<"$cur")" != "$merged" ]; then
    as_root install -d /etc/docker
    printf '%s\n' "$merged" | as_root tee "$cfg" >/dev/null
    # Log options apply to containers created AFTER this; `upgrade` recreates them.
    if [ "$ASSUME_YES" = 1 ] || { read -r -p "Restart Docker now to apply? Containers come back by themselves (~30 s) [y/N] " a; [[ "$a" =~ ^[Yy]$ ]]; }; then
      as_root systemctl restart docker && say "Docker restarted"
    else warn "not restarted — it applies at the next reboot or: sudo systemctl restart docker"; fi
  else say "  already set"; fi

  say "Swap (4 GB, swappiness 10)"
  if [ "$(awk '/SwapTotal/{print $2}' /proc/meminfo)" -eq 0 ]; then
    { as_root fallocate -l 4G /swapfile && as_root chmod 600 /swapfile && as_root mkswap -q /swapfile && as_root swapon /swapfile; } || warn "swap setup failed — check disk space"
    grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' | as_root tee -a /etc/fstab >/dev/null
  else say "  swap already present"; fi

  say "Kernel settings (/etc/sysctl.d/99-aurora.conf)"
  printf '%s\n' '# aurora-01 — written by server/maintain.sh tune' \
    'vm.swappiness = 10' 'vm.vfs_cache_pressure = 50' \
    'fs.inotify.max_user_watches = 524288' 'fs.inotify.max_user_instances = 1024' \
    | as_root tee /etc/sysctl.d/99-aurora.conf >/dev/null
  as_root sysctl -q --system >/dev/null || warn "sysctl reload reported a problem (settings apply at reboot)"

  say "journald capped at 300 MB"
  as_root install -d /etc/systemd/journald.conf.d
  printf '[Journal]\nSystemMaxUse=300M\n' | as_root tee /etc/systemd/journald.conf.d/aurora.conf >/dev/null
  as_root systemctl restart systemd-journald 2>/dev/null || true

  say "Timers: nightly backup + offsite 03:30, weekly prune Sun 04:15"
  unit() {  # unit NAME ACTION ONCALENDAR
    printf '[Unit]\nDescription=aurora %s\n\n[Service]\nType=oneshot\nExecStart=%s/server/maintain.sh %s\nNice=10\nIOSchedulingClass=idle\n' \
      "$2" "$ROOT" "$2" | as_root tee "/etc/systemd/system/$1.service" >/dev/null
    printf '[Unit]\nDescription=aurora %s timer\n\n[Timer]\nOnCalendar=%s\nPersistent=true\nRandomizedDelaySec=10m\n\n[Install]\nWantedBy=timers.target\n' \
      "$2" "$3" | as_root tee "/etc/systemd/system/$1.timer" >/dev/null
  }
  unit aurora-backup nightly '*-*-* 03:30'
  unit aurora-prune prune 'Sun *-*-* 04:15'
  as_root systemctl daemon-reload
  as_root systemctl enable --now aurora-backup.timer aurora-prune.timer >/dev/null

  say "Admin tools: btop ncdu duf lazydocker"
  as_root env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq btop ncdu duf restic >/dev/null || warn "apt tools failed"
  if ! command -v lazydocker >/dev/null; then
    local arch; arch=$(uname -m); [ "$arch" = aarch64 ] && arch=arm64
    local url="https://github.com/jesseduffield/lazydocker/releases/download/v${LAZYDOCKER_VERSION}/lazydocker_${LAZYDOCKER_VERSION}_Linux_${arch}.tar.gz"
    if curl -fsSL "$url" | as_root tar -xz -C /usr/local/bin lazydocker; then say "  lazydocker $LAZYDOCKER_VERSION"
    else warn "lazydocker download failed ($url)"; fi
  fi
  say "Tuning done."
}

# ----------------------------------------------------------------------------- backup
backup() {
  local day; day=$(date +%F)
  local dst="$BACKUP_DIR/$day"
  as_root install -d -m 700 "$BACKUP_DIR" "$dst"
  say "Backup → $dst"

  # 1. n8n's Postgres as a proper dump (a raw copy of a running database isn't safe).
  local pg; pg=$(docker ps -q --filter label=com.docker.compose.project=n8n --filter label=com.docker.compose.service=postgres | head -1)
  if [ -n "$pg" ]; then
    docker exec "$pg" sh -c 'pg_dump -U "${POSTGRES_USER:-n8n}" "${POSTGRES_DB:-n8n}"' | gzip | as_root tee "$dst/n8n-postgres.sql.gz" >/dev/null \
      && say "  n8n database dumped" || warn "n8n dump failed — continuing so volumes + configs still back up"
  else warn "n8n postgres isn't running — skipped its dump"; fi

  # 2. Every other named volume of the stacks, each project briefly paused so files are
  #    consistent. The n8n Postgres volume is skipped (dumped above).
  local v proj
  for v in $(docker volume ls -q --filter label=com.docker.compose.project); do
    case "$v" in *pg_data*) continue ;; esac
    proj=$(docker volume inspect -f '{{index .Labels "com.docker.compose.project"}}' "$v")
    local ids; ids=$(docker ps -q --filter "label=com.docker.compose.project=$proj")
    [ -n "$ids" ] && docker pause $ids >/dev/null 2>&1 || true
    docker run --rm -v "$v:/v:ro" alpine:3.20 tar -C /v -czf - . | as_root tee "$dst/vol-$v.tgz" >/dev/null || warn "volume $v failed"
    [ -n "$ids" ] && docker unpause $ids >/dev/null 2>&1 || true
  done
  say "  volumes archived"

  # 3. Configs + secrets + bind-mounted data (Hermes memories, Tailscale state).
  as_root tar -C "$ROOT" -czf "$dst/configs.tgz" --ignore-failed-read \
    secrets.env $(cd "$ROOT" && find stacks -maxdepth 3 \
      \( -path stacks/hermes/data -o -path stacks/tailscale/state -o -path stacks/admin/data \) -print -prune \
      -o \( -name '.env' -o -name 'config.yaml' -o -name 'docker-compose.override.yml' \) -print 2>/dev/null) 2>/dev/null \
    || warn "configs archive had errors"
  as_root chmod -R go-rwx "$dst"

  # 4. Keep the newest $KEEP days.
  as_root find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 -type d -name '20*' | sort | head -n -"$KEEP" | while read -r old; do as_root rm -rf "$old"; done
  say "Backup done: $(as_root du -sh "$dst" | cut -f1) (keeping $KEEP days)"
}

# ------------------------------------------------------------------------------ prune
prune() {
  say "Pruning unused images + build cache older than 7 days (volumes are never touched)"
  local before; before=$(df -P / | awk 'NR==2{print $4}')
  docker image prune -af --filter until=168h >/dev/null
  docker builder prune -af --filter until=168h >/dev/null 2>&1 || true
  as_root journalctl --vacuum-size=300M >/dev/null 2>&1 || true
  local after; after=$(df -P / | awk 'NR==2{print $4}')
  say "Freed $(( (after - before) / 1024 )) MB"
}

# ---------------------------------------------------------------------------- offsite
# Encrypted off-box copy of $BACKUP_DIR to Cloudflare R2 (S3 API) with restic — survives
# losing the server. Keys come from $ROOT/secrets.env and stay in this process: they reach
# restic only through its environment (never argv), and are never printed.
OFFSITE_STATUS="$BACKUP_DIR/.offsite-last"
NTFY_URL="${AURORA_NTFY_URL:-http://127.0.0.1:8888/aurora-backups}"
RESTIC_REPO=""

need_root() { [ "$(id -u)" = 0 ] || exec sudo --preserve-env=AURORA_ROOT,AURORA_BACKUP_DIR "$0" "$@"; }

# Load secrets.env (written with printf %q by bootstrap.sh) as plain, unexported variables.
# Returns 1 when off-box backup isn't configured yet.
offsite_keys() {
  [ -f "$ROOT/secrets.env" ] || return 1
  # shellcheck disable=SC1091
  . "$ROOT/secrets.env"
  [ -n "${RESTIC_PASSWORD:-}" ] && [ -n "${R2_ACCESS_KEY_ID:-}" ] && [ -n "${R2_SECRET_ACCESS_KEY:-}" ] || return 1
  if [ -n "${AURORA_RESTIC_REPO:-}" ]; then RESTIC_REPO="$AURORA_RESTIC_REPO"   # tests: a local repo
  else
    [ -n "${R2_ACCOUNT_ID:-}" ] || return 1
    RESTIC_REPO="s3:https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com/${R2_BUCKET:-aurora-backups}/$(hostname -s)"
  fi
}

# rst ARGS… — restic with the keys in its environment only.
rst() {
  RESTIC_REPOSITORY="$RESTIC_REPO" RESTIC_PASSWORD="$RESTIC_PASSWORD" \
  AWS_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID" AWS_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY" \
  AWS_DEFAULT_REGION=auto restic "$@"
}

offsite_fail() {  # record + push a phone alert (best effort), then fail the run
  printf 'FAILED %s %s\n' "$(date -Is)" "$1" > "$OFFSITE_STATUS" 2>/dev/null || true
  curl -fsS -m 10 -H "Title: aurora backup failed" -d "offsite backup failed on $(hostname -s): $1" "$NTFY_URL" >/dev/null 2>&1 || true
  die "offsite backup failed: $1"
}

offsite() {
  need_root offsite
  if ! offsite_keys; then
    warn "off-box backup skipped: set RESTIC_PASSWORD, R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY in secrets.env (KEYS.md §5)"
    return 0
  fi
  command -v restic >/dev/null || offsite_fail "restic not installed (run: aurora maintain tune)"
  ls -d "$BACKUP_DIR"/20* >/dev/null 2>&1 || offsite_fail "no local backups in $BACKUP_DIR (run: aurora maintain backup)"
  say "Off-box backup → R2 (restic, encrypted)"
  # Initialise once; `init` refuses an existing repo, so a wrong password fails here too.
  if ! rst cat config >/dev/null 2>&1; then
    rst init >/dev/null 2>&1 || offsite_fail "cannot open or create the restic repo (check RESTIC_PASSWORD / R2 keys / bucket)"
    say "  repository initialised"
  fi
  rst backup -q --tag aurora --host "$(hostname -s)" --exclude "$OFFSITE_STATUS" "$BACKUP_DIR" \
    || offsite_fail "restic backup"
  rst forget -q --tag aurora --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune >/dev/null \
    || offsite_fail "restic forget/prune"
  printf 'ok %s\n' "$(date -Is)" > "$OFFSITE_STATUS"
  say "Off-box backup done"
}

# Restore the newest snapshot into a temp dir and prove it's usable: repo integrity, the
# newest day's configs archive lists, and the n8n dump (when present) is valid gzip.
restore_test() {
  need_root restore-test
  offsite_keys || die "off-box backup isn't configured (KEYS.md §5)"
  command -v restic >/dev/null || die "restic not installed (run: aurora maintain tune)"
  RESTORE_TMP=$(mktemp -d); trap 'rm -rf "$RESTORE_TMP"' EXIT; local tmp="$RESTORE_TMP"
  say "Checking repository"
  rst check -q >/dev/null || die "restic check failed"
  say "Restoring latest snapshot → $tmp"
  rst restore latest --tag aurora --target "$tmp" >/dev/null || die "restore failed"
  local day; day=$(find "$tmp" -type d -path "*${BACKUP_DIR}/20*" -prune | sort | tail -1)
  [ -n "$day" ] || die "no backup day found in the snapshot"
  [ -f "$day/configs.tgz" ] && tar -tzf "$day/configs.tgz" >/dev/null || die "configs.tgz missing or unreadable in $(basename "$day")"
  if [ -f "$day/n8n-postgres.sql.gz" ]; then
    gzip -t "$day/n8n-postgres.sql.gz" 2>/dev/null || die "n8n-postgres.sql.gz is corrupt in $(basename "$day")"
  else warn "no n8n dump in $(basename "$day") (n8n wasn't running that night)"; fi
  say "Restore test passed: $(basename "$day") restores cleanly. Real restore: RESTORE in runbooks/BACKUP.md"
}

nightly() { backup; offsite; }

# ---------------------------------------------------------------------------- upgrade
upgrade() {
  local target="${1:-}"; [ -n "$target" ] || die "upgrade which stack? (a stack name, or: all)"
  local list; if [ "$target" = all ]; then list=$(stacks_running); else list="$target"; fi
  [ -n "$list" ] || die "nothing running to upgrade"
  backup
  local s svcs
  for s in $list; do
    [ -d "$ROOT/stacks/$s" ] || { warn "no stack folder for $s — skipped"; continue; }
    # Only the services that are running now (e.g. n8n without Caddy, computer without desktop).
    svcs=$(cd "$ROOT/stacks/$s" && docker compose ps --services --status running)
    [ -n "$svcs" ] || { warn "$s isn't running — skipped (start it with: aurora start $s)"; continue; }
    say "Upgrading $s: $(echo $svcs)"
    (cd "$ROOT/stacks/$s" && docker compose pull -q $svcs && docker compose up -d $svcs) \
      || warn "$s upgrade failed — continuing with the next stack"
  done
  say "Upgrade done. Check: aurora maintain report"
}

# ----------------------------------------------------------------------------- report
report() {
  set +e   # a report must finish even when one probe fails (restored at the end so callers keep -e)
  echo "aurora-01 report — $(date -Is)   (safe to paste: no secret values)"
  bash "$ROOT/check.sh" || true
  echo; echo "Upkeep"
  local lr ll; lr=$(jq -r '"log \(.["log-opts"]["max-size"] // "unset") × \(.["log-opts"]["max-file"] // "?") · live-restore \(.["live-restore"] // false)"' /etc/docker/daemon.json 2>/dev/null || echo "not tuned (run: aurora maintain tune)")
  echo "  · Docker: $(docker version -f '{{.Server.Version}}' 2>/dev/null) · $lr"
  echo "  · Swap: $(awk '/SwapTotal/{printf "%d MB", $2/1024}' /proc/meminfo) · swappiness $(cat /proc/sys/vm/swappiness)"
  for t in aurora-backup aurora-prune; do
    ll=$(systemctl show "$t.timer" -p LastTriggerUSec --value 2>/dev/null)
    echo "  · $t: $(systemctl is-active "$t.timer" 2>/dev/null || echo missing) · last: ${ll:-never}"
  done
  echo "  · Latest backup: $(as_root ls -1 "$BACKUP_DIR" 2>/dev/null | grep '^20' | tail -1 || echo none)"
  echo "  · Off-box (R2): $(as_root cat "$BACKUP_DIR/.offsite-last" 2>/dev/null || echo 'never — set R2 keys (KEYS.md §5), then: aurora maintain offsite')"
  echo "  · Tools: node $(node -v 2>/dev/null || echo -) · opencode $(opencode --version 2>/dev/null || echo -) · claude $(claude --version 2>/dev/null | head -1 || echo -) · lazydocker $(command -v lazydocker >/dev/null && echo yes || echo -)"
  echo "  · Docker disk:"; docker system df 2>/dev/null | sed 's/^/      /'
  echo "  · Listening on non-loopback addresses (should be only ssh/xrdp on tailscale + tailscaled):"
  ss -Htlnp 2>/dev/null | awk '$4 !~ /^(127\.|\[::1\])/ {print "      " $4}' | sort -u
  set -e   # restore for any caller (snapshot() calls report() mid-function)
}

# --------------------------------------------------------------------------- snapshot
# A "known-good" marker: a fresh backup + the full report + a manifest of exactly what was
# running and at which image digests, saved together so you can prove/return to this state.
snapshot() {
  local day; day=$(date +%F_%H%M)
  local dir="$BACKUP_DIR/snapshot-$day"
  backup
  as_root install -d -m 700 "$dir"
  say "Snapshot → $dir"
  report > /tmp/aurora-report.txt 2>&1 || true; as_root cp /tmp/aurora-report.txt "$dir/report.txt"; rm -f /tmp/aurora-report.txt
  # Exact images + digests of everything running, so this state is reproducible.
  docker ps --format '{{.Names}} {{.Image}}' | while read -r n img; do
    printf '%s\t%s\t%s\n' "$n" "$img" "$(docker inspect -f '{{index .Image}}' "$n" 2>/dev/null)"
  done | as_root tee "$dir/images.tsv" >/dev/null
  (cd "$ROOT" && git rev-parse HEAD 2>/dev/null) | as_root tee "$dir/repo-commit.txt" >/dev/null || true
  as_root sh -c "echo 'snapshot taken '$(date -Is) > '$dir/OK.txt'"
  say "Snapshot done. If check.sh showed all ✓, this is a confirmed-working point to return to."
  grep -q '✗' "$dir/report.txt" 2>/dev/null && warn "report.txt still has ✗ lines — not fully green yet" || say "report.txt is clean (no ✗)."
}

case "${1:-}" in
  tune) tune ;; backup) backup ;; prune) prune ;; upgrade) upgrade "${2:-}" ;; report) report ;; snapshot) snapshot ;;
  offsite) offsite ;; restore-test) restore_test ;; nightly) nightly ;;
  *) sed -n '2,26p' "$0"; exit 2 ;;
esac
