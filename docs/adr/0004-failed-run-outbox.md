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
