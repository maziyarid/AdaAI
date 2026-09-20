# Phase-1 MariaDB migration runbook

This is additive. It must not destroy existing control-core tables.

## Preconditions (stop if any fail)

1. Encrypted MariaDB backup completed and checksummed (procedure:
   `docs/AAX7-BACKUP-CHECKPOINT.md`; production dump is **not** done
   from this branch).

2. Off-host copy confirmed.
3. Restore drill into a throwaway schema succeeded (see ROLLBACK-RUNBOOK.md).
4. `maziyar-control-core.service` is healthy on 127.0.0.1:8770.
5. Diff of SQL reviewed: additive `CREATE TABLE IF NOT EXISTS ada_*` plus the single bootstrap `INSERT IGNORE` of `('global','*',1)` in `001_ada_memory.sql`. No `DROP`/`ALTER` of existing control-core tables. Stop if the diff contains anything else.
6. Production cutover approval recorded (human, not the proposing model).
7. **Live durability reconciliation complete across every runtime store.**
   Stop before any Apply step, including `006_ada_failed_run_outbox.sql`.
   Live MariaDB has no `pd_*`, but the active recovery authority is SQLite:
   `/srv/maziyar-wp-mcp/state/factory.sqlite3` contains `pd_worker_runs` and
   `pd_outbox`. `pd_outbox` overlaps 006 failure, retry, lease, idempotency
   and external-sync responsibilities. **006 HOLD:** do not create
   `ada_failed_runs` while this SQLite outbox remains active. First
   map/migrate/retire one authority and prove exactly one runtime recovery
   outbox remains.

## Live source reconciliation (AAX-7, STOP before Apply)

Captured 2026-09-19 from `control_core.py` on `server.maziyarid.com`
(65370 bytes / 1096 lines; snapshot
`runtime/control-core-baseline/live/control_core.py`, captured-bytes
sha256 `aec6639acf761dfb01a72feb670b4d841c25fb1e8000abdea41bca0dcf4a94f3`).
This is **source schema**, not a live `SHOW TABLES` dump. Live table
presence still needs `ada-inspect` (not installed) or an approved
schema-only MariaDB read.

Do **not** run the Apply section until this stop is complete.

An isolated **inventory** rehearsal of `001`–`006` exists in
`ada-reliability/tests/test_aax7_isolated_rehearsal.py`. It mutates an
in-memory table-name set only. It is not MariaDB, not `SHOW TABLES`,
and not production Apply.

### Already in live control-core source

`schema_migrations`, `agent_events`, `canonical_tasks`, `jobs`,
`job_results`, `schedules`, `dead_letter_queue`, `service_health`,
`operator_reachability`, `operator_state`, `cache_manifest`,
`harvest_provider_state`, `tool_harvest_queue`, `data_snapshots`,
`intelligence_findings`, `forecasts`, `content_gate_states`,
`green_buffers`, `pending_external_sync` (with `locked_by` /
`lease_until`), `audit_log`.

No `ada_*` names. No `pd_worker_runs`. No `pd_outbox`.

### Source-table shapes (no row dumps)

**jobs** — runtime work + leases:

- unique `idempotency_key` / `stable_id`
- `locked_by`, `lease_until`
- `ix_jobs_claim (status, available_at, priority, created_at)`
- `ix_jobs_lease (lease_until)`

**schedules** — interval dispatcher (not a second Ada scheduler):

- `interval_seconds`, `enabled`, `next_run_at`, `last_run_at`
- `uq_schedules_stable`

**pending_external_sync** — projection/outage transport:

- unique `stable_id` / `idempotency_key`
- `locked_by`, `lease_until`, `attempts` / `max_attempts`
- `ix_sync_due (status, available_at)`, `ix_sync_lease (lease_until)`
- claim uses `FOR UPDATE SKIP LOCKED`; expired leases return to pending

These are the live durability/state tables. Additive `ada_*` must
not replace them.

### Separate live artefacts (AAX-12 / AAX-15 canaries)

Prior VPS canaries used `pd_worker_runs` and `pd_outbox`. Those names
are **not** defined in `control_core.py`. Do not invent a second
runtime outbox. Reconcile `pd_*` against migration
`006_ada_failed_run_outbox.sql` (table `ada_failed_runs`) before any
apply: `006` is Ada execution-recovery, distinct from both live
`pending_external_sync` and AAX-12 `ada_agiflow_outbox`.

Required live proof still missing (viewer `readOnly` cannot query
MariaDB; `ada-inspect` is not installed):

- `SHOW TABLES` / `SHOW TABLES LIKE 'ada_%'`
- `SHOW TABLES LIKE 'pd_%'`
- `SHOW CREATE TABLE` for `jobs`, `schedules`, `pending_external_sync`
  and, if present, `pd_worker_runs` / `pd_outbox`

### Additive repo tables (not in production source)

- `001` memory: `ada_scope_versions`, `ada_memory_records`,
  `ada_memory_versions`, `ada_project_states`
- `002` receipts: `ada_policy_releases`, `ada_agent_passports`,
  `ada_tool_registry`, `ada_context_receipts`, `ada_receipt_dependencies`
- `003` journal: `ada_approval_tickets`, `ada_approval_events`,
  `ada_snapshots`, `ada_mutation_journal`, `ada_verifications`,
  `ada_external_inputs`
