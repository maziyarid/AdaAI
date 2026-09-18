# ADR 0003 — Agiflow is the coordination projection, not the runtime authority

Status: superseding current contract  
Date: 2026-09-17  
Tasks: AAX-6, AAX-12

## Context

The durable MariaDB control core remains the authoritative runtime for jobs, schedules, leases, retries, heartbeats and execution evidence. Agiflow is the shared coordination and audit surface used by Maziyar, ChatGPT, Mistral and Grok.

An earlier Phase-1 decision retained `CLICKUP_STATE_STEWARD` as the existing projection and deferred an Agiflow steward. That decision is now superseded for **new execution and coordination** by Maziyar's explicit control-plane directive: ClickUp is legacy/migration context only; normal execution must not depend on ClickUp synchronisation.

This does **not** make Agiflow a scheduler or a second runtime database.

## Decision

Use non-overlapping ownership:

| Surface | Owns | Does not own |
|---|---|---|
| GitHub (`maziyarid/AdaAI`) | Source, tests, ADRs, SQL, runbooks, PR evidence | Live runtime job/schedule/lease state |
| MariaDB control core / durable VPS state | Jobs, schedules/recipes, leases, heartbeats, retries, DLQ/quarantine, runtime evidence, external-sync outbox | Human planning and editorial/project discussion |
| Agiflow | Shared coordination/audit projection: projects, tasks, blockers, dependencies, meaningful state transitions, evidence-linked comments/handoffs | Scheduler truth, lease ownership, WordPress state, passports or direct runtime authority |
| ClickUp | Legacy migration/history input only while unresolved state is reconciled | Required state for new execution, new completion tracking or canonical runtime truth |

## Agiflow state steward

AAX-12 implements an `AGIFLOW_STATE_STEWARD` / projection bridge with these constraints:

1. It projects **meaningful coordination state only**: task mapping, status transitions, evidence comments, blockers and handoffs.
2. It does **not** write or own runtime `jobs`, `schedules`, leases or heartbeats.
3. It is idempotent and version/conflict aware; newer human edits must not be silently overwritten.
4. It uses stable mappings between durable job/task IDs and Agiflow project/task IDs.
5. If Agiflow is unavailable, authorised runtime work may continue. A durable `pending_external_sync`/outbox record may preserve the projection attempt for later idempotent replay.
6. Replay must not duplicate comments, tasks or transitions.
7. Completion projected to Agiflow must be backed by live/runtime evidence; a model assertion is insufficient.
8. Agiflow remote-execution allowance is not the normal runtime. Normal execution remains on Maziyar's VPS/control plane.

## ClickUp transition

1. `CLICKUP_STATE_STEWARD`, if still present in the live control core, is a **legacy compatibility/migration component**, not a required dependency for new Mistral execution.
2. Do not create new ClickUp-only tasks, blockers or completion dependencies.
3. Existing unresolved ClickUp `pending_external_sync` records are reconciled individually and may be migrated, explicitly resolved or quarantined.
4. Retire/disable the legacy ClickUp steward only after the replacement coordination path has passed canary, conflict, outage/replay and rollback tests.
5. Historical ClickUp evidence may remain readable for provenance after runtime dependency is removed.

## Conflict / failure behaviour

- Runtime vs Agiflow disagreement about jobs/schedules/leases/heartbeat → durable runtime state wins; Agiflow is corrected with evidence.
- Agiflow vs GitHub disagreement about code → GitHub wins for source/test state.
- ClickUp vs Agiflow disagreement → ClickUp is legacy context only; inspect current durable/live state and current explicit policy, then reconcile without blind auto-merge.
- Agiflow unavailable → continue safe authorised runtime execution, persist pending projection if needed, replay idempotently later.
- Projection failure must not stop unrelated runtime work.

## Consequences

- AAX-6 is the architecture-decision task and can close once this superseding contract is recorded.
- AAX-12 is the implementation task for the Agiflow coordination/state-steward projection.
- In-repo implementation: `ada-reliability/src/ada_reliability/agiflow_steward.py` (projection + outbox + FakeAgiflow). Additive SQL: `ada-reliability/sql/mariadb/005_ada_agiflow_projection.sql`. Live VPS wiring remains AAX-3/AAX-12 canary, not this ADR.
- MariaDB/control-core remains runtime truth.
- ClickUp is no longer required for new Mistral execution or completion tracking.
- Agiflow becomes the common coordination surface without becoming a second scheduler or runtime authority.
