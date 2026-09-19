from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "ada-reliability" / "scripts" / "aax15_sqlite_cutover_plan.py"
spec = importlib.util.spec_from_file_location("aax15_cutover", SCRIPT)
cutover = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(cutover)


def make_db(path: Path, states=("succeeded", "parked")) -> Path:
    c = sqlite3.connect(path)
    c.executescript(
        """
        CREATE TABLE pd_worker_runs (
          id INTEGER PRIMARY KEY AUTOINCREMENT, worker TEXT NOT NULL, run_id TEXT NOT NULL,
          schedule TEXT, site TEXT, state TEXT NOT NULL, status_json TEXT NOT NULL,
          evidence_ref TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          UNIQUE(worker,run_id)
        );
        CREATE TABLE pd_outbox (
          id INTEGER PRIMARY KEY AUTOINCREMENT, stable_id TEXT NOT NULL UNIQUE,
          idempotency_key TEXT NOT NULL UNIQUE, worker TEXT NOT NULL, run_id TEXT NOT NULL,
          event_type TEXT NOT NULL, state TEXT NOT NULL, failure_class TEXT, reason TEXT,
          schedule TEXT, factory_task_id TEXT, packet_ref TEXT, artifact_ref TEXT,
          payload_json TEXT NOT NULL DEFAULT '{}', reset_condition TEXT,
          attempts INTEGER NOT NULL DEFAULT 0, max_attempts INTEGER NOT NULL DEFAULT 5,
          first_failed_at TEXT NOT NULL, last_failed_at TEXT NOT NULL, next_eligible_at TEXT,
          leased_by TEXT, lease_until TEXT, external_sync_state TEXT, completed_at TEXT,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        """
    )
    c.execute(
        "INSERT INTO pd_worker_runs(worker,run_id,schedule,site,state,status_json,evidence_ref,created_at,updated_at) "
        "VALUES('w','r','','','DONE','{}','','2026-09-18T00:00:00+00:00','2026-09-18T00:00:00+00:00')"
    )
    for i, state in enumerate(states, 1):
        event = "agiflow_sync" if state == "parked" else "packet_sync"
        c.execute(
            """INSERT INTO pd_outbox(
              stable_id,idempotency_key,worker,run_id,event_type,state,failure_class,reason,
              schedule,factory_task_id,packet_ref,artifact_ref,payload_json,reset_condition,
              attempts,max_attempts,first_failed_at,last_failed_at,next_eligible_at,leased_by,
              lease_until,external_sync_state,completed_at,created_at,updated_at)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                f"stable-{i}", f"idem-{i}", "w", f"r-{i}", event, state, "TEST", "reason",
                "", "", "", "", '{"content":"x"}', "human approval" if state == "parked" else "",
                1, 5, "2026-09-18T00:00:00+00:00", "2026-09-18T00:00:01+00:00",
                None, None, None, "none", "2026-09-18T00:00:02+00:00" if state == "succeeded" else None,
                "2026-09-18T00:00:00+00:00", "2026-09-18T00:00:01+00:00",
            ),
        )
    c.commit()
    c.close()
    return path


def test_quiescent_plan_preserves_idempotency_and_parked_semantics(tmp_path):
    db = make_db(tmp_path / "factory.sqlite3")
    before = db.read_bytes()
    plan = cutover.build_plan(db)
    assert plan["cutover_ready_for_approved_maintenance_window"] is False
    assert plan["decision"]["dual_write_allowed"] is False
    assert plan["preconditions"]["active_replay_rows"] == 0
    assert plan["preconditions"]["parked_rows"] == 1
    rows = plan["target"]["rows"]
    assert [r["idempotency_key"] for r in rows] == ["idem-1", "idem-2"]
    parked = next(r for r in rows if r["lifecycle"] == "parked")
    assert parked["mutation_kind"] == "agiflow_sync"
    assert parked["durable_job_id"] is None
    assert plan["preconditions"]["missing_durable_job_bindings"] == ["stable-2"]
    assert parked["lease_owner"] is None
    assert parked["claim_generation"] == 0
    assert db.read_bytes() == before


def test_active_replay_snapshot_is_refused(tmp_path):
    db = make_db(tmp_path / "factory.sqlite3", states=("succeeded", "retryable"))
    try:
        cutover.build_plan(db)
    except cutover.CutoverError as exc:
        assert "active replay rows" in str(exc)
    else:
        raise AssertionError("retryable snapshot must be refused")


def test_plan_is_deterministic(tmp_path):
    db = make_db(tmp_path / "factory.sqlite3")
    a = cutover.build_plan(db)
    b = cutover.build_plan(db)
    assert a["source"]["outbox_digest"] == b["source"]["outbox_digest"]
    assert a["target"]["row_digest"] == b["target"]["row_digest"]
    assert [r["id"] for r in a["target"]["rows"]] == [r["id"] for r in b["target"]["rows"]]


def test_explicit_durable_job_binding_makes_replayable_snapshot_ready(tmp_path):
    db = make_db(tmp_path / "factory.sqlite3")
    plan = cutover.build_plan(db, {"stable-2": "control-core-job-42"})
    assert plan["cutover_ready_for_approved_maintenance_window"] is True
    assert plan["preconditions"]["missing_durable_job_bindings"] == []
    parked = next(r for r in plan["target"]["rows"] if r["lifecycle"] == "parked")
    assert parked["mutation_kind"] == "agiflow_sync"
    assert parked["durable_job_id"] == "control-core-job-42"


def test_payload_durable_job_binding_is_preserved(tmp_path):
    db = make_db(tmp_path / "factory.sqlite3")
    c = sqlite3.connect(db)
    c.execute(
        "UPDATE pd_outbox SET payload_json=? WHERE stable_id='stable-2'",
        ('{"content":"x","durable_job_id":"job-from-payload"}',),
    )
    c.commit()
    c.close()
    plan = cutover.build_plan(db)
    assert plan["cutover_ready_for_approved_maintenance_window"] is True
    parked = next(r for r in plan["target"]["rows"] if r["lifecycle"] == "parked")
    assert parked["durable_job_id"] == "job-from-payload"


def test_unknown_job_binding_is_refused(tmp_path):
    db = make_db(tmp_path / "factory.sqlite3")
    try:
        cutover.build_plan(db, {"does-not-exist": "job-1"})
    except cutover.CutoverError as exc:
        assert "unknown stable_id" in str(exc)
    else:
        raise AssertionError("unknown binding must be refused")
