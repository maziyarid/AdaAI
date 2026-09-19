# AAX-7 source-vs-migration reconciliation (STOP before Apply)

Captured 2026-09-19T07:05Z against PR head `d7e41a6`.
Isolated inventory rehearsal added 2026-09-19T09:00Z against
`27ffc51` source + repo SQL (in-memory table names only).
Isolated **MariaDB** rehearsal added 2026-09-19T09:16Z (disposable
skip-networking 10.11.11 instance; not VPS SHOW TABLES).

The original reconciliation began from the captured live source schema. It has now been superseded by direct production table/schema metadata captured with ada-inspect. Production SQL is still not authorised by this document.

Current live reconciliation — 2026-09-19

ada-inspect tables has now run on server.maziyarid.com. Production MariaDB has
the expected 20 control-core tables and no ada_* / pd_* tables. The active
pd_worker_runs / pd_outbox recovery store is separate SQLite and is recorded in
docs/AAX7-LIVE-RECOVERY-STORES.json.

Rule: models propose. Deterministic code authorizes. Independent
validators prove the live result.

## Decision (not executed)

Live MariaDB contains no ada_* or pd_* tables, but the active AAX-15 recovery authority is the separate SQLite pd_worker_runs/pd_outbox store. Therefore migrations 001-005 remain additive candidates, while migration 006 is OVERLAP / HOLD until the SQLite recovery authority is explicitly mapped, migrated, or retired. Do not run two recovery outboxes. Human approval remains required before any production Apply.

## Isolated inventory rehearsal (not production, not MariaDB)

In-process apply of `001`–`006` against the live **source** table
inventory:

- starting set = 20 control-core tables from `SCHEMA`
- apply adds only `ada_*` names (28 tables)
- protected `jobs` / `schedules` / `job_results` / `dead_letter_queue`
  / `pending_external_sync` / `audit_log` are unchanged
- no `DROP TABLE`, no `ALTER` of live names, no `INSERT` into live names
- rollback = drop `ada_*` names only; starting set restored
- `pd_worker_runs` / `pd_outbox` remain unknown (not in source)

This rehearsal does **not** execute SQL, does **not** open MariaDB,
and does **not** satisfy AAX-3 AC3.

## Isolated MariaDB rehearsal (not production)

Initially executed on disposable MariaDB **10.11.11** and repeated after live reconciliation on disposable MariaDB **10.11.19**, always with --skip-networking and socket/datadir/PID under /tmp. Driver: ada-reliability/scripts/isolated_mariadb_rehearsal.py. Evidence JSON: docs/AAX7-ISOLATED-MARIADB-REHEARSAL.json.

This is **not** `server.maziyarid.com`. This is **not** `maziyar_control`.
`skip_networking=ON` was required before any SQL. Production env files
were not read.

Proven on this isolated schema:

1. Pre-migration checkpoint: 20 live-source tables, protected CREATE
   SQL sha256, jobs/schedules/pending_external_sync row counts.
2. Migrations `001`–`006` applied in order, then re-applied
   (`IF NOT EXISTS` / `INSERT IGNORE` idempotent).
3. MariaDB syntax: `release` is reserved; `002` / `004` now quote
   `` `release` ``. Unquoted form is not MariaDB-safe.
4. Unique constraints: duplicate `jobs.idempotency_key` → 1062;
   one-ACTIVE `ada_policy_releases` → 1062;
   `ada_failed_runs.idempotency_key` → 1062.
5. Lease/CAS: first `claim_generation` UPDATE row_count=1;
   stale generation 0 after claim row_count=0.
6. Protected CREATE SQL and job/schedule/sync row counts unchanged
   after apply.
7. 28 `ada_*` tables created; none existed before apply.
8. Rollback dropped only `ada_*`; baseline 20-table set restored;
   protected CREATE hashes matched the checkpoint.
9. Isolated database dropped at end. Production SQL: **NONE**.

Still not proven/executed by this rehearsal:

- encrypted production backup + restore drill (AAX-7 AC1)
- production Apply
- migration 006 retirement/mapping decision against the active SQLite pd_outbox; 006 remains HOLD

The repeated 10.11.19 rehearsal additionally exercises the existing control-core
transition semantics on disposable rows before and after migrations 001-006:
schedule-release idempotency, job claim/lease, expired-lease reclaim, first
retry, terminal DLQ, and retry-from-DLQ. The normalized before/after results are
identical (control_core_behavior_equivalent=true), and each probe restores the
protected-table baseline. This evidences AAX-7 AC3 without running the
production worker loop.

