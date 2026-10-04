from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

OPS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OPS))
import agiflow_external_sync_consumer as consumer
from circuit_gate import CircuitGate, GateError


def item():
    return {"id": "queue1", "stable_id": "queue1", "target_service": "agiflow",
            "entity_type": "task_comment", "operation": "create_task_comment",
            "entity_id": "task1", "idempotency_key": "event1",
            "payload_json": json.dumps({"task_ref": "task1", "content": "fact [sync:event1]"})}


class Core:
    def __init__(self):
        self.claims = 0
        self.acks = []
        self.fail_ack = False

    def claim(self):
        self.claims += 1
        return item()

    def ack(self, target, outcome, **kwargs):
        if self.fail_ack:
            raise OSError("lost ack")
        self.acks.append((target, outcome, kwargs))
        return {"status": outcome}


class Agiflow:
    def __init__(self):
        self.rows = []
        self.writes = 0
        self.probes = 0
        self.error = None
        self.lost_create_response = False

    def probe(self):
        self.probes += 1
        if self.error:
            raise self.error
        return {"ok": True}

    def list_comments(self, task_id, *, ensure_page_budget=None):
        return self.rows.copy()

    def create_comment(self, task_id, content):
        self.writes += 1
        self.rows.append({"id": "comment1", "content": content})
        if self.lost_create_response:
            self.lost_create_response = False
            raise consumer.ConnectorError("HTTP_TRANSPORT")
        return self.rows[-1]


def test_permanent_failure_survives_new_process_and_never_claims(tmp_path):
    path = tmp_path / "gate.json"
    core, adapter = Core(), Agiflow()
    adapter.error = consumer.ConnectorError("HTTP_403", retryable=False)
    with CircuitGate(path, clock=lambda: 100) as gate:
        result = gate.run(lambda: consumer.consume_one(core, adapter, enabled=True, mirror=False))
    assert result["status"] == "PARKED"
    assert core.claims == 0
    # A new process must not execute the supplied action, including its probe.
    code = "from circuit_gate import CircuitGate; import sys;\nwith CircuitGate(sys.argv[1]) as g: print(g.run(lambda: (_ for _ in ()).throw(AssertionError('called'))))"
    p = subprocess.run([sys.executable, "-c", code, str(path)], env={**os.environ, "PYTHONPATH": str(OPS)},
                       capture_output=True, text=True, check=True)
    assert "'status': 'PARKED'" in p.stdout
    assert adapter.probes == 1
    assert json.loads(path.read_text())["failure_count"] == 1
    assert path.stat().st_mode & 0o777 == 0o600


def test_transient_backoff_retries_after_deadline(tmp_path):
    path = tmp_path / "gate.json"
    calls = []
    def fail():
        calls.append(1)
        raise consumer.ConnectorError("HTTP_503")
    with CircuitGate(path, clock=lambda: 100) as gate:
        assert gate.run(fail)["retry_at"] == 160
    with CircuitGate(path, clock=lambda: 159) as gate:
        assert gate.run(fail)["status"] == "COOLDOWN"
    assert len(calls) == 1
    with CircuitGate(path, clock=lambda: 160) as gate:
        assert gate.run(fail)["retry_at"] == 280
    assert len(calls) == 2


def test_success_closes_transient_circuit(tmp_path):
    path = tmp_path / "gate.json"
    with CircuitGate(path, clock=lambda: 100) as gate:
        gate.run(lambda: {"status": "RETRYABLE", "claimed": True, "retryable": True, "reason": "HTTP_429"})
    with CircuitGate(path, clock=lambda: 160) as gate:
        result = gate.run(lambda: {"status": "NO_ELIGIBLE_UNIT", "claimed": False})
    assert result["status"] == "NO_ELIGIBLE_UNIT"
    assert json.loads(path.read_text())["state"] == "closed"


