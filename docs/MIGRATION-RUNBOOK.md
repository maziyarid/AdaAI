# Phase-1 MariaDB migration runbook

This is additive. It must not destroy existing control-core tables.

## Preconditions (stop if any fail)

1. Encrypted MariaDB backup completed and checksummed.
2. Off-host copy confirmed.
3. Restore drill into a throwaway schema succeeded (see ROLLBACK-RUNBOOK.md).
4. `maziyar-control-core.service` is healthy on 127.0.0.1:8770.
5. Diff of SQL reviewed: additive `CREATE TABLE IF NOT EXISTS ada_*` plus the single bootstrap `INSERT IGNORE` of `('global','*',1)` in `001_ada_memory.sql`. No `DROP`/`ALTER` of existing control-core tables. Stop if the diff contains anything else.
6. Production cutover approval recorded (human, not the proposing model).

## Apply (after approval)

```bash
# on VPS, as the control-core DB user — example only
mysql --defaults-file=/etc/ada/mysql.cnf control_core \
  < /srv/ada/ada-reliability/sql/mariadb/001_ada_memory.sql
mysql --defaults-file=/etc/ada/mysql.cnf control_core \
  < /srv/ada/ada-reliability/sql/mariadb/002_ada_receipts_passports.sql
mysql --defaults-file=/etc/ada/mysql.cnf control_core \
  < /srv/ada/ada-reliability/sql/mariadb/003_ada_approvals_journal.sql
mysql --defaults-file=/etc/ada/mysql.cnf control_core \
  < /srv/ada/ada-reliability/sql/mariadb/004_ada_qalam_eval.sql
mysql --defaults-file=/etc/ada/mysql.cnf control_core \
  < /srv/ada/ada-reliability/sql/mariadb/005_ada_agiflow_projection.sql
mysql --defaults-file=/etc/ada/mysql.cnf control_core \
  < /srv/ada/ada-reliability/sql/mariadb/006_ada_failed_run_outbox.sql
```

Do not restart WordPress MCP, OAuth gateway, GSC MCP, or unrelated units.

Verify:

```sql
SHOW TABLES LIKE 'ada_%';
SELECT scope_type, scope_id, version FROM ada_scope_versions;
```

Existing `jobs` / `schedules` / lease tables must still be readable.

## What this session did not do

- Did not connect to production MariaDB.
- Did not import `/opt/maziyar-control-core` from this session (no SSH here).
- Did not run a live canary.
