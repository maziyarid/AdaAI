# MariaDB 10.11 dialect review — Phase 1 `ada_*` SQL

Status: document-only review. **Not applied to production.** No backup/restore drill has been executed.

Reviewed files:

- `ada-reliability/sql/mariadb/001_ada_memory.sql`
- `ada-reliability/sql/mariadb/002_ada_receipts_passports.sql`
- `ada-reliability/sql/mariadb/003_ada_approvals_journal.sql`
- `ada-reliability/sql/mariadb/004_ada_qalam_eval.sql`

## Compatible with MariaDB 10.11

- `CREATE TABLE IF NOT EXISTS` + `ENGINE=InnoDB`
- `utf8mb4` / `utf8mb4_unicode_ci`
- `TIMESTAMP(6)` + `ON UPDATE CURRENT_TIMESTAMP(6)`
- `JSON` columns (MariaDB 10.2+)
- `CHAR(36)` UUIDs, `CHAR(64)` sha256 hex
- `VARCHAR(191)` keys (safe under `utf8mb4` index limits)
- `INSERT IGNORE` seed of `ada_scope_versions`
- `AUTO_INCREMENT` on event tables
- Prefix `ada_` — does not collide with documented control-core job/schedule/lease tables

## Intentional absences (do not add)

- No `pgcrypto`, `jsonb`, `plpgsql`, or PostgreSQL `UUID` type
- No `DROP TABLE` / `ALTER` of existing control-core tables
- No second scheduler schema

## Risks before apply

1. Live table names for jobs/schedules/leases are **not** captured from the host. Confirm no existing `ada_*` tables before apply.
2. JSON columns are fine on 10.11; avoid PostgreSQL-only operators in later queries.
3. Apply only after backup + restore drill + human approval (`docs/MIGRATION-RUNBOOK.md`).

## Safest next host step

`mysqldump --no-data` the live control-core schema (no data, no secrets) and diff table names against this prefix plan.