def test_reset_requires_successful_probe_and_never_runs_action(tmp_path):
    path = tmp_path / "gate.json"
    action = lambda: pytest.fail("reset drained queue")
    with CircuitGate(path) as gate:
        gate.run(lambda: {"status": "RETRYABLE", "reason": "HTTP_403", "retryable": False})
    def blocked():
        raise consumer.ConnectorError("HTTP_403", retryable=False)
    with CircuitGate(path) as gate:
        assert gate.run(action, reset_probe=blocked)["status"] == "PARKED"
    with CircuitGate(path) as gate:
        assert gate.run(action, reset_probe=lambda: {"ok": True}) == {"status": "RESET", "claimed": False}
    with CircuitGate(path) as gate:
        assert gate.run(lambda: {"status": "NO_ELIGIBLE_UNIT"})["status"] == "NO_ELIGIBLE_UNIT"


def test_concurrent_process_cannot_enter_consumer(tmp_path):
    path = tmp_path / "gate.json"
    code = "from circuit_gate import CircuitGate; import sys;\nwith CircuitGate(sys.argv[1]): pass"
    with CircuitGate(path):
        p = subprocess.run([sys.executable, "-c", code, str(path)], env={**os.environ, "PYTHONPATH": str(OPS)},
                           capture_output=True, text=True)
    assert p.returncode != 0
    assert "CONSUMER_ALREADY_RUNNING" in p.stderr


@pytest.mark.parametrize("content", ["{", "[]", '{"version":2}', '{"version":1,"state":"closed","failure_count":true,"retry_at":0}',
                                  '{"version":1,"state":"closed","failure_count":0,"retry_at":NaN}'])
def test_corrupt_state_fails_closed(tmp_path, content):
    path = tmp_path / "gate.json"
    path.write_text(content)
    with CircuitGate(path) as gate:
        with pytest.raises(GateError, match="CIRCUIT_STATE_INVALID"):
            gate.run(lambda: pytest.fail("corrupt state allowed IO"))
    assert path.read_text() == content


def test_symlink_state_is_rejected(tmp_path):
    real = tmp_path / "private"
    real.write_text('{"version":1,"state":"closed","failure_count":0,"retry_at":0}')
    path = tmp_path / "gate.json"
    path.symlink_to(real)
    with CircuitGate(path) as gate:
        with pytest.raises(GateError, match="CIRCUIT_STATE_INVALID"):
            gate.run(lambda: pytest.fail("followed symlink"))


@pytest.mark.parametrize("status,retryable", [(400,False),(401,False),(403,False),(404,False),
                                               (408,True),(429,True),(503,True)])
def test_http_error_is_typed_and_response_body_never_escapes(monkeypatch, status, retryable):
    def reject(*args, **kwargs):
        from io import BytesIO
        raise HTTPError("https://example.invalid", status, "secret-marker", {},
                        BytesIO(b'{"token":"secret-marker","retryable":false}'))
    monkeypatch.setattr(consumer.HTTP_OPENER, "open", reject)
    with pytest.raises(consumer.ConnectorError) as info:
        consumer._json_request("https://example.invalid", {}, headers={})
    assert info.value.code == f"HTTP_{status}"
    assert info.value.retryable is retryable
    assert "secret-marker" not in str(info.value)


def test_disabled_consumer_does_no_network_or_claim():
    core, adapter = Core(), Agiflow()
    assert consumer.consume_one(core, adapter, enabled=False)["status"] == "DISABLED"
    assert core.claims == adapter.probes == 0


def test_lost_create_response_replays_by_marker_without_duplicate():
    core, adapter = Core(), Agiflow()
    adapter.lost_create_response = True
    first = consumer.consume_one(core, adapter, enabled=True, mirror=False)
    assert first["status"] == "RETRYABLE"
    assert core.acks[-1][1] == "retry"
    second = consumer.consume_one(core, adapter, enabled=True, mirror=False)
    assert second["status"] == "DEDUPED_EXISTING"
    assert core.acks[-1][1] == "succeeded"
    assert adapter.writes == 1


def test_lost_ack_replays_by_marker_without_duplicate():
    core, adapter = Core(), Agiflow()
    core.fail_ack = True
    with pytest.raises(OSError):
        consumer.consume_one(core, adapter, enabled=True, mirror=False)
    core.fail_ack = False
    assert consumer.consume_one(core, adapter, enabled=True, mirror=False)["status"] == "DEDUPED_EXISTING"
    assert adapter.writes == 1


