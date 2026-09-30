from __future__ import annotations
import ast
import copy
import datetime as dt
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("ack_patch",ROOT/"prepare_ack_patch.py")
patch=importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
NOW=dt.datetime(2026,9,30,12)
ROW={"id":"row1","stable_id":"stable1","target_service":"agiflow","entity_type":"task_comment",
     "entity_id":"task1","status":"in_progress","locked_by":"worker1","attempts":2,"max_attempts":5,
     "lease_until":NOW+dt.timedelta(seconds=30),"available_at":NOW,"expected_external_version":None}


class Cursor:
    def __init__(self,row,lose_update=False):
        self.row=copy.deepcopy(row)
        self.rowcount=0
        self.writes=[]
        self.lose_update=lose_update
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def execute(self,sql,args):
        if sql.lstrip().startswith("UPDATE"):
            if self.lose_update:
                self.rowcount=0
                return
            # Treat the SQL predicate as a contract with values independent
            # of the function's owner/attempt branch.
            assert "AND status='in_progress' AND locked_by=%s AND attempts=%s AND lease_until>%s" in sql
            assert args[6:]==(self.row["locked_by"],self.row["attempts"],NOW)
            self.writes.append(args)
            self.row["status"]=args[0]
            self.rowcount=1
    def fetchone(self):return copy.deepcopy(self.row)


def function(row=None,lose_update=False):
    source=patch.transform((ROOT/"tests/baseline_ack.py").read_text())
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=="ack_external_sync")
    cursor=Cursor(ROW if row is None else row,lose_update)
    conn=SimpleNamespace(cursor=lambda:cursor,commit=lambda:None,close=lambda:None)
    ns={"db":lambda:conn,"now":lambda:NOW,"dt":dt,"audit":lambda *args:None}
    exec(compile(ast.Module(body=[node],type_ignores=[]),"<isolated-ack>","exec"),ns)
    return ns["ack_external_sync"],cursor


@pytest.mark.parametrize("worker,attempt", [(None,None),("worker1",None),("worker1",True),("worker1","2"),
                                           ("worker1",1),("stale_worker",2)])
def test_unbound_or_stale_ack_cannot_change_queue(worker,attempt):
    ack,cursor=function()
    with pytest.raises(RuntimeError):
        ack("row1","succeeded",worker_id=worker,claim_attempt=attempt)
    assert cursor.writes==[]


@pytest.mark.parametrize("expiry", [None,NOW,NOW-dt.timedelta(seconds=1)])
def test_expired_lease_cannot_ack(expiry):
    ack,cursor=function({**ROW,"lease_until":expiry})
    with pytest.raises(RuntimeError,match="lease expired"):
        ack("row1","succeeded",worker_id="worker1",claim_attempt=2)
    assert cursor.writes==[]


def test_current_owner_attempt_can_ack():
    ack,cursor=function()
    assert ack("row1","succeeded",observed_external_version="comment1",
               worker_id="worker1",claim_attempt=2)["status"]=="succeeded"
    assert len(cursor.writes)==1


def test_reclaim_by_same_worker_fences_old_attempt():
    ack,cursor=function({**ROW,"attempts":3})
    with pytest.raises(RuntimeError,match="attempt lost"):
        ack("row1","succeeded",worker_id="worker1",claim_attempt=2)
    assert cursor.writes==[]


def test_conditional_write_failure_is_not_success():
    ack,cursor=function(lose_update=True)
    with pytest.raises(RuntimeError,match="lease ownership lost"):
        ack("row1","succeeded",worker_id="worker1",claim_attempt=2)
    assert cursor.writes==[]


def test_legacy_other_target_keeps_existing_api():
    ack,cursor=function({**ROW,"target_service":"clickup"})
    assert ack("row1","succeeded")["status"]=="succeeded"


def test_terminal_repeated_ack_does_no_write():
    ack,cursor=function({**ROW,"status":"succeeded","locked_by":None,"lease_until":None})
    assert ack("row1","succeeded",worker_id="worker1",claim_attempt=2)["status"]=="succeeded"
    assert cursor.writes==[]


def test_hash_mismatch_refuses_candidate():
    with pytest.raises(ValueError,match="LIVE_BASELINE_CHANGED"):
        patch.prepare(b"arbitrary code")


def test_changed_anchor_fails_closed():
    with pytest.raises(ValueError,match="SOURCE_ANCHOR_MISMATCH"):
        patch.transform((ROOT/"tests/baseline_ack.py").read_text().replace(patch.HEADER,"changed"))


def test_http_endpoint_forwards_fence():
    source=patch.transform((ROOT/"tests/baseline_ack.py").read_text())
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=="endpoint")
    seen=[]
    ns={"ack_external_sync":lambda *a,**kw:seen.append((a,kw))}
    exec(compile(ast.Module(body=[node],type_ignores=[]),"<http-adapter>","exec"),ns)
    ns["endpoint"](["","external-sync","row1","ack"],{"outcome":"succeeded","worker_id":"worker1","claim_attempt":2})
    assert seen[0][1]=={"worker_id":"worker1","claim_attempt":2}
