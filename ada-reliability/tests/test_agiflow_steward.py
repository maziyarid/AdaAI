"""AAX-12 / ADR-0003: Agiflow is a coordination projection, not a scheduler."""
from __future__ import annotations

import pytest

from ada_reliability.agiflow_steward import (
    AGIFLOW_BLOCKED,
    AGIFLOW_CANCELLED,
    AGIFLOW_DONE,
    AGIFLOW_IN_PROGRESS,
    AGIFLOW_REVIEW,
    AGIFLOW_TODO,
    AgiflowStateSteward,
    CloseGrant,
    FakeAgiflow,
    IssuedEvidence,
    ReadOnlyRuntime,
)
from ada_reliability.engine import AdaError

HMAC_KEY = "phase1-agiflow-steward-hmac-key-32b"


def _job(job_id: str, state: str, title: str = "Teznevise metadata") -> dict:
    return {"id": job_id, "state": state, "title": title, "site_id": "teznevise.ir"}


def _steward(jobs: dict[str, dict] | None = None) -> tuple[AgiflowStateSteward, FakeAgiflow, ReadOnlyRuntime]:
    runtime = ReadOnlyRuntime(jobs or {})
    agiflow = FakeAgiflow()
    steward = AgiflowStateSteward(
        agiflow=agiflow,
        runtime=runtime,
        project_id="other-projects-infrastructure",
        hmac_key=HMAC_KEY,
    )
    return steward, agiflow, runtime


def _issue(steward: AgiflowStateSteward, job_id: str, **kwargs) -> IssuedEvidence:
    defaults = dict(
        durable_job_id=job_id,
        live_hash="abc123live",
        verifier_identity="verifier",
        source="runtime",
    )
    defaults.update(kwargs)
    return steward.issue_evidence(**defaults)


# -- mapping ----------------------------------------------------------------

def test_stable_mapping_is_idempotent():
    job = _job("job-1", "queued")
    steward, agiflow, _ = _steward({"job-1": job})
    first = steward.ensure_mapping("job-1", job["title"])
    second = steward.ensure_mapping("job-1", job["title"])
    assert first["created"] is True
    assert second["created"] is False
    assert first["mapping"].agiflow_task_id == second["mapping"].agiflow_task_id
    assert len(agiflow.tasks) == 1


def test_queued_job_projects_to_todo():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "queued")})
    result = steward.project("job-1")
    assert result["status"] == "PROJECTED"
    assert result["agiflow_status"] == AGIFLOW_TODO
    assert agiflow.tasks[result["agiflow_task_id"]]["status"] == AGIFLOW_TODO


def test_running_job_projects_in_progress_checkpoint():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "running")})
    result = steward.project("job-1")
    assert result["agiflow_status"] == AGIFLOW_IN_PROGRESS
    bodies = [c["body"] for c in agiflow.comments]
    assert any("is running" in b for b in bodies)


# -- evidence-backed completion --------------------------------------------

def test_succeeded_without_evidence_stays_in_progress():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "succeeded")})
    result = steward.project("job-1")
    assert result["agiflow_status"] == AGIFLOW_IN_PROGRESS
    assert agiflow.tasks[result["agiflow_task_id"]]["status"] != AGIFLOW_REVIEW
    assert agiflow.tasks[result["agiflow_task_id"]]["status"] != AGIFLOW_DONE


def test_untrusted_verifier_cannot_issue_evidence():
    steward, _, _ = _steward({"job-1": _job("job-1", "succeeded")})
    with pytest.raises(AdaError) as ei:
        steward.issue_evidence(
            durable_job_id="job-1",
            live_hash="abc123live",
            verifier_identity="model_proposer",
            source="runtime",
        )
    assert ei.value.code == "UNTRUSTED_VERIFIER"


def test_model_source_cannot_issue_evidence():
    steward, _, _ = _steward({"job-1": _job("job-1", "succeeded")})
    with pytest.raises(AdaError) as ei:
        steward.issue_evidence(
            durable_job_id="job-1",
            live_hash="abc123live",
            verifier_identity="verifier",
            source="model_assertion",
        )
    assert ei.value.code == "UNTRUSTED_EVIDENCE_SOURCE"


def test_caller_constructed_evidence_is_rejected():
    """Greptile P1: a caller-built object with trusted-looking strings is not proof."""
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "succeeded")})
    forged = IssuedEvidence(
        id="forged-id",
        durable_job_id="job-1",
        live_hash="abc123live",
        verifier_identity="verifier",
        source="runtime",
        signature="deadbeef",
    )
    with pytest.raises(AdaError) as ei:
        steward.project("job-1", evidence_id=forged.id)
    assert ei.value.code == "UNKNOWN_EVIDENCE"
    # no evidence_id → still withheld
    result = steward.project("job-1")
    assert result["agiflow_status"] == AGIFLOW_IN_PROGRESS
    assert list(agiflow.tasks.values())[0]["status"] == AGIFLOW_IN_PROGRESS


