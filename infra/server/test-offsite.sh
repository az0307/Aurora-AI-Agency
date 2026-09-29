#!/usr/bin/env bash
# test-offsite.sh — local test for `maintain.sh offsite` + `restore-test` (T009).
#
#   bash infra/server/test-offsite.sh
#
# Needs restic on PATH. Runs as root (like the systemd timer) against a throwaway ROOT,
# BACKUP_DIR and a LOCAL restic repo (AURORA_RESTIC_REPO) instead of Cloudflare R2, so it
# needs no network and no real keys. Exits non-zero on the first failed check.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
MAINTAIN="$HERE/maintain.sh"
command -v restic >/dev/null || { echo "SKIP: restic not installed"; exit 0; }
[ "$(id -u)" = 0 ] || { echo "run as root (sudo bash $0)"; exit 2; }

T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
pass=0
ok()   { pass=$((pass + 1)); printf '  ok  %s\n' "$*"; }
fail() { printf '  FAIL %s\n' "$*"; exit 1; }

mkdir -p "$T/root" "$T/backups/2026-09-28" "$T/backups/2026-09-29"
# A fake nightly backup: a real gzip "dump" and a real tarball, like backup() writes.
echo "-- fake pg_dump" | gzip > "$T/backups/2026-09-29/n8n-postgres.sql.gz"
tar -C "$T/root" -czf "$T/backups/2026-09-29/configs.tgz" --files-from /dev/null
echo "old" | gzip > "$T/backups/2026-09-28/n8n-postgres.sql.gz"

run() { AURORA_ROOT="$T/root" AURORA_BACKUP_DIR="$T/backups" AURORA_RESTIC_REPO="$T/repo" \
        AURORA_NTFY_URL="http://127.0.0.1:9/none" bash "$MAINTAIN" "$@"; }

echo "1. no keys in secrets.env -> offsite skips cleanly (exit 0, no repo)"
: > "$T/root/secrets.env"
out=$(run offsite 2>&1) || fail "offsite exited non-zero without keys: $out"
grep -q "skipped" <<<"$out" || fail "no 'skipped' message: $out"
[ ! -e "$T/repo" ] || fail "repo created without keys"
ok "skips without keys"

echo "2. keys set -> offsite inits repo and uploads the latest backup"
printf '%s\n' "RESTIC_PASSWORD=test-pass-123" "R2_ACCOUNT_ID=acct" \
  "R2_ACCESS_KEY_ID=akid" "R2_SECRET_ACCESS_KEY=secret" > "$T/root/secrets.env"
chmod 600 "$T/root/secrets.env"
out=$(run offsite 2>&1) || fail "offsite failed: $out"
n=$(RESTIC_PASSWORD=test-pass-123 restic -r "$T/repo" snapshots --json | jq length)
[ "$n" = 1 ] || fail "expected 1 snapshot, got $n"
grep -q '^ok ' "$T/backups/.offsite-last" || fail ".offsite-last not ok: $(cat "$T/backups/.offsite-last")"
ok "snapshot uploaded, status file ok"

echo "3. secrets never appear in output"
for s in test-pass-123 akid secret; do grep -q "$s" <<<"$out" && fail "output leaked '$s'"; done
ok "no secret values printed"

echo "4. second run is idempotent (no re-init, 2 snapshots)"
run offsite >/dev/null 2>&1 || fail "second offsite failed"
n=$(RESTIC_PASSWORD=test-pass-123 restic -r "$T/repo" snapshots --json | jq length)
[ "$n" = 2 ] || fail "expected 2 snapshots, got $n"
ok "re-run adds a snapshot"

echo "5. restore-test restores the latest snapshot and validates the dump"
out=$(run restore-test 2>&1) || fail "restore-test failed: $out"
grep -q "Restore test passed" <<<"$out" || fail "no pass message: $out"
ok "restore-test passes"

echo "6. restore-test fails on a broken dump"
echo "not gzip" > "$T/backups/2026-09-29/n8n-postgres.sql.gz"
run offsite >/dev/null 2>&1 || fail "offsite failed"
if run restore-test >/dev/null 2>&1; then fail "restore-test passed on a corrupt dump"; fi
ok "restore-test catches a corrupt dump"

echo "7. wrong password -> offsite fails and records it"
sed -i 's/^RESTIC_PASSWORD=.*/RESTIC_PASSWORD=wrong/' "$T/root/secrets.env"
if run offsite >/dev/null 2>&1; then fail "offsite passed with a wrong password"; fi
grep -q '^FAILED ' "$T/backups/.offsite-last" || fail ".offsite-last not FAILED"
ok "failure is non-zero and recorded"

echo "8. secrets.env written the way bootstrap.sh writes it (printf %q) with base64-style chars"
rm -rf "$T/repo"; pw='a/b+c=d e$f'
{ for kv in "RESTIC_PASSWORD=$pw" R2_ACCOUNT_ID=acct R2_ACCESS_KEY_ID=akid R2_SECRET_ACCESS_KEY=secret; do
    printf '%s=%q\n' "${kv%%=*}" "${kv#*=}"; done; } > "$T/root/secrets.env"
run offsite >/dev/null 2>&1 || fail "offsite failed with a %q-quoted password"
RESTIC_PASSWORD="$pw" restic -r "$T/repo" snapshots -q >/dev/null || fail "repo not readable with the real password"
ok "%q-quoted secrets load correctly"

echo "All $pass checks passed."