def test_duplicate_marker_is_conflict_and_never_writes():
    core, adapter = Core(), Agiflow()
    adapter.rows = [{"id": "one", "content": "[sync:event1]"}, {"id": "two", "content": "[sync:event1]"}]
    assert consumer.consume_one(core, adapter, enabled=True, mirror=False)["status"] == "CONFLICT"
    assert core.acks[-1][1] == "conflict"
    assert adapter.writes == 0


def test_permanent_failure_after_claim_retains_retry_in_authoritative_queue(tmp_path):
    core, adapter = Core(), Agiflow()
    def fail(task_id, *, ensure_page_budget=None):
        raise consumer.ConnectorError("HTTP_401", retryable=False)
    adapter.list_comments = fail
    with CircuitGate(tmp_path / "gate.json") as gate:
        result = gate.run(lambda: consumer.consume_one(core, adapter, enabled=True, mirror=False))
    assert result["status"] == "PARKED" and result["claimed"] is True
    assert core.acks[-1][1] == "retry"
    assert adapter.writes == 0


def test_cli_disabled_does_not_create_state(tmp_path):
    path = tmp_path / "gate.json"
    env = dict(os.environ)
    env["AGIFLOW_CONSUMER_ENABLED"] = "false"
    p = subprocess.run([sys.executable, str(OPS / "agiflow_external_sync_consumer.py"), "--once", "--circuit-state", str(path)],
                       env=env, capture_output=True, text=True, check=True)
    assert json.loads(p.stdout) == {"status": "DISABLED", "claimed": False}
    assert not path.exists()


def test_error_diagnostics_are_safe(tmp_path):
    path = tmp_path / "gate.json"
    def fail():
        raise RuntimeError("private-token and patient-data")
    with CircuitGate(path) as gate:
        result = gate.run(fail)
    assert "private-token" not in json.dumps(result)
    assert "private-token" not in path.read_text()


def test_redirect_refuses_credential_forwarding():
    req = consumer.urllib.request.Request("https://example.invalid", headers={"x-api-key":"fixture"})
    with pytest.raises(consumer.ConnectorError) as info:
        consumer.RejectRedirects().redirect_request(req, None, 302, "", {}, "https://other.invalid")
    assert info.value.code == "HTTP_REDIRECT_REFUSED"
    assert info.value.retryable is False


def test_http_client_ack_binds_server_claim(monkeypatch):
    client=consumer.HttpControlCoreClient("http://127.0.0.1:8770","fixture")
    seen=[]
    def post(path,payload):
        seen.append((path,payload))
        return {"id":"row1","stable_id":"stable1","attempts":3,"locked_by":consumer.WORKER_ID,
                "lease_until":(consumer.datetime.now(consumer.timezone.utc)+__import__("datetime").timedelta(seconds=180)).isoformat()}
    monkeypatch.setattr(client,"_post",post)
    client.claim()
    client.ack("stable1","succeeded")
    assert seen[-1][1]["worker_id"]==consumer.WORKER_ID
    assert seen[-1][1]["claim_attempt"]==3
    with pytest.raises(consumer.QueueError,match="ACK_CLAIM_BINDING_MISSING"):
        client.ack("different-record","succeeded")


@pytest.mark.parametrize("row", [{"id":"row1","attempts":1,"locked_by":"someone_else"},
                               {"id":"row1","attempts":True,"locked_by":consumer.WORKER_ID}])
def test_invalid_claim_binding_is_refused(monkeypatch,row):
    client=consumer.HttpControlCoreClient("http://127.0.0.1:8770","fixture")
    monkeypatch.setattr(client,"_post",lambda *args:row)
    with pytest.raises(consumer.QueueError,match="CLAIM_BINDING_INVALID"):
        client.claim()


def test_comment_create_is_denied_when_claim_budget_is_exhausted():
    core, adapter = Core(), Agiflow()
    def expired():
        raise consumer.QueueError("CLAIM_LEASE_BUDGET_EXHAUSTED")
    core.ensure_write_budget = expired
    result = consumer.consume_one(core, adapter, enabled=True, mirror=False)
    assert result["status"] == "RETRYABLE"
    assert adapter.writes == 0
    assert core.acks[-1][1] == "retry"