- `004` qalam: `ada_qalam_assets`, `ada_model_registry`,
  `ada_eval_traces`, `ada_mirror_events`, `ada_backup_runs`,
  `ada_audit_events`
- `005` AAX-12 projection: `ada_agiflow_task_map`, `ada_agiflow_outbox`,
  `ada_agiflow_evidence`, `ada_agiflow_close_grants`,
  `ada_agiflow_projection_events`
- `006` AAX-15 recovery: `ada_failed_runs`, `ada_failed_run_events`
  (documents claim / expire / result CAS on `claim_generation`)

`ada-context-core/sql/001_schema.sql` is the older PostgreSQL-shaped
contract. It is **not** the production apply path. Live authority is
MariaDB `control_core.py` + additive `ada-reliability/sql/mariadb/*`.

## Apply (after approval AND after precondition 7)

```bash
# on VPS, as the control-core DB user — example only
# 006 remains HOLD while the active SQLite pd_outbox recovery authority exists.
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
# DO NOT APPLY 006 while /srv/maziyar-wp-mcp/state/factory.sqlite3
# contains the active pd_outbox recovery authority.
# mysql ... < 006_ada_failed_run_outbox.sql   # HOLD
```

Do not restart WordPress MCP, OAuth gateway, GSC MCP, or unrelated units.

Verify:

```sql
SHOW TABLES LIKE 'ada_%';
SELECT scope_type, scope_id, version FROM ada_scope_versions;
```

Existing `jobs` / `schedules` / lease tables must still be readable.

## What this branch has not done

- Did not connect to production MariaDB / did not `SHOW TABLES`.
- Did not apply any `ada_*` SQL.
- Did not run a live Teznevise / WordPress write canary.

## 2026-09-19 authoritative cross-store reconciliation

Approved `ada-inspect` live reads now supersede the earlier discovery blocker. Production control-core MariaDB has exactly the expected 20 control-core tables, with no `ada_*` and no `pd_*`. Schema-only metadata was captured for jobs, schedules, dead_letter_queue, pending_external_sync, job_results, and schema_migrations; no rows or secrets were dumped.

The prior AAX-15 `pd_worker_runs` / `pd_outbox` canary was also real, but those tables are in SQLite at `/srv/maziyar-wp-mcp/state/factory.sqlite3`, created/used by `/srv/maziyar-wp-mcp/deploy/run_ledger_outbox.py`. `pd_outbox` already owns idempotency, failure class/reason, attempts/max-attempts, retry eligibility, reset condition, leases, external-sync state, and terminal lifecycle. This materially overlaps migration 006. Therefore **006 is HOLD** until the SQLite recovery authority is mapped, migrated, or retired. MariaDB `SHOW TABLES` alone is not a sufficient 006 safety check.

Production SQL remains NONE.

## AAX-15 single-authority cutover gate for migration 006

Migration 006 remains **HOLD**. MariaDB `ada_failed_runs` is the future execution-recovery authority, while SQLite `pd_outbox` remains authoritative until a quiescent, approved switch. Dual-write and dual-claim are forbidden.

Before 006 can move from HOLD: satisfy the full encrypted backup plus off-host key/copy gate; identify and quiesce every `pd_outbox` producer and claimer; run `ada-reliability/scripts/aax15_sqlite_cutover_plan.py` against the frozen SQLite database in read-only mode; require zero `queued`, `retryable`, and `inflight` rows; preserve idempotency keys exactly and preserve parked state; apply/import only inside the approved maintenance window; switch the runtime AAX-15 writer/claimer to MariaDB before re-enabling producers; verify source/target counts and digests, replay fencing and outage catch-up; then retain SQLite read-only for historical evidence with no replay writes or claims.

The planner deliberately emits JSON mapping/evidence only. It emits no executable SQL and cannot perform the cutover.

For any replayable `agiflow_sync` row, a durable control-core job binding is mandatory. The planner preserves `payload_json.durable_job_id` when present or accepts an explicit `--job-binding STABLE_ID=DURABLE_JOB_ID`. If a replayable row has neither, `cutover_ready_for_approved_maintenance_window` is false. Never invent a job ID from task names, run IDs, or Agiflow IDs.
A legacy Agiflow row that has already been durably handed off to control-core pending_external_sync is a different case, but caller-supplied text is never sufficient proof. The delegation tuple must bind the legacy stable ID, exact idempotency key and independent control-core record ID, and --control-core-catalog must point to a fresh HMAC-SHA256 signed envelope issued by maziyar-control-core from pending_external_sync. The planner trusts only key ID aax15-control-core-catalog-v1 and the fixed root-owned verification key path /etc/maziyar-control-core/aax15-external-sync-catalog.key; there is no CLI option to substitute another verification key. Catalog validity is capped at 15 minutes with a 30-second future-clock-skew allowance. The signed record must bind the exact external stable ID, idempotency key, durable status, target service, entity type and operation. Only after this verification does the planner derive an immutable verified handle and preserve the legacy row as parked historical evidence with mutation_kind=none while control-core external-sync remains the sole delivery authority. Never provide both a durable job binding and an external-sync delegation for one row. The repository contains no catalog HMAC secret, and migration 006 remains HOLD until a trusted fresh export and all other Apply gates exist.

Legacy SQLite external_sync_state strings can exceed migration 006 VARCHAR(32). The planner normalises known long markers into bounded target values and preserves the complete original marker in _legacy_pd_outbox.external_sync_state inside JSON payload evidence.