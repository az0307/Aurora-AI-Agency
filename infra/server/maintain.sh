#!/usr/bin/env bash
# maintain.sh — admin + upkeep for aurora-01 (runs ON THE SERVER; uses sudo where needed).
#
#   aurora maintain tune          # one-time system tuning (idempotent; asks before restarting Docker)
#   aurora maintain backup        # snapshot n8n DB + stack data + configs to /var/backups/aurora
#   aurora maintain prune         # free disk: old unused images/build cache, capped journals
#   aurora maintain upgrade STACK # backup, pull newer images, recreate that stack (or: all)
#   aurora maintain report        # full read-only health + upkeep report (paste it to Claude)
#   aurora maintain snapshot      # backup + report + a versions/health manifest = "this worked"
#   aurora maintain offsite       # push the newest backup to your bucket, encrypted (also runs nightly)
#   aurora maintain offsite-status   ·   offsite-restore [id]   # list copies · restore to a new folder
#   aurora maintain pg-upgrade    # n8n Postgres 16 → 17: backup, dump, restore onto a new volume,
#                                 #   verify row counts, auto-rollback on failure (asks first)
#
# `tune` sets up (each step is skipped if already done):
#   - Docker: log rotation (10 MB × 3 per container) + live-restore (containers keep running
#     while Docker itself restarts/updates)
#   - 4 GB swap + swappiness 10 (the 8 GB box slows down under a spike instead of OOM-killing)
#   - kernel: more inotify watches (agents/editors watch many files), gentler cache pressure
#   - journald capped at 300 MB
#   - systemd timers: nightly backup 03:30, weekly prune Sun 04:15 (server local time)
#   - admin tools: btop, ncdu, duf, lazydocker (Docker TUI)
#   - cleanup: closes ufw 80/443 left by older cloud-init (unless a container really publishes
#     them), removes Ubuntu's broken apt thefuck (its login traceback)
#
# Backups land ON the box (/var/backups/aurora, root-only, 7 kept) and, once RESTIC_* is in
# secrets.env, an encrypted copy goes to your S3 bucket every night (see `offsite`).
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

# Containers this run has paused (backup). Always unpaused on exit — even on Ctrl-C or a
# systemd stop mid-archive — so an interrupted backup never leaves a stack frozen.
PAUSED=""
unpause_paused() { if [ -n "$PAUSED" ]; then docker unpause $PAUSED >/dev/null 2>&1 || true; PAUSED=""; fi; }
trap unpause_paused EXIT
trap 'unpause_paused; exit 130' INT TERM

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

  say "Timers: nightly backup 03:30, weekly prune Sun 04:15"
  unit() {  # unit NAME ACTION ONCALENDAR
    printf '[Unit]\nDescription=aurora %s\n\n[Service]\nType=oneshot\nExecStart=%s/server/maintain.sh %s\nNice=10\nIOSchedulingClass=idle\n' \
      "$2" "$ROOT" "$2" | as_root tee "/etc/systemd/system/$1.service" >/dev/null
    printf '[Unit]\nDescription=aurora %s timer\n\n[Timer]\nOnCalendar=%s\nPersistent=true\nRandomizedDelaySec=10m\n\n[Install]\nWantedBy=timers.target\n' \
      "$2" "$3" | as_root tee "/etc/systemd/system/$1.timer" >/dev/null
  }
  unit aurora-backup backup '*-*-* 03:30'
  unit aurora-prune prune 'Sun *-*-* 04:15'
  as_root systemctl daemon-reload
  as_root systemctl enable --now aurora-backup.timer aurora-prune.timer >/dev/null

  say "Admin tools: btop ncdu duf lazydocker"
  as_root env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq btop ncdu duf >/dev/null || warn "apt tools failed"
  if ! command -v lazydocker >/dev/null; then
    local arch; arch=$(uname -m); [ "$arch" = aarch64 ] && arch=arm64
    local url="https://github.com/jesseduffield/lazydocker/releases/download/v${LAZYDOCKER_VERSION}/lazydocker_${LAZYDOCKER_VERSION}_Linux_${arch}.tar.gz"
    if curl -fsSL "$url" | as_root tar -xz -C /usr/local/bin lazydocker; then say "  lazydocker $LAZYDOCKER_VERSION"
    else warn "lazydocker download failed ($url)"; fi
  fi
  # Older cloud-init opened 80/443 in ufw. Nothing on this box serves the public internet
  # (Tailscale serve; a Cloudflare Tunnel is outbound-only), so close them — unless a container
  # really publishes 80/443 (a deliberate `--profile public` Caddy), which is left alone.
  if command -v ufw >/dev/null && as_root ufw status 2>/dev/null | grep -qE '^(80|443)/tcp +ALLOW'; then
    if docker ps --format '{{.Ports}}' | grep -qE '(0\.0\.0\.0|\[::\]|:::):(80|443)->'; then
      warn "ufw allows 80/443 and a container publishes them (public Caddy?) — left as is"
    else
      as_root ufw delete allow 80/tcp >/dev/null 2>&1 || true
      as_root ufw delete allow 443/tcp >/dev/null 2>&1 || true
      say "Closed ufw 80/443 (nothing here is public)"
    fi
  fi
  # Ubuntu 24.04's apt thefuck imports distutils (removed in Python 3.12), so the fish login
  # alias printed a traceback every time. Older installs have it; remove it only if it's broken.
  if command -v thefuck >/dev/null && ! thefuck --version >/dev/null 2>&1; then
    as_root env DEBIAN_FRONTEND=noninteractive apt-get remove -y -qq thefuck >/dev/null \
      && say "Removed broken thefuck (login traceback gone)" || warn "couldn't remove thefuck"
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
    if [ -n "$ids" ]; then PAUSED="$ids"; docker pause $ids >/dev/null 2>&1 || true; fi
    docker run --rm -v "$v:/v:ro" alpine:3.20 tar -C /v -czf - . | as_root tee "$dst/vol-$v.tgz" >/dev/null || warn "volume $v failed"
    unpause_paused
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

  # 5. Off-box copy (T009) when configured; a failure never spoils the on-box backup.
  if offsite_ready; then offsite || warn "off-box copy failed — the on-box backup is fine; retry: aurora maintain offsite"
  else say "  off-box copy not set up yet (RESTIC_* in secrets.env — see KEYS.md)"; fi
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
  if offsite_ready; then echo "  · Off-box copy: set up (nightly; list with: aurora maintain offsite-status)"
  else echo "  · Off-box copy: NOT set up — on-box backups don't survive losing the server (KEYS.md → restic)"; fi
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

