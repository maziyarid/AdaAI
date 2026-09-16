# Phase-1 rollback runbook

Ada tables are additive. Rollback is drop-`ada_*` plus restore from backup if a later step touched live jobs.

## If only Ada tables were added

```sql
-- review first; this does not touch control-core jobs
SET @tables = (
  SELECT GROUP_CONCAT(table_name)
  FROM information_schema.tables
  WHERE table_schema = DATABASE() AND table_name LIKE 'ada_%'
);
-- then DROP TABLE each ada_* after explicit approval
```

Control-core service should keep running. No need to restore the whole instance if `jobs`/`schedules` were untouched.

## If control-core state was changed

1. Stop only Ada-related workers (not WP MCP).
2. Restore the last encrypted MariaDB backup that passed checksum.
3. Apply binary-log PITR to the restore point recorded in `ada_backup_runs` if configured.
4. Restart `maziyar-control-core.service`.
5. Re-verify `127.0.0.1:8770` health and a known job row.

Do not copy PostgreSQL WAL commands here.

## Restore drill (required before first production apply)

1. Create a temporary schema.
2. Restore the encrypted backup into it.
3. `SELECT COUNT(*)` on live control-core job table and `ada_scope_versions` if present.
4. Drop the temporary schema.
5. Record result in `ada_backup_runs` with `backup_kind='RESTORE_DRILL'`.
