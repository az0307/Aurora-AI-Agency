# Backup + disaster-recovery runbook

Two layers: **restic** (encrypted, off-box, granular) + **Hetzner snapshots** (fast,
whole-box). A backup you haven't restored is a hope, not a backup — test step 4.

## What to back up
- Docker named volumes: `n8n_data`, `pg_data` (or a `pg_dump`), `kuma_data`, `beszel_data`,
  `ntfy_*`, Dokploy's data.
- The **n8n encryption key** (`N8N_ENCRYPTION_KEY`) — store in a password manager, not just
  on the box.
- `.env` files (in your secrets manager, e.g. Infisical), and this `infra/` dir (already in git).

## 1. Off-box target (pick one)
- **Cloudflare R2** (S3-compatible, egress-free) — good default.
- **Hetzner Storage Box** (cheap, same provider).

Configure rclone once:
```sh
rclone config       # create a remote named e.g. "r2" (S3 provider = Cloudflare R2)
```

## 2. restic to that target
```sh
apt-get install -y restic
export RESTIC_REPOSITORY="rclone:r2:aurora-backups/$(hostname)"
export RESTIC_PASSWORD="<strong-passphrase>"   # store safely
restic init

# Postgres: dump logically rather than copying live files
docker exec n8n-postgres-1 pg_dump -U n8n n8n > /tmp/n8n.sql

# Back up volume data + the dump
restic backup /var/lib/docker/volumes/n8n_data /tmp/n8n.sql
restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
```

## 3. Schedule it
Add a cron / systemd-timer (or an n8n workflow!) to run step 2 nightly and ping **ntfy** on
failure. Example cron:
```
15 3 * * *  /usr/local/bin/aurora-backup.sh   # wraps the restic commands above
```

## 4. Test a restore (do this once, for real)
```sh
restic snapshots
restic restore latest --target /tmp/restore-test
# verify n8n.sql restores into a throwaway Postgres, and volume files look right
```

## 5. Whole-box snapshots (Hetzner)
- Take a snapshot before risky changes (Claude can do this via the Hetzner MCP).
- Snapshots live in the same Project — they cover "I broke the box", not "the region/provider
  is gone". restic-to-R2 covers the latter. Keep both.

## Recovery drill
Lost the box entirely? `terraform apply` a fresh one (cloud-init re-hardens it) →
reinstall Dokploy → `restic restore` the volumes + import the `pg_dump` → redeploy stacks.
Because everything is code + off-box data, this is minutes-to-an-hour, not a rebuild.