# ---------------------------------------------------------------------- off-box (restic)
# Encrypted copy of the newest backup in an S3-compatible bucket (Backblaze B2, Cloudflare R2,
# Hetzner Object Storage…), so losing the server doesn't lose the backups. Needs, in secrets.env:
#   RESTIC_REPOSITORY      s3:https://<endpoint>/<bucket>/aurora-01
#   RESTIC_PASSWORD        the encryption key — lose it and every copy is unreadable (Bitwarden!)
#   AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY   the bucket's S3 keys (+ AWS_DEFAULT_REGION if needed)
# Values are read by root from secrets.env and handed to the container by NAME (`-e VAR`), so
# they never appear on a command line or in output. restic runs from a pinned image (no install).
RESTIC_IMAGE="${RESTIC_IMAGE:-restic/restic:0.19.1}"   # pinned 2026-09-28
OFFSITE_HOST="${OFFSITE_HOST:-$(hostname -s)}"          # snapshots are grouped per host
OFFSITE_KEEP="${OFFSITE_KEEP:---keep-daily 7 --keep-weekly 4 --keep-monthly 6}"

offsite_ready() {
  as_root grep -qE '^RESTIC_REPOSITORY=.+' "$ROOT/secrets.env" 2>/dev/null \
    && as_root grep -qE '^RESTIC_PASSWORD=.+' "$ROOT/secrets.env" 2>/dev/null
}
restic_run() { # restic_run "<extra docker args, e.g. -v a:b>" <restic args…>
  local extra="$1"; shift
  as_root env AURORA_SECRETS="$ROOT/secrets.env" AURORA_IMG="$RESTIC_IMAGE" AURORA_H="$OFFSITE_HOST" \
    AURORA_EXTRA="$extra ${AURORA_RESTIC_DOCKER_ARGS:-}" bash -c '
    set -a; . "$AURORA_SECRETS"; set +a
    exec docker run --rm -i --hostname "$AURORA_H" $AURORA_EXTRA \
      -e RESTIC_REPOSITORY -e RESTIC_PASSWORD -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
      -v aurora-restic-cache:/root/.cache/restic "$AURORA_IMG" "$@"' restic_run "$@"
}