def test_http_ack_is_refused_after_local_lease_deadline(monkeypatch):
    core = consumer.HttpControlCoreClient("http://127.0.0.1:8770", "fixture")
    core.claim_target = "row1"
    core.claim_attempt = 2
    core.claim_deadline = consumer.time.monotonic() - 1
    monkeypatch.setattr(core, "_post", lambda *args: pytest.fail("expired ACK sent"))
    with pytest.raises(consumer.QueueError, match="CLAIM_LEASE_BUDGET_EXHAUSTED"):
        core.ack("row1", "succeeded")


def test_queue_binding_error_does_not_park_healthy_connector(tmp_path):
    path = tmp_path / "gate.json"
    def invalid_binding():
        raise consumer.QueueError("CLAIM_BINDING_INVALID")
    with CircuitGate(path) as gate:
        result = gate.run(invalid_binding)
    assert result["status"] == "QUEUE_ERROR"
    with CircuitGate(path) as gate:
        assert gate.run(lambda: {"status": "NO_ELIGIBLE_UNIT"})["status"] == "NO_ELIGIBLE_UNIT"


def test_core_http_conflict_does_not_park_agiflow(monkeypatch, tmp_path):
    from io import BytesIO
    def reject(*args, **kwargs):
        raise HTTPError("http://127.0.0.1:8770", 409, "fixture", {}, BytesIO(b'{}'))
    monkeypatch.setattr(consumer.HTTP_OPENER, "open", reject)
    core = consumer.HttpControlCoreClient("http://127.0.0.1:8770", "fixture")
    with CircuitGate(tmp_path / "gate.json") as gate:
        result = gate.run(core.claim)
    assert result["status"] == "QUEUE_ERROR"
    assert result["reason"] == "HTTP_409"


def test_core_null_claim_reports_empty_without_cooldown(monkeypatch, tmp_path):
    from io import BytesIO
    class Response(BytesIO):
        status = 200
        headers = {"Content-Type": "application/json"}
    monkeypatch.setattr(consumer.HTTP_OPENER, "open", lambda *a, **k: Response(b'null'))
    core = consumer.HttpControlCoreClient("http://127.0.0.1:8770", "fixture")
    adapter = Agiflow()
    with CircuitGate(tmp_path / "gate.json") as gate:
        result = gate.run(lambda: consumer.consume_one(core, adapter, enabled=True, mirror=False))
    assert result["status"] == "NO_ELIGIBLE_UNIT"
    assert json.loads((tmp_path / "gate.json").read_text())["state"] == "closed"


def test_failed_reset_probe_preserves_permanent_latch(tmp_path):
    path = tmp_path / "gate.json"
    with CircuitGate(path, clock=lambda: 100) as gate:
        gate.run(lambda: {"status": "RETRYABLE", "reason": "HTTP_403", "retryable": False})
    def unavailable():
        raise consumer.ConnectorError("HTTP_503")
    with CircuitGate(path, clock=lambda: 101) as gate:
        assert gate.run(lambda: pytest.fail("reset ran queue"), reset_probe=unavailable)["status"] == "PARKED"
    with CircuitGate(path, clock=lambda: 1000) as gate:
        assert gate.run(lambda: pytest.fail("failed reset reopened parked consumer"))["status"] == "PARKED"


@pytest.mark.parametrize("matching", [True, False])
def test_large_comment_history_reconciles_seen_marker_without_unsafe_create(monkeypatch, matching):
    client = consumer.StatelessAgiflowMcpClient("https://example.invalid", "fixture")
    rows = [{"id": "existing1", "content": "fact [sync:event1]" if matching else "other"}]
    def call(request_id, name, args):
        if name == "list_task_comments":
            return {"comments": rows, "total": 10000}
        pytest.fail("incomplete history allowed comment creation")
    monkeypatch.setattr(client, "_call_tool", call)
    monkeypatch.setattr(client, "probe", lambda: {"ok": True})
    core = Core()
    result = consumer.consume_one(core, client, enabled=True, mirror=False)
    assert result["status"] == ("DEDUPED_EXISTING" if matching else "QUARANTINED")
    assert core.acks[-1][1] == ("succeeded" if matching else "quarantined")
    if not matching:
        assert result["owner_action_required"] is True
        assert result["reason"] == "COMMENT_SCAN_LIMIT_EXCEEDED"


