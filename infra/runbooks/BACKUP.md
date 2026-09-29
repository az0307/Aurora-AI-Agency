# Backup + disaster-recovery runbook

Two layers: **restic** (encrypted, off-box, granular) + **Hetzner snapshots** (fast,
whole-box). A backup you haven't restored is a hope, not a backup — run the restore drill.

## What gets backed up
`aurora maintain backup` (nightly, 03:30) writes `/var/backups/aurora/<date>/`, root-only, 7 kept:
- `n8n-postgres.sql.gz`: a proper `pg_dump` of n8n's database.
- `vol-<name>.tgz`: every other stack volume (each stack paused for a few seconds).
- `configs.tgz`: `secrets.env`, every stack `.env`, Hermes data, Tailscale state.

`aurora maintain offsite` then pushes that folder to **Cloudflare R2** with restic,
encrypted on the box before upload. It keeps 7 daily, 4 weekly and 6 monthly snapshots.
The timer runs both steps as `aurora maintain nightly`.

Also keep the **n8n encryption key** (`N8N_ENCRYPTION_KEY`) and `RESTIC_PASSWORD` in
Bitwarden. Losing `RESTIC_PASSWORD` makes every off-box snapshot unreadable.

## 1. One-time setup (R2)
1. Cloudflare dashboard → **R2** → Create bucket `aurora-backups` (location: automatic).
2. R2 → **Manage API tokens** → Create token → **Object Read & Write**, scoped to that bucket
   only. Copy the Access Key ID and Secret Access Key. The account ID is on the R2 overview page.
3. Make the restic password: `openssl rand -base64 32`. Save it in Bitwarden **first**.
4. On the phone, fill these in `secrets.env` (KEYS.md §5), then `./bootstrap.sh --ship-only`:
   `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `RESTIC_PASSWORD`
   (optional `R2_BUCKET`, default `aurora-backups`).
5. On the box: `aurora maintain tune` (installs restic, points the timer at `nightly`), then
   `aurora maintain backup && aurora maintain offsite`. The first run initialises the repo at
   `s3:https://<account>.r2.cloudflarestorage.com/aurora-backups/<hostname>`.

Keys stay in `/opt/aurora/secrets.env` (mode 600). They reach restic only through its
environment, never its command line, and are never printed.

## 2. Check it
- `aurora maintain report` shows `Off-box (R2): ok <time>` or `FAILED <time> <step>`.
- A failed run exits non-zero (so `systemctl status aurora-backup` shows it) and pushes an
  ntfy alert to `http://127.0.0.1:8888/aurora-backups` when the monitoring stack runs.
  Subscribe to that topic in the ntfy app.
- Without R2 keys, `offsite` prints a warning and skips; the local backup still runs.

## 3. Restore test (monthly, one command)
```sh
aurora maintain restore-test
```
It runs `restic check`, restores the newest snapshot to a temp dir, checks `configs.tgz`
lists and the n8n dump is valid gzip, then deletes the temp dir. Local test of this whole flow:
`sudo bash infra/server/test-offsite.sh` (uses a local repo, no R2 needed).

## 4. Real restore (box lost or data broken)
Load the keys, then restore to a folder:
```sh
sudo -i
set -a; . /opt/aurora/secrets.env; set +a
export RESTIC_REPOSITORY="s3:https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com/${R2_BUCKET:-aurora-backups}/aurora-01"
export AWS_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID" AWS_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY" AWS_DEFAULT_REGION=auto
restic snapshots --tag aurora
restic restore latest --tag aurora --target /tmp/restore
ls /tmp/restore/var/backups/aurora/          # pick the day you want
```
On a new box, `/opt/aurora/secrets.env` doesn't exist yet: export the same four values by hand.

Then, from that day's folder:
- **n8n database:** start the n8n stack's Postgres only, then
  `gunzip -c n8n-postgres.sql.gz | docker exec -i <postgres-container> psql -U n8n n8n`.
- **Volumes:** `docker run --rm -v <volume>:/v -v "$PWD":/b alpine:3.20 tar -C /v -xzf /b/vol-<volume>.tgz`
  with the stack stopped.
- **Configs:** `tar -C /opt/aurora -xzf configs.tgz` restores `secrets.env`, `.env` files, Hermes
  data and Tailscale state.

Validate the dump in a throwaway Postgres first if unsure:
```sh
docker run -d --name pg-restore-test -e POSTGRES_PASSWORD=test postgres:16-alpine; sleep 5
docker exec -i pg-restore-test psql -U postgres -c 'CREATE DATABASE n8n;'
gunzip -c n8n-postgres.sql.gz | docker exec -i pg-restore-test psql -U postgres n8n >/dev/null
docker exec pg-restore-test psql -U postgres n8n -c '\dt' | grep -qi workflow_entity && echo "RESTORE OK"
docker rm -f pg-restore-test
```

## 5. Whole-box snapshots (Hetzner)
- Take a snapshot before risky changes (Claude can do this via the Hetzner MCP).
- Snapshots live in the same Project — they cover "I broke the box", not "the region/provider
  is gone". restic-to-R2 covers the latter. Keep both.

## Recovery drill
Lost the box entirely? `terraform apply` a fresh one (cloud-init re-hardens it) →
`./bootstrap.sh --ship-only` → §4 above (restore configs, volumes, `pg_dump`) → `stacks-up.sh` each stack.
Because everything is code + off-box data, this is minutes-to-an-hour, not a rebuild.