def test_evidence_bound_to_other_job_is_denied():
    steward, _, _ = _steward({
        "job-1": _job("job-1", "succeeded"),
        "job-2": _job("job-2", "succeeded"),
    })
    ev = _issue(steward, "job-2")
    with pytest.raises(AdaError) as ei:
        steward.project("job-1", evidence_id=ev.id)
    assert ei.value.code == "EVIDENCE_JOB_MISMATCH"


def test_tampered_issued_evidence_signature_is_denied():
    steward, _, _ = _steward({"job-1": _job("job-1", "succeeded")})
    ev = _issue(steward, "job-1")
    steward.issued_evidence[ev.id]["signature"] = "00" * 32
    with pytest.raises(AdaError) as ei:
        steward.project("job-1", evidence_id=ev.id)
    assert ei.value.code == "FORGED_EVIDENCE"


def test_verified_success_projects_review():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "succeeded")})
    ev = _issue(steward, "job-1")
    result = steward.project("job-1", evidence_id=ev.id)
    assert result["agiflow_status"] == AGIFLOW_REVIEW
    assert agiflow.tasks[result["agiflow_task_id"]]["status"] == AGIFLOW_REVIEW


def test_done_requires_issued_human_close_grant():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "succeeded")})
    ev = _issue(steward, "job-1")
    with pytest.raises(AdaError) as ei:
        steward.issue_close_grant(
            durable_job_id="job-1", evidence_id=ev.id, closer_identity="model_proposer",
        )
    assert ei.value.code == "UNTRUSTED_CLOSER"
    review = steward.project("job-1", evidence_id=ev.id)
    assert review["agiflow_status"] == AGIFLOW_REVIEW
    grant = steward.issue_close_grant(
        durable_job_id="job-1", evidence_id=ev.id, closer_identity="human_approver",
    )
    done = steward.project("job-1", evidence_id=ev.id, close_grant_id=grant.id)
    assert done["agiflow_status"] == AGIFLOW_DONE
    assert agiflow.tasks[done["agiflow_task_id"]]["status"] == AGIFLOW_DONE


def test_close_grant_is_one_time():
    steward, _, _ = _steward({"job-1": _job("job-1", "succeeded")})
    ev = _issue(steward, "job-1")
    grant = steward.issue_close_grant(
        durable_job_id="job-1", evidence_id=ev.id, closer_identity="human_approver",
    )
    first = steward.project("job-1", evidence_id=ev.id, close_grant_id=grant.id)
    assert first["agiflow_status"] == AGIFLOW_DONE
    with pytest.raises(AdaError) as ei:
        steward.project("job-1", evidence_id=ev.id, close_grant_id=grant.id)
    assert ei.value.code == "CLOSE_GRANT_CONSUMED"


def test_forged_close_grant_id_is_rejected():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "succeeded")})
    ev = _issue(steward, "job-1")
    forged = CloseGrant(
        id="forged-grant",
        durable_job_id="job-1",
        evidence_id=ev.id,
        closer_identity="human_approver",
        signature="deadbeef",
    )
    with pytest.raises(AdaError) as ei:
        steward.project("job-1", evidence_id=ev.id, close_grant_id=forged.id)
    assert ei.value.code == "UNKNOWN_CLOSE_GRANT"
    result = steward.project("job-1", evidence_id=ev.id)
    assert result["agiflow_status"] == AGIFLOW_REVIEW


def test_legacy_evidence_kwarg_is_not_accepted():
    """Old forgeable API was project(..., evidence=ProjectionEvidence(...))."""
    steward, _, _ = _steward({"job-1": _job("job-1", "succeeded")})
    with pytest.raises(TypeError):
        steward.project("job-1", evidence=object())  # type: ignore[call-arg]


def test_missing_live_hash_cannot_issue():
    steward, _, _ = _steward({"job-1": _job("job-1", "succeeded")})
    with pytest.raises(AdaError) as ei:
        steward.issue_evidence(
            durable_job_id="job-1",
            live_hash="",
            verifier_identity="verifier",
        )
    assert ei.value.code == "MISSING_LIVE_HASH"


def test_issue_evidence_requires_known_job():
    steward, _, _ = _steward()
    with pytest.raises(AdaError) as ei:
        steward.issue_evidence(
            durable_job_id="missing",
            live_hash="abc123live",
            verifier_identity="verifier",
        )
    assert ei.value.code == "UNKNOWN_RUNTIME_JOB"


def test_close_grant_without_evidence_id_is_denied():
    steward, _, _ = _steward({"job-1": _job("job-1", "succeeded")})
    with pytest.raises(AdaError) as ei:
        steward.project("job-1", close_grant_id="any-grant")
    assert ei.value.code == "CLOSE_GRANT_REQUIRES_EVIDENCE"


