# ADR 0004 — Failed-run outbox is execution recovery, not Agiflow projection

Status: accepted for the Phase-1 in-repo contract  
Date: 2026-09-18  
Tasks: AAX-15 (distinct from AAX-12)

## Context

Scheduled workers can fail after a job is already durable in MariaDB control-core: factory packet missing, Agiflow down, OOM/SIGKILL 137, connectivity loss. Chat output and Agiflow comments are not recovery. AAX-12 already has an outbox, but that outbox only replays **coordination projection**.

## Decision

Keep two non-overlapping outboxes:

| Outbox | Owns | Does not own |
|---|---|---|
| AAX-12 `ada_agiflow_outbox` | Agiflow task/comment/status projection when Agiflow is down | Jobs, schedules, leases, WordPress, packet ACK, failed-run evidence |
| AAX-15 `ada_failed_runs` | Failed/blocked/coordination-pending *executions*: identity, failure class, attempts, eligibility, external-sync state | Scheduling, leasing, applying production mutations, forging Agiflow Review/Done |

Workers may report `replay=queued|parked|retryable` only after durable persist succeeds. Otherwise `replay=UNAVAILABLE`. Deterministic blockers park and do not hot-loop. Replay is bounded, idempotent, ordered, and lease-aware. WordPress and packet ACK retry through AdaEngine under the same mutation idempotency key. Agiflow catch-up calls AAX-12 `project(evidence_id=..., close_grant_id=...)`.

This is not a second scheduler. Control-core jobs/schedules/leases remain runtime truth.

## Consequences

- In-repo tests prove the state machine. They do not prove production MariaDB.
- Live VPS currently also has `pd_worker_runs` / `pd_outbox`. Reconcile names before applying `006_ada_failed_run_outbox.sql`.
- AAX-12 HMAC evidence rules are unchanged.

## 2026-09-19 authority cutover clarification

The live AAX-15 recovery implementation is currently `/srv/maziyar-wp-mcp/state/factory.sqlite3` with `pd_worker_runs` and `pd_outbox`. It is active state, not a disposable test artefact. `pd_outbox` overlaps the proposed MariaDB `ada_failed_runs` responsibility.

**Decision:** control-core MariaDB `ada_failed_runs` / `ada_failed_run_events` is the future AAX-15 execution-recovery authority, but SQLite `pd_outbox` remains authoritative until an explicitly approved quiescent cutover. There is no dual-write or dual-claim phase.

The cutover sequence is: quiesce every SQLite producer/claimer; run the read-only deterministic `ada-reliability/scripts/aax15_sqlite_cutover_plan.py`; refuse the cutover while any `queued`, `retryable`, or `inflight` row exists; preserve idempotency keys exactly and keep parked rows parked; satisfy the encrypted/off-host backup gate; apply/import in one controlled maintenance transaction; switch the runtime writer/claimer to MariaDB before re-enabling producers; verify counts/digests, fencing and outage replay; then retain SQLite read-only as historical evidence only.

`pd_worker_runs` remains historical run evidence after cutover and must not become a second replay authority. Successful-run history does not need to be copied into `ada_failed_runs`, whose scope is failed/pending execution recovery.

Current live planning snapshot on 2026-09-19: 10 `succeeded`, 1 `parked`, zero observed `retryable`/`inflight` rows. This is favourable for planning but is not an Apply grant; it must be rechecked immediately before an approved cutover.
