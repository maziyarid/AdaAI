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

## Live source reconciliation (AAX-7, SQL not applied)

Captured 2026-09-19 from `control_core.py` on `server.maziyarid.com`
(65370 bytes / 1096 lines). This is source schema, **not** a live
`SHOW TABLES` dump.

### Already in live control-core source

`schema_migrations`, `agent_events`, `canonical_tasks`, `jobs`,
`job_results`, `schedules`, `dead_letter_queue`, `service_health`,
`operator_reachability`, `operator_state`, `cache_manifest`,
`harvest_provider_state`, `tool_harvest_queue`, `data_snapshots`,
`intelligence_findings`, `forecasts`, `content_gate_states`,
`green_buffers`, `pending_external_sync` (with `locked_by` /
`lease_until`), `audit_log`.

No `ada_*` names. No `pd_worker_runs`. No `pd_outbox`.

### Separate live artefacts (AAX-12 / AAX-15 canaries)

Prior VPS canaries used `pd_worker_runs` and `pd_outbox`. Those names
are **not** defined in `control_core.py`. Do not invent a second
runtime outbox. Reconcile `pd_*` against `006_ada_failed_runs` before
any apply: `006` is Ada execution-recovery, distinct from both live
`pending_external_sync` and AAX-12 `ada_agiflow_outbox`.

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

## What this branch has not done

- Did not connect to production MariaDB / did not `SHOW TABLES`.
- Did not apply any `ada_*` SQL.
- Did not run a live Teznevise / WordPress write canary.
