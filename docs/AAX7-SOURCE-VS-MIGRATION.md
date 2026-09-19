# AAX-7 source-vs-migration reconciliation (STOP before Apply)

Captured 2026-09-19T07:05Z against PR head `d7e41a6`.
Isolated inventory rehearsal added 2026-09-19T09:00Z against
`27ffc51` source + repo SQL (in-memory table names only).

This is **live source schema** from
`runtime/control-core-baseline/live/control_core.py` (65370 bytes).
It is **not** `SHOW TABLES`. AAX-3 AC3 remains open until
`ada-inspect tables` runs. Do **not** apply production SQL from this
document.

Rule: models propose. Deterministic code authorizes. Independent
validators prove the live result.

## Decision (not executed)

Retain additive repo migrations as complementary **if** live MariaDB
has no `pd_worker_runs` / `pd_outbox` / `ada_*`. If those tables exist
live, stop and remap 006 rather than creating a second recovery
outbox. Human approval still required before Apply.

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

1. `ada-inspect tables` → live `ada_%` / `pd_%` names
2. `ada-inspect create jobs` / `schedules` / `pending_external_sync`
3. If present, `ada-inspect create pd_worker_runs` / `pd_outbox`
4. Encrypted backup + restore drill
5. Human approval

Production SQL this session: **NONE**.
