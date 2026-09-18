"""AAX-15: durable failed-run outbox is execution recovery, not Agiflow projection."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
import threading

from ada_reliability.agiflow_steward import (
    AGIFLOW_IN_PROGRESS,
    AgiflowStateSteward,
    FakeAgiflow,
    ReadOnlyRuntime,
)
from ada_reliability.engine import AdaError
from ada_reliability.failed_run_outbox import (
    CLASS_AGIFLOW_UNAVAILABLE,
    CLASS_FACTORY_PACKET_MISSING,
    CLASS_OOM,
    CLASS_PACKET_PIPELINE,
    CLASS_TRANSIENT,
    HARD_BATCH_CAP,
    LIFECYCLE_DEAD_LETTER,
    LIFECYCLE_INFLIGHT,
    LIFECYCLE_PARKED,
    LIFECYCLE_QUEUED,
    LIFECYCLE_RETRYABLE,
    LIFECYCLE_SUCCEEDED,
    REPLAY_PARKED,
    REPLAY_QUEUED,
    REPLAY_RETRYABLE,
    REPLAY_UNAVAILABLE,
    FailedRunOutbox,
    InMemoryFailedRunStore,
    UnavailableFailedRunStore,
    classify_failure,
    sync_marker,
)

HMAC_KEY = "phase1-agiflow-steward-hmac-key-32b"


class Clock:
    def __init__(self, t: datetime | None = None):
        self.t = t or datetime(2026, 9, 18, 15, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.t

    def advance(self, **kw) -> None:
        self.t += timedelta(**kw)


def _outbox(store=None, **kwargs) -> FailedRunOutbox:
    return FailedRunOutbox(store=store or InMemoryFailedRunStore(), **kwargs)


def _fail(box: FailedRunOutbox, **kwargs):
    defaults = dict(
        run_id="run-1",
        worker="TO-FA-CONTENT",
        reason="connection reset",
        failure_class=CLASS_TRANSIENT,
        schedule_id="sched-1",
        durable_job_id="job-1",
        idempotency_key="idem-run-1",
    )
    defaults.update(kwargs)
    return box.record_failure(**defaults)


# -- classification ---------------------------------------------------------

def test_exit_137_is_parked_oom():
    assert classify_failure(exit_code=137, reason="killed") == CLASS_OOM
    box = _outbox()
    st = _fail(box, exit_code=137, reason="SIGKILL", idempotency_key="oom-1")
    assert st.durable is True
    assert st.replay == REPLAY_PARKED
    assert st.lifecycle == LIFECYCLE_PARKED
    assert st.failure_class == CLASS_OOM
    rec = box.store.get("oom-1")
    assert rec["reset_condition"] == "memory_pressure_resolved"
    assert rec["next_retry_at"] is None


def test_factory_packet_missing_is_parked():
    box = _outbox()
    st = _fail(
        box,
        failure_class=CLASS_FACTORY_PACKET_MISSING,
        reason="FACTORY_PACKET_MISSING packet=abc",
        packet_id="pkt-1",
        factory_task_id="ft-1",
        idempotency_key="pkt-miss",
    )
    assert st.replay == REPLAY_PARKED
    assert box.claim_batch() == []
    assert box.eligible() == []


def test_packet_pipeline_failure_does_not_hot_loop():
    box = _outbox()
    _fail(
        box,
        failure_class=CLASS_PACKET_PIPELINE,
        reason="pipeline stalled",
        idempotency_key="pipe-1",
    )
    first = box.replay_batch()
    second = box.replay_batch()
    assert first["claimed"] == 0
    assert second["claimed"] == 0
    assert box.store.get("pipe-1")["lifecycle"] == LIFECYCLE_PARKED


# -- RUN_STATUS / persistence ----------------------------------------------

def test_retryable_only_after_durable_persist():
    box = _outbox()
    st = _fail(box, idempotency_key="t-1")
    assert st.replay == REPLAY_RETRYABLE
    assert st.durable is True
    assert box.store.get("t-1")["attempt_count"] == 1


def test_unavailable_store_never_claims_success():
    box = _outbox(store=UnavailableFailedRunStore())
    st = _fail(box, idempotency_key="gone")
    assert st.replay == REPLAY_UNAVAILABLE
    assert st.durable is False
    assert st.reason == "DURABLE_STORE_UNAVAILABLE"


def test_missing_identity_is_unavailable_not_queued():
    box = _outbox()
    st = box.record_failure(run_id="", worker="w", reason="x")
    assert st.replay == REPLAY_UNAVAILABLE
    assert st.durable is False


def test_idempotent_record_does_not_duplicate_rows():
    box = _outbox()
    first = _fail(box, idempotency_key="same")
    second = _fail(box, idempotency_key="same", reason="again")
    assert first.failed_run_id == second.failed_run_id
    assert len(box.store.all()) == 1
    assert box.store.get("same")["attempt_count"] == 2


# -- claim / replay bounds -------------------------------------------------

def test_replay_is_bounded_and_in_first_failure_order():
    clock = Clock()
    box = _outbox(clock=clock)
    _fail(box, run_id="r1", idempotency_key="a", durable_job_id="j1")
    clock.advance(seconds=1)
    _fail(box, run_id="r2", idempotency_key="b", durable_job_id="j2")
    clock.advance(seconds=1)
    _fail(box, run_id="r3", idempotency_key="c", durable_job_id="j3")
    claimed = box.claim_batch(limit=2)
    assert [c["idempotency_key"] for c in claimed] == ["a", "b"]
    assert all(c["lifecycle"] == LIFECYCLE_INFLIGHT for c in claimed)
    leftover = box.eligible()
    assert [r["idempotency_key"] for r in leftover] == ["c"]


def test_batch_cap_is_hard():
    box = _outbox()
    for i in range(HARD_BATCH_CAP + 5):
        _fail(box, run_id=f"r{i}", idempotency_key=f"k{i}")
    claimed = box.claim_batch(limit=10_000)
    assert len(claimed) == HARD_BATCH_CAP


def test_parked_is_never_claimed():
    box = _outbox()
    _fail(box, failure_class=CLASS_OOM, exit_code=137, reason="oom", idempotency_key="p")
    _fail(box, idempotency_key="ok")
    claimed = box.claim_batch()
    assert [c["idempotency_key"] for c in claimed] == ["ok"]


def test_future_next_retry_is_not_claimed():
    clock = Clock()
    box = _outbox(clock=clock)
    _fail(box, idempotency_key="later", retry_after=timedelta(minutes=10))
    assert box.claim_batch() == []
    clock.advance(minutes=11)
    assert len(box.claim_batch()) == 1


# -- mutation duplication --------------------------------------------------

def test_wordpress_replay_requires_engine_and_does_not_apply_directly():
    box = _outbox()
    _fail(
        box, idempotency_key="wp-1", mutation_kind="wordpress_mutation",
        mutation_idempotency_key="mut-1",
    )
    result = box.replay_batch()
    assert result["requires_engine"] == 1
    rec = box.store.get("wp-1")
    assert rec["lifecycle"] != LIFECYCLE_SUCCEEDED
    assert box.store.mutation_seen("wordpress_mutation", "mut-1") is False


def test_engine_retry_is_idempotent_across_lost_ack():
    calls = []

    def engine(rec):
        calls.append(rec["idempotency_key"])
        return {"status": "APPLIED"}

    box = _outbox(engine_retry=engine)
    _fail(
        box, idempotency_key="wp-2", mutation_kind="wordpress_mutation",
        mutation_idempotency_key="mut-2",
    )
    first = box.replay_batch()
    assert first["applied"] == 1
    rec = box.store.get("wp-2")
    rec["lifecycle"] = LIFECYCLE_RETRYABLE
    rec["next_retry_at"] = box.now().isoformat()
    box.store.put(rec)
    second = box.replay_batch()
    assert second["skipped"] == 1
    assert calls == ["wp-2"]
    assert box.store.get("wp-2")["lifecycle"] == LIFECYCLE_SUCCEEDED


def test_packet_ack_duplicate_is_skipped():
    box = _outbox()
    box.store.mutation_record("packet_ack", "ack-1")
    _fail(
        box, idempotency_key="ack-run", mutation_kind="packet_ack",
        mutation_idempotency_key="ack-1", packet_id="pkt-9",
    )
    result = box.replay_batch()
    assert result["skipped"] == 1
    assert box.store.get("ack-run")["lifecycle"] == LIFECYCLE_SUCCEEDED


# -- Agiflow handoff (AAX-12), not AAX-12 outbox merge ---------------------

def _steward(jobs: dict) -> tuple[AgiflowStateSteward, FakeAgiflow]:
    runtime = ReadOnlyRuntime(jobs)
    agiflow = FakeAgiflow()
    steward = AgiflowStateSteward(
        agiflow=agiflow, runtime=runtime,
        project_id="other-projects-infrastructure", hmac_key=HMAC_KEY,
    )
    return steward, agiflow


def test_agiflow_outage_persists_pending_external_sync_then_catchup():
    steward, agiflow = _steward({
        "job-1": {"id": "job-1", "state": "running", "title": "canary"},
    })
    box = _outbox(steward=steward)
    st = _fail(
        box,
        failure_class=CLASS_AGIFLOW_UNAVAILABLE,
        reason="agiflow down",
        idempotency_key="ag-1",
        mutation_kind="agiflow_sync",
        durable_job_id="job-1",
    )
    assert st.replay == REPLAY_QUEUED
    agiflow.unavailable = True
    parked = box.replay_batch()
    assert parked["claimed"] == 1
    rec = box.store.get("ag-1")
    assert rec["lifecycle"] == LIFECYCLE_QUEUED
    assert rec["external_sync_state"] == "pending"
    agiflow.unavailable = False
    catchup = box.replay_batch()
    assert catchup["applied"] == 1
    rec = box.store.get("ag-1")
    assert rec["lifecycle"] == LIFECYCLE_SUCCEEDED
    assert rec["external_sync_state"] == "succeeded"
    assert len(agiflow.tasks) == 1
    assert list(agiflow.tasks.values())[0]["status"] == AGIFLOW_IN_PROGRESS
    # replay again must not duplicate comments/tasks
    rec["lifecycle"] = LIFECYCLE_RETRYABLE
    rec["next_retry_at"] = box.now().isoformat()
    rec["mutation_kind"] = "agiflow_sync"
    box.store.put(rec)
    again = box.replay_batch()
    assert again["skipped"] == 1
    assert len(agiflow.comments) == 1
    assert len(agiflow.tasks) == 1


def test_agiflow_human_conflict_parks_without_overwrite():
    steward, agiflow = _steward({
        "job-1": {"id": "job-1", "state": "running", "title": "canary"},
    })
    first = steward.project("job-1")
    agiflow.simulate_human_edit(first["agiflow_task_id"], status="Done")
    box = _outbox(steward=steward)
    _fail(
        box, failure_class=CLASS_AGIFLOW_UNAVAILABLE, reason="sync",
        idempotency_key="ag-conflict", mutation_kind="agiflow_sync",
        durable_job_id="job-1",
    )
    result = box.replay_batch()
    assert result["parked"] == 1
    rec = box.store.get("ag-conflict")
    assert rec["lifecycle"] == LIFECYCLE_PARKED
    assert rec["external_sync_state"] == "conflict"
    assert rec["reset_condition"] == "human_agiflow_conflict_resolved"
    assert agiflow.tasks[first["agiflow_task_id"]]["status"] == "Done"


def test_caller_constructed_agiflow_evidence_still_rejected():
    steward, _ = _steward({
        "job-1": {"id": "job-1", "state": "succeeded", "title": "done?"},
    })
    box = _outbox(steward=steward)
    _fail(
        box, failure_class=CLASS_AGIFLOW_UNAVAILABLE, reason="sync",
        idempotency_key="ag-forged", mutation_kind="agiflow_sync",
        durable_job_id="job-1",
        payload={"evidence_id": "forged-id", "verified": True},
    )
    result = box.replay_one(box.store.get("ag-forged"))
    assert result["status"] == "PARKED"
    assert result["reason"] == "UNKNOWN_EVIDENCE"
    # payload verified flag is ignored; steward looks up id
    rec = box.store.get("ag-forged")
    assert rec["lifecycle"] == LIFECYCLE_PARKED


def test_aax15_store_is_not_the_agiflow_projection_outbox():
    steward, _ = _steward({
        "job-1": {"id": "job-1", "state": "running", "title": "t"},
    })
    box = _outbox(steward=steward)
    _fail(
        box, failure_class=CLASS_AGIFLOW_UNAVAILABLE, reason="down",
        idempotency_key="sep", mutation_kind="agiflow_sync", durable_job_id="job-1",
    )
    assert "sep" in box.store.rows
    assert box.store.rows["sep"].get("kind") != "project"
    assert steward.outbox == {} or all(
        row.get("kind") in ("create_task", "project") for row in steward.outbox.values()
    )


# -- restart simulation (not VPS) ------------------------------------------

def test_in_memory_restart_preserves_records_and_mutation_ledger():
    store = InMemoryFailedRunStore()
    box = _outbox(store=store)
    _fail(box, idempotency_key="keep-me", run_id="r-keep")
    box.store.mutation_record("packet_ack", "ack-z")
    snapshot = store.dump()
    restored = InMemoryFailedRunStore.load(snapshot)
    box2 = _outbox(store=restored)
    rec = box2.store.get("keep-me")
    assert rec["run_id"] == "r-keep"
    assert rec["lifecycle"] == LIFECYCLE_RETRYABLE
    assert restored.mutation_seen("packet_ack", "ack-z") is True
    claimed = box2.claim_batch()
    assert [c["idempotency_key"] for c in claimed] == ["keep-me"]


def test_expired_inflight_lease_requeues_without_duplicate():
    clock = Clock()
    box = _outbox(clock=clock, lease_seconds=30)
    _fail(box, idempotency_key="lease-1")
    claimed = box.claim_batch()
    assert claimed[0]["lifecycle"] == LIFECYCLE_INFLIGHT
    clock.advance(seconds=31)
    again = box.claim_batch()
    assert len(again) == 1
    assert again[0]["idempotency_key"] == "lease-1"
    assert len(box.store.all()) == 1


# -- unpark / dead-letter / quarantine -------------------------------------

def test_unpark_requires_matching_reset_condition():
    box = _outbox()
    _fail(
        box, failure_class=CLASS_FACTORY_PACKET_MISSING,
        reason="FACTORY_PACKET_MISSING", idempotency_key="need-pkt",
    )
    with pytest.raises(AdaError) as ei:
        box.acknowledge_reset("need-pkt", condition="wrong")
    assert ei.value.code == "RESET_CONDITION_MISMATCH"
    assert box.claim_batch() == []
    out = box.acknowledge_reset("need-pkt", condition="packet_available")
    assert out["status"] == "RETRYABLE"
    assert len(box.claim_batch()) == 1


def test_max_attempts_dead_letters():
    box = _outbox()
    st = _fail(box, idempotency_key="dlq", max_attempts=2)
    _fail(box, idempotency_key="dlq", reason="again")
    rec = box.store.get("dlq")
    assert rec["lifecycle"] == LIFECYCLE_DEAD_LETTER
    assert rec["attempt_count"] == 2
    assert box.claim_batch() == []
    assert st.durable is True


def test_quarantine_is_terminal():
    box = _outbox()
    _fail(box, idempotency_key="q1")
    box.quarantine("q1", reason="poison")
    assert box.store.get("q1")["lifecycle"] == "quarantined"
    assert box.claim_batch() == []


# -- must not be a scheduler -----------------------------------------------

def test_outbox_cannot_enqueue_or_lease():
    box = _outbox()
    with pytest.raises(AdaError) as ei:
        box.enqueue("job-1")
    assert ei.value.code == "OUTBOX_MUST_NOT_WRITE_RUNTIME"
    with pytest.raises(AdaError):
        box.acquire_lease("job-1")
    assert box._write_attempts == ["enqueue", "acquire_lease"]


def test_sync_marker_is_stable():
    assert sync_marker("abc") == "[sync:abc]"


def test_clickup_is_unused():
    box = _outbox()
    _fail(box, idempotency_key="cu")
    box.replay_batch()
    assert box.clickup_was_used() is False


# -- Greptile P1 regressions (atomic claim / engine outcome / unknown kind) --

def test_competing_workers_claim_exactly_once():
    """Store-level CAS: two workers may both see an eligible row; only one owns it."""
    calls: list[str] = []
    lock = threading.Lock()
    start = threading.Barrier(2)

    def engine(rec):
        with lock:
            calls.append(rec["idempotency_key"])
        return {"status": "APPLIED"}

    store = InMemoryFailedRunStore()
    box_a = FailedRunOutbox(store=store, engine_retry=engine)
    box_b = FailedRunOutbox(store=store, engine_retry=engine)
    _fail(
        box_a,
        idempotency_key="race-1",
        mutation_kind="wordpress_mutation",
        mutation_idempotency_key="mut-race",
    )

    results: list[dict | None] = [None, None]

    def worker(idx: int, box: FailedRunOutbox) -> None:
        start.wait()
        results[idx] = box.replay_batch()

    threads = [
        threading.Thread(target=worker, args=(0, box_a)),
        threading.Thread(target=worker, args=(1, box_b)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert calls == ["race-1"]
    assert store.get("race-1")["lifecycle"] == LIFECYCLE_SUCCEEDED
    assert sum(r["claimed"] for r in results) == 1
    assert sum(r["applied"] for r in results) == 1
    assert store.mutation_seen("wordpress_mutation", "mut-race") is True


def test_engine_failed_does_not_become_succeeded():
    box = _outbox(engine_retry=lambda rec: {"status": "FAILED"})
    _fail(box, idempotency_key="fail-1")
    result = box.replay_batch()
    rec = box.store.get("fail-1")
    assert rec["lifecycle"] != LIFECYCLE_SUCCEEDED
    assert rec["lifecycle"] in (LIFECYCLE_RETRYABLE, LIFECYCLE_QUEUED)
    assert result["applied"] == 0
    assert result["claimed"] == 1


def test_engine_executing_does_not_become_succeeded():
    box = _outbox(engine_retry=lambda rec: {"status": "EXECUTING"})
    _fail(box, idempotency_key="exec-1")
    result = box.replay_batch()
    rec = box.store.get("exec-1")
    assert rec["lifecycle"] != LIFECYCLE_SUCCEEDED
    assert rec["lifecycle"] in (LIFECYCLE_RETRYABLE, LIFECYCLE_QUEUED)
    assert result["applied"] == 0


def test_unknown_engine_status_is_parked_not_succeeded():
    box = _outbox(engine_retry=lambda rec: {"status": "MAYBE"})
    _fail(box, idempotency_key="maybe-1")
    result = box.replay_one(box.store.get("maybe-1"))
    rec = box.store.get("maybe-1")
    assert result["status"] == "PARKED"
    assert rec["lifecycle"] == LIFECYCLE_PARKED
    assert rec["lifecycle"] != LIFECYCLE_SUCCEEDED


def test_unknown_mutation_kind_is_parked_on_persist():
    box = _outbox()
    st = _fail(
        box, idempotency_key="unk-1", mutation_kind="side_channel_write",
    )
    assert st.replay == REPLAY_PARKED
    assert st.lifecycle == LIFECYCLE_PARKED
    rec = box.store.get("unk-1")
    assert rec["mutation_kind"] == "side_channel_write"
    assert rec["last_error"] == "UNKNOWN_MUTATION_KIND"
    assert rec["reset_condition"] == "mutation_kind_supported"
    assert box.claim_batch() == []
    replayed = box.replay_one(rec)
    assert replayed["status"] == "PARKED"
    assert box.store.get("unk-1")["lifecycle"] != LIFECYCLE_SUCCEEDED


def test_legacy_unknown_mutation_kind_is_parked_on_replay():
    """Corrupt/legacy rows that bypassed persist validation must not succeed."""
    box = _outbox()
    _fail(box, idempotency_key="legacy-unk")
    rec = box.store.get("legacy-unk")
    rec["mutation_kind"] = "mystery_kind"
    rec["lifecycle"] = LIFECYCLE_RETRYABLE
    box.store.put(rec)
    result = box.replay_one(box.store.get("legacy-unk"))
    assert result["status"] == "PARKED"
    assert result["reason"] == "UNKNOWN_MUTATION_KIND"
    stored = box.store.get("legacy-unk")
    assert stored["lifecycle"] == LIFECYCLE_PARKED
    assert stored["lifecycle"] != LIFECYCLE_SUCCEEDED