def test_tampered_close_grant_signature_is_denied():
    steward, _, _ = _steward({"job-1": _job("job-1", "succeeded")})
    ev = _issue(steward, "job-1")
    grant = steward.issue_close_grant(
        durable_job_id="job-1", evidence_id=ev.id, closer_identity="human_approver",
    )
    steward.close_grants[grant.id]["signature"] = "00" * 32
    with pytest.raises(AdaError) as ei:
        steward.project("job-1", evidence_id=ev.id, close_grant_id=grant.id)
    assert ei.value.code == "FORGED_CLOSE_GRANT"


def test_failed_job_projects_blocked():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "failed")})
    result = steward.project("job-1")
    assert result["agiflow_status"] == AGIFLOW_BLOCKED


# -- idempotent comments ---------------------------------------------------

def test_repeat_projection_does_not_duplicate_comments():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "running")})
    steward.project("job-1")
    steward.project("job-1")
    steward.project("job-1")
    assert len(agiflow.comments) == 1


def test_distinct_events_get_distinct_comments():
    jobs = {"job-1": _job("job-1", "running")}
    steward, agiflow, runtime = _steward(jobs)
    steward.project("job-1")
    runtime.jobs["job-1"] = _job("job-1", "succeeded")
    ev = _issue(steward, "job-1")
    steward.project("job-1", evidence_id=ev.id)
    kinds = {c["idempotency_key"] for c in agiflow.comments}
    assert len(agiflow.comments) == 2
    assert len(kinds) == 2


# -- human edit preservation -----------------------------------------------

def test_newer_human_edit_is_not_overwritten():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "running")})
    first = steward.project("job-1")
    agiflow.simulate_human_edit(first["agiflow_task_id"], status=AGIFLOW_DONE)
    steward.runtime.jobs["job-1"] = _job("job-1", "failed")
    result = steward.project("job-1")
    assert result["status"] == "CONFLICT"
    assert result["reason"] == "newer_human_edit"
    assert agiflow.tasks[first["agiflow_task_id"]]["status"] == AGIFLOW_DONE


# -- outage / replay -------------------------------------------------------

def test_outage_parks_outbox_and_runtime_is_untouched():
    steward, agiflow, runtime = _steward({"job-1": _job("job-1", "running")})
    agiflow.unavailable = True
    result = steward.project("job-1")
    assert result["status"] == "PENDING_SYNC"
    assert steward.pending_outbox()
    assert runtime.write_attempts == []
    assert runtime.get_job("job-1")["state"] == "running"


def test_replay_after_recovery_is_idempotent():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "running")})
    agiflow.unavailable = True
    steward.project("job-1")
    steward.project("job-1")  # duplicate enqueue must collapse per kind
    pending = steward.pending_outbox()
    assert {row["durable_job_id"] for row in pending} == {"job-1"}
    assert {row["kind"] for row in pending} <= {"create_task", "project"}
    assert len(pending) <= 2
    agiflow.unavailable = False
    first = steward.replay_outbox()
    second = steward.replay_outbox()
    assert first["applied"] >= 1
    assert second["applied"] == 0
    assert len(agiflow.tasks) == 1
    assert len(agiflow.comments) == 1
    task = next(iter(agiflow.tasks.values()))
    assert task["status"] == AGIFLOW_IN_PROGRESS


def test_replay_preserves_human_conflict():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "running")})
    first = steward.project("job-1")
    agiflow.simulate_human_edit(first["agiflow_task_id"], status=AGIFLOW_CANCELLED)
    steward.runtime.jobs["job-1"] = _job("job-1", "succeeded")
    ev = _issue(steward, "job-1")
    agiflow.unavailable = True
    parked = steward.project("job-1", evidence_id=ev.id)
    assert parked["status"] == "PENDING_SYNC"
    agiflow.unavailable = False
    replayed = steward.replay_outbox()
    assert replayed["conflicts"] == 1
    assert agiflow.tasks[first["agiflow_task_id"]]["status"] == AGIFLOW_CANCELLED


def test_outbox_does_not_store_forgeable_evidence_fields():
    steward, agiflow, _ = _steward({"job-1": _job("job-1", "succeeded")})
    ev = _issue(steward, "job-1")
    agiflow.unavailable = True
    steward.project("job-1", evidence_id=ev.id)
    pending = steward.pending_outbox()
    for row in pending:
        payload = row["payload"]
        assert "verified" not in payload
        assert "verifier_identity" not in payload
        assert "closer_identity" not in payload
        if row["kind"] == "project":
            assert payload.get("evidence_id") == ev.id


# -- steward must not own runtime or execute Agiflow -----------------------

