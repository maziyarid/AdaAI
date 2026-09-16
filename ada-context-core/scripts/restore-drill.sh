#!/usr/bin/env bash
set -euo pipefail
: "${ADA_ADMIN_DATABASE_URL:?required; admin URL able to CREATE/DROP a temporary DB}"
: "${ADA_BACKUP_FILE:?required}"
command -v age >/dev/null
name="ada_restore_verify_$(date -u +%Y%m%d%H%M%S)"
cleanup(){ psql "$ADA_ADMIN_DATABASE_URL" -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS $name;" >/dev/null 2>&1 || true; }
trap cleanup EXIT
psql "$ADA_ADMIN_DATABASE_URL" -v ON_ERROR_STOP=1 -c "CREATE DATABASE $name;"
base=${ADA_ADMIN_DATABASE_URL%/*}
age -d "$ADA_BACKUP_FILE" | gunzip | psql "$base/$name" -v ON_ERROR_STOP=1 >/dev/null
psql "$base/$name" -v ON_ERROR_STOP=1 -c "SELECT count(*) AS memory_records FROM memory_records; SELECT count(*) AS audit_events FROM audit_events;"
echo "restore drill passed: $name"
