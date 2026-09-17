# ADR 0003 — Agiflow is the execution board, not a second runtime authority

Status: accepted  
Date: 2026-09-17  
Task: AAX-6

## Context

The live control core already runs `CLICKUP_STATE_STEWARD` every 600 seconds against MariaDB `maziyar_control`. ChatGPT and Grok now share the Agiflow project **Ada AI** (`AAX`) for Phase-1 execution. Bolting Agiflow on as another canonical state writer would create two (or three) competing authorities: ClickUp, Agiflow, and the control plane.

## Decision

Phase 1 keeps **three surfaces with non-overlapping ownership**:

| Surface | Owns | Does not own |
|---|---|---|
| GitHub (`maziyarid/AdaAI`) | Source, tests, ADRs, SQL, runbooks, PR evidence | Runtime job/schedule state |
| MariaDB control core | Runtime jobs, schedules, leases, health, `pending_external_sync` | Agent planning / AAX board |
| Agiflow AAX board | Human/agent execution: blockers, dependencies, progress, handoffs | Jobs, schedules, WordPress, passports |

Agiflow **must not** become a scheduler, job queue, or bidirectional replica of ClickUp.

## Phase-1 interoperability

1. **Do not replace** `CLICKUP_STATE_STEWARD` in this phase. It remains the ClickUp projection for existing control-core entities.
2. **Do not add** an `AGIFLOW_STATE_STEWARD` that writes `jobs` / `schedules` / leases.
3. Ada agents (ChatGPT/Grok) update AAX tasks as they work. Those comments are planning evidence, not runtime truth.
4. Any future control-core → Agiflow projection is **one-directional**, idempotent, and comment/status-only. It must key on an Ada idempotency key, fail closed on version conflict, and audit the attempt. It must not create ClickUp or Agiflow records that the other board then tries to own.
5. When Agiflow is unavailable: continue on GitHub. Catch up AAX comments later. Do not buffer Agiflow writes inside the control core.
6. ClickUp unresolved `pending_external_sync` rows (AAX-5) are diagnosed individually. They are not a reason to stand up a second steward.

## Conflict / failure behaviour

- Runtime vs Agiflow disagreement → MariaDB wins for jobs/schedules; Agiflow is marked blocked with the SHA/evidence.
- Agiflow vs GitHub disagreement on code → GitHub wins.
- ClickUp vs Agiflow → neither is runtime SoT; do not auto-merge. Human/AAX-5 disposition only.

## Consequences

- AAX-6 implementation in Phase 1 is this contract plus documentation, not a new live steward.
- A later steward, if ever approved, goes through Ada `authorize()` + receipts and stays additive around the existing scheduler.