def test_steward_cannot_enqueue_or_lease():
    steward, _, runtime = _steward({"job-1": _job("job-1", "queued")})
    with pytest.raises(AdaError) as ei:
        runtime.enqueue("job-1")
    assert ei.value.code == "STEWARD_MUST_NOT_WRITE_RUNTIME"
    with pytest.raises(AdaError):
        runtime.acquire_lease("job-1")
    assert "enqueue" in runtime.write_attempts
    assert "acquire_lease" in runtime.write_attempts
    steward.project("job-1")
    assert runtime.write_attempts == ["enqueue", "acquire_lease"]


def test_steward_must_not_call_agiflow_execute():
    _, agiflow, _ = _steward()
    with pytest.raises(AdaError) as ei:
        agiflow.execute("anything")
    assert ei.value.code == "STEWARD_MUST_NOT_EXECUTE_AGIFLOW"
    assert agiflow.execute_calls == ["execute"]


def test_clickup_is_never_required():
    class ClickUpSpy:
        def __init__(self):
            self.calls = []

        def create_task(self, *a, **k):
            self.calls.append(("create_task", a, k))
            raise AssertionError("ClickUp must not be used")

    spy = ClickUpSpy()
    runtime = ReadOnlyRuntime({"job-1": _job("job-1", "queued")})
    agiflow = FakeAgiflow()
    steward = AgiflowStateSteward(
        agiflow=agiflow, runtime=runtime, project_id="p", hmac_key=HMAC_KEY, clickup=spy,
    )
    steward.project("job-1")
    assert spy.calls == []
    assert steward.clickup_was_used() is False


def test_hmac_key_too_short_fails_closed():
    with pytest.raises(RuntimeError):
        AgiflowStateSteward(
            agiflow=FakeAgiflow(),
            runtime=ReadOnlyRuntime(),
            project_id="p",
            hmac_key="short",
        )


# -- rollback of projection, not of runtime --------------------------------

def test_rollback_restores_previous_agiflow_status():
    jobs = {"job-1": _job("job-1", "queued")}
    steward, agiflow, runtime = _steward(jobs)
    steward.project("job-1")
    runtime.jobs["job-1"] = _job("job-1", "running")
    projected = steward.project("job-1")
    assert projected["agiflow_status"] == AGIFLOW_IN_PROGRESS
    rolled = steward.rollback_projection("job-1")
    assert rolled["status"] == "ROLLED_BACK"
    assert rolled["agiflow_status"] == AGIFLOW_TODO
    assert runtime.get_job("job-1")["state"] == "running"


def test_rollback_refuses_newer_human_edit():
    steward, agiflow, runtime = _steward({"job-1": _job("job-1", "queued")})
    steward.project("job-1")
    runtime.jobs["job-1"] = _job("job-1", "running")
    first = steward.project("job-1")
    agiflow.simulate_human_edit(first["agiflow_task_id"], status=AGIFLOW_DONE)
    result = steward.rollback_projection("job-1")
    assert result["status"] == "CONFLICT"
    assert agiflow.tasks[first["agiflow_task_id"]]["status"] == AGIFLOW_DONE


# -- in-process canary (repository proof; not a live VPS canary) -----------

def test_in_process_canary_job_to_review_with_outage_and_rollback():
    jobs = {"canary-1": _job("canary-1", "queued", title="canary metadata")}
    steward, agiflow, runtime = _steward(jobs)

    queued = steward.project("canary-1")
    assert queued["agiflow_status"] == AGIFLOW_TODO

    runtime.jobs["canary-1"] = _job("canary-1", "running", title="canary metadata")
    running = steward.project("canary-1")
    assert running["agiflow_status"] == AGIFLOW_IN_PROGRESS

    agiflow.unavailable = True
    runtime.jobs["canary-1"] = _job("canary-1", "succeeded", title="canary metadata")
    ev = _issue(steward, "canary-1")
    parked = steward.project("canary-1", evidence_id=ev.id)
    assert parked["status"] == "PENDING_SYNC"
    assert runtime.get_job("canary-1")["state"] == "succeeded"

    agiflow.unavailable = False
    replay = steward.replay_outbox()
    assert replay["applied"] >= 1
    task_id = steward.mapping_for("canary-1").agiflow_task_id
    assert agiflow.tasks[task_id]["status"] == AGIFLOW_REVIEW

    rolled = steward.rollback_projection("canary-1")
    assert rolled["status"] == "ROLLED_BACK"
    assert agiflow.tasks[task_id]["status"] == AGIFLOW_IN_PROGRESS
    assert runtime.get_job("canary-1")["state"] == "succeeded"


def test_unknown_runtime_job_fails_closed():
    steward, _, _ = _steward()
    with pytest.raises(AdaError) as ei:
        steward.project("missing")
    assert ei.value.code == "UNKNOWN_RUNTIME_JOB"
