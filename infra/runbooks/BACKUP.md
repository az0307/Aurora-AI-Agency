# Backup + disaster-recovery runbook

Two layers: **restic** (encrypted, off-box, granular) + **Hetzner snapshots** (fast,
whole-box). A backup you haven't restored is a hope, not a backup — run the restore drill.

## What to back up
- Docker named volumes: `n8n_data`, `pg_data` (or a `pg_dump`), `kuma_data`, `beszel_data`,
  `ntfy_cache` / `ntfy_etc`, and Dokploy's data dir (`/etc/dokploy`).
- The **n8n encryption key** (`N8N_ENCRYPTION_KEY`) — store in a password manager, not just
  on the box (losing it makes stored credentials unreadable).
- `.env` files (in your secrets manager, e.g. Infisical), and this `infra/` dir (already in git).

## 1. One-time setup (run ONCE per box — not in the nightly job)
```sh
apt-get install -y restic
rclone config       # create a remote e.g. "r2" (S3 provider = Cloudflare R2), or a Storage Box

export RESTIC_REPOSITORY="rclone:r2:aurora-backups/$(hostname)"
export RESTIC_PASSWORD="<strong-passphrase>"      # store safely (password manager)

# Idempotent init: only initialise if the repo doesn't already exist.
# (`restic cat config` exits 10 when the repo is absent, as of restic 0.17+.)
restic cat config >/dev/null 2>&1 || restic init
```

## 2. Nightly backup script (`/usr/local/bin/aurora-backup.sh`)
Fail-closed, cleans up the plaintext dump, and covers every declared volume:
```sh
#!/usr/bin/env bash
set -euo pipefail

export RESTIC_REPOSITORY="rclone:r2:aurora-backups/$(hostname)"
export RESTIC_PASSWORD_FILE="/root/.restic-pass"   # 0600, root-only

# Logical Postgres dump with restrictive perms + guaranteed cleanup.
DUMP="$(mktemp)"; chmod 600 "$DUMP"
trap 'rm -f "$DUMP"' EXIT
docker exec n8n-postgres-1 pg_dump -U n8n n8n > "$DUMP"   # aborts the run if pg_dump fails

# Back up all promised data sources + the dump. Missing volumes are skipped, not fatal.
restic backup \
  /var/lib/docker/volumes/n8n_data \
  /var/lib/docker/volumes/kuma_data \
  /var/lib/docker/volumes/beszel_data \
  /var/lib/docker/volumes/ntfy_cache \
  /var/lib/docker/volumes/ntfy_etc \
  /etc/dokploy \
  "$DUMP"

restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
```
Make it executable: `chmod +x /usr/local/bin/aurora-backup.sh`.

## 3. Schedule it
Cron / systemd-timer (or an n8n workflow!) runs the **script from step 2** nightly — never
re-runs `restic init`. Ping **ntfy** on failure. Example cron:
```sh
15 3 * * *  /usr/local/bin/aurora-backup.sh || curl -d "backup failed on $(hostname)" ntfy.example.com/backups
```

## 4. Restore drill (do this once, for real)
```sh
restic snapshots
restic restore latest --target /tmp/restore-test          # extracts files only

# Actually validate the Postgres dump by importing into a throwaway instance:
docker run -d --name pg-restore-test -e POSTGRES_PASSWORD=test postgres:16-alpine
sleep 5
# the dump was backed up as a temp file — find it under the restored tree:
DUMP_PATH="$(find /tmp/restore-test -name 'tmp.*' -type f | head -n1)"
docker exec -i pg-restore-test psql -U postgres -c 'CREATE DATABASE n8n;'
docker exec -i pg-restore-test psql -U postgres n8n < "$DUMP_PATH"
# validate expected tables exist:
docker exec pg-restore-test psql -U postgres n8n -c '\dt' | grep -qi workflow_entity \
  && echo "RESTORE OK" || echo "RESTORE FAILED — investigate"
docker rm -f pg-restore-test
```
Confirm the n8n volume files also look right under `/tmp/restore-test`.

## 5. Whole-box snapshots (Hetzner)
- Take a snapshot before risky changes (Claude can do this via the Hetzner MCP).
- Snapshots live in the same Project — they cover "I broke the box", not "the region/provider
  is gone". restic-to-R2 covers the latter. Keep both.

## Recovery drill
Lost the box entirely? `terraform apply` a fresh one (cloud-init re-hardens it) →
reinstall Dokploy → `restic restore` the volumes + import the `pg_dump` → redeploy stacks.
Because everything is code + off-box data, this is minutes-to-an-hour, not a rebuild.
