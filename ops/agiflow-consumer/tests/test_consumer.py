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

    def list_comments(self, task_id):
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
    def fail(task_id):
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