def test_incomplete_history_stops_rescanning_after_queue_quarantine(tmp_path):
    class DurableCore(Core):
        def __init__(self):
            super().__init__()
            self.path = tmp_path / "queue.json"
            self.path.write_text(json.dumps({"state": "pending"}))
        def claim(self):
            self.claims += 1
            return item() if json.loads(self.path.read_text())["state"] == "pending" else None
        def ack(self, target, outcome, **kwargs):
            result = super().ack(target, outcome, **kwargs)
            self.path.write_text(json.dumps({"state": outcome}))
            return result
    class LargeHistory(Agiflow):
        def __init__(self):
            super().__init__()
            self.scans = 0
        def list_comments(self, task_id, *, ensure_page_budget=None):
            self.scans += 1
            return consumer.CommentScan([], complete=False)
    core, adapter = DurableCore(), LargeHistory()
    result = consumer.consume_one(core, adapter, enabled=True, mirror=False)
    assert result["status"] == "QUARANTINED"
    # Reopen durable queue state: normal eligibility never includes quarantine.
    restarted = DurableCore.__new__(DurableCore)
    Core.__init__(restarted)
    restarted.path = core.path
    assert consumer.consume_one(restarted, adapter, enabled=True, mirror=False)["status"] == "NO_ELIGIBLE_UNIT"
    assert adapter.scans == 1
    assert adapter.writes == 0


def test_incomplete_postcreate_verification_quarantines_unknown_outcome():
    core, adapter = Core(), Agiflow()
    scans = iter([consumer.CommentScan([], complete=True), consumer.CommentScan([], complete=False)])
    adapter.list_comments = lambda task_id, ensure_page_budget=None: next(scans)
    result = consumer.consume_one(core, adapter, enabled=True, mirror=False)
    assert adapter.writes == 1
    assert result["status"] == "QUARANTINED"
    assert result["phase"] == "verify"
    assert result["owner_action_required"] is True
    assert core.acks[-1][1] == "quarantined"


def test_incomplete_scan_does_not_quarantine_healthy_connector(tmp_path):
    core, adapter = Core(), Agiflow()
    adapter.list_comments = lambda task_id, ensure_page_budget=None: consumer.CommentScan([], complete=False)
    with CircuitGate(tmp_path / "gate.json") as gate:
        result = gate.run(lambda: consumer.consume_one(core, adapter, enabled=True, mirror=False))
    assert result["status"] == "QUARANTINED"
    assert json.loads((tmp_path / "gate.json").read_text())["state"] == "closed"


def test_permanent_provider_denial_survives_failed_queue_ack(tmp_path):
    core, adapter = Core(), Agiflow()
    def denied(task, *, ensure_page_budget=None):
        raise consumer.ConnectorError("HTTP_403", retryable=False)
    def ack_failed(*args, **kwargs):
        raise consumer.QueueError("HTTP_503")
    adapter.list_comments = denied
    core.ack = ack_failed
    with CircuitGate(tmp_path / "gate.json") as gate:
        result = gate.run(lambda: consumer.consume_one(core, adapter, enabled=True, mirror=False))
    assert result["status"] == "PARKED"
    assert result["reason"] == "HTTP_403"


def test_missing_core_credential_does_not_park_connector(tmp_path, monkeypatch):
    monkeypatch.delenv("CONTROL_API_TOKEN", raising=False)
    with CircuitGate(tmp_path / "gate.json") as gate:
        result = gate.run(consumer.build_live_clients)
    assert result["status"] == "QUEUE_ERROR"
    assert result["reason"] == "CONTROL_API_TOKEN_MISSING"
    assert result["owner_action_required"] is True


