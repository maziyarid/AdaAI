from __future__ import annotations
import importlib.util
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
import pytest

SCRIPT=Path(__file__).resolve().parents[1]/"medical_evidence.py"
spec=importlib.util.spec_from_file_location("medical_evidence_under_test", SCRIPT)
medical=importlib.util.module_from_spec(spec)
spec.loader.exec_module(medical)


def database(tmp_path, monkeypatch):
    db=tmp_path/"factory.sqlite3"
    monkeypatch.setattr(medical,"DB",db)
    with medical.connect() as c:
        c.executescript("""
        CREATE TABLE content_ladder(chain_id TEXT PRIMARY KEY, factory_lane TEXT,site_key TEXT,
          worker_id TEXT,stage TEXT,status TEXT,state_json TEXT,updated_at TEXT);
        CREATE TABLE content_ladder_events(chain_id TEXT,stage TEXT,event_type TEXT,detail_json TEXT,created_at TEXT);
        """)
        c.execute("INSERT INTO content_ladder VALUES(?,?,?,?,?,?,?,?)",
                  ("chain1","medical","site1","DRB-MED","D","awaiting_claim_approval",'{}',"2026-01-01T00:00:00Z"))
        medical.ensure_schema(c)
    return db


def test_verifier_failure_makes_cli_exit_nonzero(tmp_path,monkeypatch,capsys):
    database(tmp_path,monkeypatch)
    monkeypatch.setattr(medical,"run_pending",lambda limit:[{"status":"VERIFIER_FAILED"}])
    monkeypatch.setattr(sys,"argv",["medical_evidence","run-pending"])
    assert medical.main()==1
    assert json.loads(capsys.readouterr().out)["results"][0]["status"]=="VERIFIER_FAILED"


def test_failed_verifier_retains_created_job_id(monkeypatch):
    def fake(argv,**kwargs):
        return subprocess.CompletedProcess(argv,0,json.dumps({"job_id":"job1"} if argv[1]=="queue" else {"status":"blocked"}),"")
    monkeypatch.setattr(medical.subprocess,"run",fake)
    with pytest.raises(medical.VerifierError) as info:
        medical.queue_and_run_verifier("site1","chain1","public claims")
    assert info.value.job_id=="job1"
    assert info.value.code=="VERIFIER_CANDIDATE_NOT_READY"


def test_failure_is_durable_parked_and_ineligible_after_restart(tmp_path,monkeypatch):
    db=database(tmp_path,monkeypatch)
    claims=[{"claim_key":"claim1","candidate_wording":"fixture wording","medical_risk":"M1","uncertainty":""}]
    monkeypatch.setattr(medical,"candidate_claims_from_state",lambda state:claims)
    monkeypatch.setattr(medical,"retrieve_for_claim",lambda *args: ([],{}))
    monkeypatch.setattr(medical,"verifier_prompt",lambda *args:"fixture")
    def fail(*args):
        raise medical.VerifierError("VERIFIER_CANDIDATE_NOT_READY","job1")
    monkeypatch.setattr(medical,"queue_and_run_verifier",fail)
    monkeypatch.setattr(medical,"record_verifier_failure",lambda *args:{"replay":"parked"})
    result=medical.process_chain("chain1")
    assert result["status"]=="VERIFIER_FAILED" and result["verifier_job_id"]=="job1"
    assert result["approved"]==0
    with sqlite3.connect(db) as c:
        status,raw=c.execute("SELECT status,state_json FROM content_ladder WHERE chain_id='chain1'").fetchone()
        assert status=="blocked_verifier"
        assert json.loads(raw)["verifier_reset_condition"]==medical.RESET_CONDITION
        assert c.execute("SELECT verifier_job_id FROM medical_evidence_runs").fetchone()[0]=="job1"
    # Reload source and reopen the real SQLite file: no in-process state.
    again=importlib.util.module_from_spec(spec);spec.loader.exec_module(again);again.DB=db
    assert again.pending_chain_ids(8)==[]
    assert again.process_chain("chain1")["status"]=="SKIPPED_NOT_AT_EVIDENCE_GATE"


@pytest.mark.parametrize("stdout,rc,expected", [
    ('{"status":"PERSISTED","replay":"parked"}',0,"parked"),
    ('{"status":"PERSISTED","replay":"retryable"}',0,"UNAVAILABLE"),
    ('{"status":"RUN_RECORDED_REPLAY_UNAVAILABLE","replay":"UNAVAILABLE"}',0,"UNAVAILABLE"),
    ('bad json',0,"UNAVAILABLE"), ('',1,"UNAVAILABLE")])
def test_existing_ledger_failure_is_never_reported_as_queued(monkeypatch,stdout,rc,expected):
    calls=[]
    def fake(argv,**kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv,rc,stdout,"private error")
    monkeypatch.setattr(medical.subprocess,"run",fake)
    row={"chain_id":"chain1","worker_id":"DRB-MED","site_key":"site1"}
    first=medical.record_verifier_failure(row,"run1","VERIFIER_RUN_FAILED","job1")
    assert first["replay"]==expected
    medical.record_verifier_failure(row,"run2","VERIFIER_RUN_FAILED","job1")
    # Attempt IDs cannot create a second replay owner for the same failure.
    for flag in ("--stable-id","--idempotency-key"):
        assert calls[0][calls[0].index(flag)+1]==calls[1][calls[1].index(flag)+1]
    assert "private error" not in json.dumps(first)


@pytest.mark.parametrize("results", [[],[{"status":"APPROVED"}],[{"status":"INSUFFICIENT_EVIDENCE"}]])
def test_expected_gate_results_do_not_mark_verifier_as_broken(tmp_path,monkeypatch,results):
    database(tmp_path,monkeypatch)
    monkeypatch.setattr(medical,"run_pending",lambda limit:results)
    monkeypatch.setattr(sys,"argv",["medical_evidence","run-pending"])
    assert medical.main()==0


def test_cli_single_failed_chain_exits_nonzero(tmp_path,monkeypatch):
    database(tmp_path,monkeypatch)
    monkeypatch.setattr(medical,"process_chain",lambda chain:{"status":"VERIFIER_FAILED"})
    monkeypatch.setattr(sys,"argv",["medical_evidence","run","chain1"])
    assert medical.main()==1


def test_failed_verification_does_not_overwrite_advanced_human_review(tmp_path,monkeypatch):
    db=database(tmp_path,monkeypatch)
    row,state=medical.load_chain("chain1")
    with medical.connect() as c:
        c.execute("UPDATE content_ladder SET stage='G',status='awaiting_human_review',state_json=? WHERE chain_id='chain1'",
                  ('{"human_review_status":"PENDING"}',))
    medical.save_evidence_run(row,state,"run1",[],{},{},"job1",None,[],[],"VERIFIER_FAILED")
    with sqlite3.connect(db) as c:
        stage,status,raw=c.execute("SELECT stage,status,state_json FROM content_ladder").fetchone()
        assert (stage,status)==("G","awaiting_human_review")
        assert json.loads(raw)["human_review_status"]=="PENDING"
        assert c.execute("SELECT count(*) FROM medical_evidence_runs").fetchone()[0]==1