offsite() { # push the newest backup; creates the repo on first use; applies retention
  offsite_ready || die "off-box backup isn't set up: add RESTIC_REPOSITORY, RESTIC_PASSWORD and the bucket's AWS_* keys to secrets.env (see KEYS.md), ship it, retry"
  local latest; latest=$(as_root find "$BACKUP_DIR" -mindepth 1 -maxdepth 1 -type d -name '20*' | sort | tail -1)
  [ -n "$latest" ] || die "no backup in $BACKUP_DIR yet — run: aurora maintain backup"
  say "Off-box: $(basename "$latest") → bucket (encrypted)"
  restic_run "" cat config >/dev/null 2>&1 || { say "  first run: creating the encrypted repository"; restic_run "" init >/dev/null; }
  # A fixed path (/aurora-backup) + host tag, so restic dedups night to night and retention groups them.
  restic_run "-v $latest:/aurora-backup:ro" backup /aurora-backup --host "$OFFSITE_HOST" --tag nightly --quiet
  restic_run "" forget --host "$OFFSITE_HOST" --prune $OFFSITE_KEEP --quiet >/dev/null
  restic_run "" check --quiet >/dev/null && say "  pushed, retention applied, repository checked"
}
offsite_status() {
  offsite_ready || die "off-box backup isn't set up (see KEYS.md)"
  restic_run "" snapshots --host "$OFFSITE_HOST" --compact
}
offsite_restore() { # offsite-restore [snapshot-id|latest] → a NEW folder; live data is never touched
  offsite_ready || die "off-box backup isn't set up (see KEYS.md)"
  local snap="${1:-latest}" dst; dst="$BACKUP_DIR/restore-$(date +%F_%H%M%S)"
  as_root install -d -m 700 "$dst"
  say "Restoring off-box snapshot '$snap' → $dst"
  restic_run "-v $dst:/restore" restore "$snap" --host "$OFFSITE_HOST" --target /restore >/dev/null
  as_root chmod -R go-rwx "$dst"
  say "Restored into $dst/aurora-backup:"; as_root ls -la "$dst/aurora-backup"
  echo "   It's the same layout as a nightly backup (n8n-postgres.sql.gz, vol-*.tgz, configs.tgz)."
  echo "   Nothing live was changed. To use it, copy what you need back (see server/README.md → Restore)."
}

# ------------------------------------------------------------------------- pg-upgrade
# n8n's Postgres 16 → 17. 17 can't read 16's data files, so this is a dump/restore onto a NEW
# volume: full backup → stop n8n → dump → start 17 on the new volume → restore → compare every
# table's row count → start n8n and wait for /healthz. Any failure rolls back to 16 on the old
# volume, which is never modified or deleted. Values in .env are never printed.
PG_TARGET_TAG="${PG_TARGET_TAG:-17-alpine}"
PG_TARGET_VOLUME="${PG_TARGET_VOLUME:-n8n_pg_data17}"

envset() { # envset FILE KEY VALUE — replace or append one line; file stays mode 600
  local tmp; tmp=$(umask 077; mktemp "$1.XXXXXX")
  K="$2" V="$3" awk 'BEGIN{k=ENVIRON["K"]; v=ENVIRON["V"]} index($0, k"=")==1 {if(!d) print k"="v; d=1; next} {print} END{if(!d) print k"="v}' "$1" > "$tmp" \
    && chmod 600 "$tmp" && mv "$tmp" "$1"
}
pg_psql() { docker compose exec -T postgres sh -c 'psql -h 127.0.0.1 -v ON_ERROR_STOP=1 -X -q -At -U "$POSTGRES_USER" -d "$POSTGRES_DB" "$@"' psql "$@"; }
pg_counts() { # "table<TAB>rows" for every table in public, sorted — compared before vs after
  pg_psql -c "select table_name || E'\t' || (xpath('/row/c/text()', query_to_xml(format('select count(*) as c from public.%I', table_name), false, true, '')))[1]::text
              from information_schema.tables where table_schema='public' and table_type='BASE TABLE' order by table_name"
}
pg_wait() { # until 17 answers over TCP (the init-time temp server is socket-only, so this skips it)
  local i; for i in $(seq 1 60); do
    docker compose exec -T postgres sh -c 'pg_isready -q -h 127.0.0.1 -U "$POSTGRES_USER"' 2>/dev/null && return 0; sleep 2
  done; return 1
}