@pytest.mark.parametrize("matching", [False, True])
@pytest.mark.parametrize("postcreate", [False, True])
@pytest.mark.parametrize("page_seconds", [3.3, 19.9])
def test_slow_pagination_reserves_quarantine_ack_lease(monkeypatch, postcreate, page_seconds, matching):
    clock = [0.0]
    monkeypatch.setattr(consumer.time, "monotonic", lambda: clock[0])
    core = consumer.HttpControlCoreClient("http://127.0.0.1:8770", "fixture")
    state = {"outcome": "pending", "pages": 0, "writes": 0, "acks": []}
    def claim():
        if state["outcome"] != "pending":
            return None
        core.claim_target, core.claim_attempt, core.claim_deadline = "queue1", 1, 180.0
        return item()
    def ack_post(path, payload):
        assert path == "/external-sync/queue1/ack"
        clock[0] += 19.9
        assert clock[0] < core.claim_deadline
        state["outcome"] = payload["outcome"]
        state["acks"].append(payload)
        return {"status": payload["outcome"]}
    monkeypatch.setattr(core, "claim", claim)
    monkeypatch.setattr(core, "_post", ack_post)
    adapter = consumer.StatelessAgiflowMcpClient("https://example.invalid", "fixture")
    monkeypatch.setattr(adapter, "probe", lambda: {"ok": True})
    def call(request_id, name, args):
        if name == "create_task_comment":
            state["writes"] += 1
            clock[0] += 19.9
            return {"id": "uncertain"}
        assert name == "list_task_comments"
        if postcreate and not state["writes"]:
            return {"comments": [], "total": 0}
        state["pages"] += 1
        clock[0] += page_seconds
        rows = [{"id": str(args["offset"] + i), "content": "other"} for i in range(100)]
        if matching and state["pages"] == 1:
            rows[0] = {"id": "observed", "content": "fact [sync:event1]"}
        return {"comments": rows, "total": 6000}
    monkeypatch.setattr(adapter, "_call_tool", call)
    result = consumer.consume_one(core, adapter, enabled=True, mirror=False)
    assert result["status"] == (("SUCCEEDED" if postcreate else "DEDUPED_EXISTING") if matching else "QUARANTINED")
    if not matching:
        assert result["phase"] == ("verify" if postcreate else "precheck")
        assert result["reason"] == "COMMENT_SCAN_LEASE_BUDGET_EXHAUSTED"
    assert state["writes"] == int(postcreate)
    assert len(state["acks"]) == 1
    assert state["acks"][0]["claim_attempt"] == 1
    assert state["acks"][0]["worker_id"] == consumer.WORKER_ID
    assert state["pages"] < 50
    pages = state["pages"]
    assert consumer.consume_one(core, adapter, enabled=True, mirror=False)["status"] == "NO_ELIGIBLE_UNIT"
    assert state["pages"] == pages

@pytest.mark.parametrize("postcreate", [False, True])
def test_marker_with_changed_content_is_conflict_not_delivery(postcreate):
    core, adapter = Core(), Agiflow()
    changed = {"id": "comment1", "content": "human correction [sync:event1]"}
    if postcreate:
        def create(task_id, content):
            adapter.writes += 1
            adapter.rows.append(changed)
            return changed
        adapter.create_comment = create
    else:
        adapter.rows = [changed]
    result = consumer.consume_one(core, adapter, enabled=True, mirror=False)
    assert result["status"] == "CONFLICT"
    assert result["reason"] == "DURABLE_MARKER_CONTENT_MISMATCH"
    assert core.acks[-1][1] == "conflict"
    assert adapter.rows == [changed]  # Never overwrite the human's edit.
    assert adapter.writes == int(postcreate)
    assert "human correction" not in json.dumps(result)


def test_lost_create_then_human_edit_cannot_be_acknowledged_as_original():
    core, adapter = Core(), Agiflow()
    adapter.lost_create_response = True
    assert consumer.consume_one(core, adapter, enabled=True, mirror=False)["status"] == "RETRYABLE"
    adapter.rows[0]["content"] = "changed after uncertain write [sync:event1]"
    result = consumer.consume_one(core, adapter, enabled=True, mirror=False)
    assert result["status"] == "CONFLICT"
    assert adapter.writes == 1
    assert core.acks[-1][1] == "conflict"


