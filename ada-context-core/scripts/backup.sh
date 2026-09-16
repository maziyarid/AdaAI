#!/usr/bin/env bash
set -euo pipefail
: "${ADA_DATABASE_URL:?required}"
: "${ADA_BACKUP_DIR:=/var/backups/ada}"
: "${ADA_BACKUP_AGE_RECIPIENT:?required; use an age public recipient, never a private key here}"
command -v pg_dump >/dev/null
command -v age >/dev/null
mkdir -p "$ADA_BACKUP_DIR"
chmod 700 "$ADA_BACKUP_DIR"
ts=$(date -u +%Y%m%dT%H%M%SZ)
out="$ADA_BACKUP_DIR/ada-$ts.sql.gz.age"
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
pg_dump "$ADA_DATABASE_URL" --format=plain --no-owner --no-privileges | gzip -9 > "$tmp"
age -r "$ADA_BACKUP_AGE_RECIPIENT" -o "$out" "$tmp"
sha256sum "$out" > "$out.sha256"
chmod 600 "$out" "$out.sha256"
echo "$out"
# Off-host replication is mandatory in production. Configure rclone/rsync separately and alert if it fails.
