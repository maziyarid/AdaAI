# MariaDB 10.11 dialect review — Phase 1 `ada_*` SQL

Status: document-only review. **Not applied to production.** No backup/restore drill has been executed.

Reviewed files:

- `ada-reliability/sql/mariadb/001_ada_memory.sql`
- `ada-reliability/sql/mariadb/002_ada_receipts_passports.sql`
- `ada-reliability/sql/mariadb/003_ada_approvals_journal.sql`
- `ada-reliability/sql/mariadb/004_ada_qalam_eval.sql`
- `ada-reliability/sql/mariadb/005_ada_agiflow_projection.sql`

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
- `ada_policy_releases.active_component` VIRTUAL generated column + UNIQUE (MariaDB 10.2+; multiple NULLs allowed, so only one ACTIVE row per component)
- `ada_qalam_assets.path_hash CHAR(64)` primary-key component (full-path SHA-256) instead of unique `path(191)` prefix
- `ada_agiflow_task_map` / `ada_agiflow_outbox` / `ada_agiflow_evidence` / `ada_agiflow_close_grants` / `ada_agiflow_projection_events` — projection only; unique durable_job_id and outbox idempotency_key; HMAC-SHA256 signatures on issued evidence and close grants (`CHAR(64)`); no jobs/schedules tables

## Intentional absences (do not add)

- No `pgcrypto`, `jsonb`, `plpgsql`, or PostgreSQL `UUID` type
- No `DROP TABLE` / `ALTER` of existing control-core tables
- No second scheduler schema

## Risks before apply

1. Live table names for jobs/schedules/leases are **not** captured from the host. Confirm no existing `ada_*` tables before apply.
2. JSON columns are fine on 10.11; avoid PostgreSQL-only operators in later queries.
3. Apply only after backup + restore drill + human approval (`docs/MIGRATION-RUNBOOK.md`).
4. `path_hash` must be SHA2(path, 256) of the full 512-char path; a prefix unique index is not collision-safe.
5. One-ACTIVE uniqueness relies on the generated `active_component` column. Application code must still SUPERSEDE the previous ACTIVE row before inserting a new ACTIVE row.

## Safest next host step

`mysqldump --no-data` the live control-core schema (no data, no secrets) and diff table names against this prefix plan.
