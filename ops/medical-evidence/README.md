# Medical verifier failure contract

Recovered from the current live medical_evidence.py on 2026-09-30.
Baseline SHA-256: 5eeb3b3811351eafaf327ff041166dc502dc286e141d9d8a11fd8f3b336f6d70.

Scope: execution failure reporting and recovery only. Source retrieval, evidence
tiers, medical risk classification and independent claim approval are preserved.

A verifier error retains its created job ID, records a safe fixed error code,
and returns a nonzero command exit status. The existing hourly orchestrator
therefore detects this step as failed. Its chain becomes blocked_verifier in
the existing content_ladder, with no approved claims and an explicit repair /
authorised retry condition. Reopening SQLite after process restart still excludes
that chain from run-pending.

Failure recording invokes the existing run_ledger_outbox.py persist-failure
command: pd_outbox stays the only active recovery owner. A chain/code fingerprint
remains stable across run IDs. replay=parked is reported only when the helper
confirms durable persistence; missing/broken storage reports replay=UNAVAILABLE.
No second outbox or MariaDB migration is introduced.

APPROVED and INSUFFICIENT_EVIDENCE remain their existing distinct evidence
outcomes. Neither is a verifier execution failure. This patch does not change
clinical approval, source sufficiency or human review requirements.

## Controlled deployment

AAX-11/15 runtime changes require explicit deployment approval. Check the live
baseline hash and preserve a root-only code backup. Confirm an evidence worker
is not currently running before replacing only medical_evidence.py at its
existing deploy path. Preserve the existing scheduler, database and run ledger.
Do not enqueue an AI job or publish content just to test deployment.

Validate run_ledger_outbox.py availability/permissions and the same interpreter
before activation. Production acceptance must show a failed fixture yields a
nonzero process result, a durable parked failure, the verifier job ID and no
duplicate scheduling/publication. Offline tests are not this live proof.

Recovery is operator-controlled after repairing the verifier dependency: inspect
the retained job and evidence, then authorise one bounded retry through the
existing workflow. Do not reset clinical human approval or blindly bulk-reset
historical failures.

Rollback restores the backed-up code. Preserve medical_evidence_runs, pd_outbox
and blocked_verifier records. Older code will not select blocked_verifier through
run-pending; do not erase those records to force automatic replay.

## Verification

pytest ops/medical-evidence/tests

Tests isolate SQLite and fake providers; no real model/API invocation occurs.
