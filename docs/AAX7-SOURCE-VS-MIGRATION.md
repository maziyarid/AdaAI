# AAX-7 source-vs-migration reconciliation (STOP before Apply)

Captured 2026-09-19T07:05Z against PR head `d7e41a6`.

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

## Responsibility map

| Responsibility | Live control-core source | Repo Ada | Class |
| --- | --- | --- | --- |
| Job persistence | `jobs` unique `idempotency_key`, status/priority/attempts | none (must not create `jobs`) | already provided live |
| Schedule dispatch | `schedules` + `release_due_schedules` INSERT IGNORE | none | already provided live |
| Job lease | `jobs.locked_by` / `lease_until`; claim `FOR UPDATE SKIP LOCKED` | none | already provided live |
| Job retry | `jobs.attempts` / `max_attempts`; finish requeues or DLQ | none | already provided live |
| Dead-letter | `dead_letter_queue` unique per job | none | already provided live |
| External/connector sync | `pending_external_sync` unique idempotency + lease | none | already provided live |
| Agiflow projection | live `agiflow_outbox_bridge.py` + `pending_external_sync` | `005` `ada_agiflow_*` | complementary projection, not a scheduler |
| Execution-failure recovery | not named `ada_failed_runs` / `pd_*` in this source file | `006` `ada_failed_runs` | complementary **if** live has no `pd_outbox`; overlapping **if** it does |
| Memory/receipts/passports | not in this source | `001`–`004` `ada_*` | still missing live (source); confirm with SHOW TABLES |
| Audit | `audit_log` | journal tables in `003` | complementary (Ada mutation journal ≠ control-core audit) |

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