pg_upgrade() {
  local dir="$ROOT/stacks/n8n"
  [ -f "$dir/.env" ] || die "no stacks/n8n/.env — n8n was never set up here"
  cd "$dir"
  local cur_tag cur_vol
  cur_tag=$(sed -n 's/^POSTGRES_IMAGE_TAG=//p' .env | tail -1); cur_tag=${cur_tag:-16-alpine}
  cur_vol=$(sed -n 's/^PG_VOLUME_NAME=//p' .env | tail -1);     cur_vol=${cur_vol:-n8n_pg_data}
  case "$cur_tag" in 16*) ;; *) say "n8n Postgres is on $cur_tag already — nothing to do"; return 0 ;; esac
  docker compose ps --status running -q postgres | grep -q . || die "n8n's Postgres isn't running — start it first: aurora start n8n"
  docker volume inspect "$PG_TARGET_VOLUME" >/dev/null 2>&1 \
    && die "volume $PG_TARGET_VOLUME already exists (an earlier attempt?). Check it, then: docker volume rm $PG_TARGET_VOLUME"

  say "n8n Postgres $cur_tag (volume $cur_vol) → $PG_TARGET_TAG (new volume $PG_TARGET_VOLUME)"
  echo "   n8n is offline for a few minutes. The old volume is kept, so you can roll back."
  if [ "$ASSUME_YES" != 1 ]; then
    read -r -p "Type 'upgrade' to go ahead: " a; [ "$a" = upgrade ] || die "cancelled — nothing changed"
  fi

  backup
  local work; work="$BACKUP_DIR/pg-upgrade-$(date +%F_%H%M)"; as_root install -d -m 700 "$work"

  say "Stopping n8n (Postgres stays up for the dump)"
  docker compose stop n8n >/dev/null
  local before; before=$(pg_counts) || { docker compose start n8n >/dev/null; die "couldn't read row counts on 16 — n8n restarted, nothing changed"; }
  say "Dumping $(printf '%s\n' "$before" | grep -c .) tables"
  docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges' \
    | gzip | as_root tee "$work/n8n-pg16.sql.gz" >/dev/null \
    || { docker compose start n8n >/dev/null; die "dump failed — n8n restarted on 16, nothing changed"; }

  rollback() {
    warn "$1 — rolling back to $cur_tag on $cur_vol"
    docker compose stop postgres >/dev/null 2>&1 || true
    envset .env POSTGRES_IMAGE_TAG "$cur_tag"; envset .env PG_VOLUME_NAME "$cur_vol"
    docker compose up -d postgres n8n >/dev/null 2>&1 || true
    die "rolled back; n8n is on its old database. The failed $PG_TARGET_VOLUME is kept for inspection (docker volume rm $PG_TARGET_VOLUME to discard). Dump: $work"
  }

  say "Starting Postgres $PG_TARGET_TAG on $PG_TARGET_VOLUME"
  docker compose stop postgres >/dev/null
  envset .env POSTGRES_IMAGE_TAG "$PG_TARGET_TAG"; envset .env PG_VOLUME_NAME "$PG_TARGET_VOLUME"
  docker compose up -d postgres >/dev/null 2>&1 || rollback "Postgres $PG_TARGET_TAG didn't start"
  pg_wait || rollback "Postgres $PG_TARGET_TAG never became ready"

  say "Restoring"
  as_root cat "$work/n8n-pg16.sql.gz" | gunzip | pg_psql >/dev/null || rollback "restore failed"
  local after; after=$(pg_counts) || rollback "couldn't read row counts on $PG_TARGET_TAG"
  [ "$before" = "$after" ] || rollback "row counts differ after restore ($(diff <(echo "$before") <(echo "$after") | grep -c '^[<>]') lines)"
  say "Row counts match on all $(printf '%s\n' "$after" | grep -c .) tables"

  say "Starting n8n on $PG_TARGET_TAG"
  docker compose up -d n8n >/dev/null 2>&1 || rollback "n8n didn't start"
  local i ok=0; for i in $(seq 1 60); do curl -fsS -m 5 -o /dev/null http://127.0.0.1:5678/healthz 2>/dev/null && { ok=1; break; }; sleep 3; done
  [ "$ok" = 1 ] || rollback "n8n didn't answer /healthz on $PG_TARGET_TAG"

  say "Done: n8n runs on Postgres $PG_TARGET_TAG (volume $PG_TARGET_VOLUME). Dump kept in $work."
  echo "   The old volume $cur_vol is untouched. Once you're happy (say a week), free it:"
  echo "     docker volume rm $cur_vol"
  echo "   Roll back before then (loses anything n8n saved since): set POSTGRES_IMAGE_TAG=$cur_tag and"
  echo "   PG_VOLUME_NAME=$cur_vol in stacks/n8n/.env, then: aurora start n8n"
}

case "${1:-}" in
  tune) tune ;; backup) backup ;; prune) prune ;; upgrade) upgrade "${2:-}" ;; report) report ;; snapshot) snapshot ;;
  pg-upgrade) pg_upgrade ;;
  offsite) offsite ;; offsite-status) offsite_status ;; offsite-restore) offsite_restore "${2:-latest}" ;;
  *) sed -n '2,28p' "$0"; exit 2 ;;
esac