@pytest.mark.parametrize("page", [
    {}, {"total": 0}, {"comments": None, "total": 0},
    {"comments": False, "total": 0},
    {"comments": [None], "total": 1},
    {"comments": [{"id": "one"}], "total": 1},
    {"comments": [{"content": "text"}], "total": 1},
    {"comments": [{"id": "one", "content": 42}], "total": 1},
    {"comments": [{"id": "one", "content": "text", "taskId": "another-task"}], "total": 1},
    {"comments": [], "total": -1}, {"comments": [], "total": True},
    {"comments": [], "total": "0"},
    {"comments": [{"id": "one", "content": "text"}], "total": 0},
])
def test_malformed_history_never_authorises_a_new_comment(monkeypatch, page):
    core = Core()
    adapter = consumer.StatelessAgiflowMcpClient("https://example.invalid", "fixture")
    monkeypatch.setattr(adapter, "probe", lambda: {"ok": True})
    writes = []
    def call(request_id, name, args):
        if name == "create_task_comment":
            writes.append(args)
            return {"id": "unexpected"}
        return page
    monkeypatch.setattr(adapter, "_call_tool", call)
    result = consumer.consume_one(core, adapter, enabled=True, mirror=False)
    assert writes == [], "malformed history allowed a write"
    assert result["status"] == "RETRYABLE"
    assert core.acks[-1][1] == "retry"


def test_structured_mcp_payload_is_used_before_display_text():
    payload = {"comments": [{"id": "one", "content": "fact [sync:event1]"}], "total": 1}
    result = {"structuredContent": payload, "content": [{"type": "text", "text": "Action completed."}]}
    assert consumer.StatelessAgiflowMcpClient._tool_payload(result) == payload


@pytest.mark.parametrize("result", [
    {"content": []},
    {"structuredContent": None, "content": []},
    {"structuredContent": [], "content": [{"type": "text", "text": "{}"}]},
])
def test_missing_or_malformed_mcp_payload_is_not_an_empty_history(result):
    with pytest.raises(consumer.ConnectorError):
        consumer.StatelessAgiflowMcpClient._tool_payload(result)


def test_tool_error_does_not_accept_successful_looking_structured_payload():
    with pytest.raises(consumer.ConnectorError, match="MCP_TOOL_ERROR"):
        consumer.StatelessAgiflowMcpClient._tool_payload({
            "isError": True, "structuredContent": {"comments": [], "total": 0}})


def test_repeated_comment_ids_cannot_complete_an_offset_scan(monkeypatch):
    adapter = consumer.StatelessAgiflowMcpClient("https://example.invalid", "fixture")
    rows = [{"id": str(i), "content": "other"} for i in range(100)]
    monkeypatch.setattr(adapter, "_call_tool", lambda *args: {"comments": rows, "total": 200})
    result = adapter.list_comments("task1")
    assert result.complete is False
    assert result.reason == "COMMENT_SCAN_UNSTABLE"

@pytest.mark.parametrize("postcreate", [False, True])
def test_unstable_history_cannot_reconcile_even_a_seen_exact_marker(postcreate):
    core, adapter = Core(), Agiflow()
    exact = {"id": "one", "content": "fact [sync:event1]"}
    unstable = consumer.CommentScan([exact], complete=False, reason="COMMENT_SCAN_UNSTABLE")
    scans = iter([consumer.CommentScan([], complete=True), unstable] if postcreate else [unstable])
    adapter.list_comments = lambda task_id, ensure_page_budget=None: next(scans)
    result = consumer.consume_one(core, adapter, enabled=True, mirror=False)
    assert result["status"] == "QUARANTINED"
    assert result["reason"] == "COMMENT_SCAN_UNSTABLE"
    assert core.acks[-1][1] == "quarantined"
    assert adapter.writes == int(postcreate)


def test_total_change_marks_comment_history_unstable(monkeypatch):
    adapter = consumer.StatelessAgiflowMcpClient("https://example.invalid", "fixture")
    pages = iter([
        {"comments": [{"id": str(i), "content": "other"} for i in range(100)], "total": 101},
        {"comments": [{"id": "100", "content": "other"}], "total": 102},
    ])
    monkeypatch.setattr(adapter, "_call_tool", lambda *args: next(pages))
    result = adapter.list_comments("task1")
    assert result.complete is False
    assert result.reason == "COMMENT_SCAN_UNSTABLE"