## Responsibility map

| Responsibility | Live control-core source | Repo Ada | Class |
| --- | --- | --- | --- |
| persistence | `jobs` unique `idempotency_key` | none (must not create `jobs`) | already provided live |
| failure records | `job_results` + `dead_letter_queue` | `006` `ada_failed_runs` | complementary **if** live has no `pd_outbox`; overlapping **if** it does |
| leases | `jobs.locked_by` / `lease_until`; `pending_external_sync` lease | `006` recovery lease is not a job lease | already provided live (jobs); complementary (006 recovery CAS) |
| claim generation | `jobs` `FOR UPDATE SKIP LOCKED` | `006` `claim_generation` CAS | already provided live (jobs); complementary (006) |
| retry | `jobs.attempts` / `max_attempts` | `006` `attempt_count` / `next_retry_at` | already provided live (jobs); complementary (006) |
| idempotency | `jobs.idempotency_key`; `pending_external_sync.idempotency_key` | `006` / `005` unique idempotency keys | already provided live; complementary (Ada keys) |
| dead-letter | `dead_letter_queue` unique per job | `006` `lifecycle=dead_letter` | already provided live; complementary (Ada recovery) |
| quarantine | `dead_letter_queue.quarantined_at`; sync `status=quarantined` | `006` `lifecycle=quarantined` | already provided live; complementary (Ada recovery) |
| external sync | `pending_external_sync` unique idempotency + lease | none (must not replace it) | already provided live |
| Agiflow handoff | live `agiflow_outbox_bridge.py` + `pending_external_sync` | `005` `ada_agiflow_*` | complementary projection, not a scheduler |
| Job persistence | `jobs` unique `idempotency_key`, status/priority/attempts | none (must not create `jobs`) | already provided live |
| Schedule dispatch | `schedules` + `release_due_schedules` INSERT IGNORE | none | already provided live |
| Memory/receipts/passports | not in this source | `001`–`004` `ada_*` | still missing live (source); confirm with SHOW TABLES |
| Audit | `audit_log` | journal tables in `003` | complementary (Ada mutation journal ≠ control-core audit) |
| conflict | none identified in source vs `ada_*` names | — | conflict: none in source (pd_* unknown until SHOW TABLES) |

## 006 specifically

Migration file: `ada-reliability/sql/mariadb/006_ada_failed_run_outbox.sql`
Table: `ada_failed_runs` (+ `ada_failed_run_events`)

006 must not:

- create `jobs` / `schedules`
- replace `pending_external_sync`
- become a second scheduler or lease authority for control-core jobs

006 may exist beside live job durability as **Ada execution recovery**
only after live `pd_worker_runs` / `pd_outbox` presence is known.

## Still required before Apply

1. Encrypted production backup + restore drill (command plan:
   docs/AAX7-BACKUP-CHECKPOINT.md; production dump not executed).
2. Resolve the migration-006 HOLD: map/migrate/retire the active SQLite
   recovery authority before any MariaDB ada_failed_runs runtime is enabled.
3. Human approval for any production Apply.

Production SQL this session: **NONE**.

## 2026-09-19 live cross-store decision

Actual production metadata is now known. MariaDB has the expected 20 control-core tables and no `ada_*` / `pd_*`. The active AAX-15 recovery store is separate SQLite `/srv/maziyar-wp-mcp/state/factory.sqlite3` with `pd_worker_runs` and `pd_outbox`.

This changes the 006 classification from conditional to **OVERLAP / HOLD**. SQLite `pd_outbox` already provides unique idempotency, failure metadata, retry attempts/eligibility, reset conditions, lease ownership/expiry, external-sync state, and terminal state. `006_ada_failed_run_outbox.sql` would create another recovery authority with materially the same responsibilities. Do not run both. Migrations 001–005 remain additive candidates subject to human approval; 006 requires an explicit map/migrate/retire decision first.

AAX-7 remains Testing. Production SQL remains NONE.

AAX-7 AC3 is now evidenced by the disposable before/after behaviour rehearsal. AAX-7 remains **Testing** because AC1 (encrypted production backup/schema checkpoint plus restore drill) is still open. Production SQL remains **NONE**.
