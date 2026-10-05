import importlib.util
import json
import os
import sys
import threading
import types
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "runtime" / "control-core-baseline" / "candidates" / "google-approval" / "control_core.py"

pymysql = types.ModuleType("pymysql")
pymysql.connect = lambda *args, **kwargs: None
pymysql_cursors = types.ModuleType("pymysql.cursors")
pymysql_cursors.DictCursor = object
pymysql.cursors = pymysql_cursors
sys.modules.setdefault("pymysql", pymysql)
sys.modules.setdefault("pymysql.cursors", pymysql_cursors)

spec = importlib.util.spec_from_file_location("control_core_google_approval_fixture", SOURCE)
core = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(core)


class Store:
    def __init__(self):
        self.tickets = {}
        self.events = []
        self.audits = []


class Cursor:
    def __init__(self, store):
        self.store = store
        self.result = []
        self.rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql, args=()):
        query = " ".join(sql.split())
        low = query.lower()
        self.result = []
        self.rowcount = 0

        if low.startswith("select * from ada_approval_tickets where task_run_id="):
            proposal_id = args[0]
            matches = [row for row in self.store.tickets.values() if row["task_run_id"] == proposal_id]
            matches.sort(key=lambda row: row["requested_at"], reverse=True)
            self.result = matches[:1]
            return

        if low.startswith("insert into ada_approval_tickets"):
            (
                ticket_id, proposal_id, tool_name, site_id, resource_id, payload_hash,
                snapshot_hash, context_receipt_id, dependency_hash, requested_by, expires_at,
            ) = args
            row = {
                "id": ticket_id,
                "task_run_id": proposal_id,
                "parent_job": None,
                "tool_name": tool_name,
                "site_id": site_id,
                "resource_id": resource_id,
                "payload_hash": payload_hash,
                "snapshot_hash": snapshot_hash,
                "context_receipt_id": context_receipt_id,
                "dependency_hash": dependency_hash,
                "state": "PENDING",
                "requested_by": requested_by,
                "requester_identity": "ms_robot_actor",
                "approved_by": None,
                "approver_identity": None,
                "approval_id": None,
                "one_time_token_hash": None,
                "requested_at": core.now(),
                "decided_at": None,
                "expires_at": expires_at,
                "consumed_at": None,
            }
            self.store.tickets[ticket_id] = row
            self.rowcount = 1
            return

        if low.startswith("insert into ada_approval_events"):
            self.store.events.append((query, args))
            self.rowcount = 1
            return

        if low.startswith("insert ignore into audit_log"):
            self.store.audits.append((query, args))
            self.rowcount = 1
            return

        if low.startswith("select * from ada_approval_tickets where id="):
            row = self.store.tickets.get(args[0])
            self.result = [row] if row else []
            return

        if low.startswith("select * from ada_approval_tickets where state="):
            state, limit = args
            matches = [row for row in self.store.tickets.values() if row["state"] == state]
            matches.sort(key=lambda row: row["requested_at"], reverse=True)
            self.result = matches[: int(limit)]
            return

        if "update ada_approval_tickets set state='expired'" in low:
            ticket = self.store.tickets[args[-1]]
            ticket["state"] = "EXPIRED"
            self.rowcount = 1
            return

        if "update ada_approval_tickets set state='granted'" in low:
            approver, approval_id, token_hash, decided_at, ticket_id = args
            ticket = self.store.tickets[ticket_id]
            ticket.update({
                "state": "GRANTED",
                "approved_by": approver,
                "approver_identity": "human_approver",
                "approval_id": approval_id,
                "one_time_token_hash": token_hash,
                "decided_at": decided_at,
            })
            self.rowcount = 1
            return

        if "update ada_approval_tickets set state='denied'" in low:
            approver, decided_at, ticket_id = args
            ticket = self.store.tickets[ticket_id]
            ticket.update({
                "state": "DENIED",
                "approved_by": approver,
                "approver_identity": "human_approver",
                "decided_at": decided_at,
            })
            self.rowcount = 1
            return

        if "update ada_approval_tickets set state='consumed'" in low:
            consumed_at, ticket_id = args
            ticket = self.store.tickets[ticket_id]
            ticket.update({"state": "CONSUMED", "consumed_at": consumed_at})
            self.rowcount = 1
            return

        raise AssertionError("unexpected SQL: " + query)

    def fetchone(self):
        return self.result[0] if self.result else None

    def fetchall(self):
        return list(self.result)


class Connection:
    def __init__(self, store):
        self.store = store

    def cursor(self):
        return Cursor(self.store)

    def commit(self):
        pass

    def close(self):
        pass


def request(base, path, token, method="GET", body=None):
    raw = None if body is None else json.dumps(body).encode()
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    if raw is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base + path, data=raw, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        return exc.code, json.load(exc)


def approval_payload():
    return {
        "proposal_id": str(uuid.uuid4()),
        "context_receipt_id": str(uuid.uuid4()),
        "project_id": "project-a",
        "action": "gsc.site.remove",
        "site_id": "example.com",
        "resource_id": "sc-domain:example.com",
        "payload_hash": "a" * 64,
        "snapshot_hash": "",
        "dependency_hash": "b" * 64,
        "requested_by": "user-a",
        "mutation_type": "DELETE",
        "capability": "google.gsc.site.remove",
        "ttl_seconds": 3600,
    }


def test_scoped_approval_tokens_payload_binding_and_one_time_consumption(monkeypatch):
    store = Store()
    monkeypatch.setattr(core, "db", lambda: Connection(store))
    monkeypatch.setenv("CONTROL_API_TOKEN", "broad-control-token")
    monkeypatch.setenv("CONTROL_MS_ROBOT_TOKEN", "ms-robot-limited-token")
    monkeypatch.setenv("CONTROL_APPROVAL_TOKEN", "human-approval-token")
    monkeypatch.setenv("CONTROL_APPROVAL_SIGNING_KEY", "s" * 64)

    server = core.ThreadingHTTPServer(("127.0.0.1", 0), core.API)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = "http://127.0.0.1:" + str(server.server_port)
    try:
        payload = approval_payload()

        code, _ = request(base, "/approvals", "broad-control-token", "POST", payload)
        assert code == 401

        code, created = request(base, "/approvals", "ms-robot-limited-token", "POST", payload)
        assert code == 201
        assert created["state"] == "PENDING"
        ticket_id = created["ticket_id"]

        code, replay = request(base, "/approvals", "ms-robot-limited-token", "POST", payload)
        assert code == 201
        assert replay["ticket_id"] == ticket_id

        changed = {**payload, "payload_hash": "c" * 64}
        code, conflict = request(base, "/approvals", "ms-robot-limited-token", "POST", changed)
        assert code == 409
        assert conflict["error"] == "approval_ticket_payload_conflict"

        code, _ = request(base, "/approvals?state=PENDING", "ms-robot-limited-token")
        assert code == 401
        code, listed = request(base, "/approvals?state=PENDING", "human-approval-token")
        assert code == 200
        assert listed["approvals"][0]["ticket_id"] == ticket_id

        code, _ = request(base, f"/approvals/{ticket_id}/grant", "ms-robot-limited-token", "POST", {"approver": "maziyar"})
        assert code == 401
        code, granted = request(base, f"/approvals/{ticket_id}/grant", "human-approval-token", "POST", {"approver": "maziyar"})
        assert code == 200
        assert granted["state"] == "GRANTED"
        assert store.tickets[ticket_id]["one_time_token_hash"]
        assert "one_time_token" not in granted

        code, _ = request(base, f"/approvals/{ticket_id}/proof", "human-approval-token", "POST", {})
        assert code == 401
        code, proof = request(base, f"/approvals/{ticket_id}/proof", "ms-robot-limited-token", "POST", {})
        assert code == 200
        assert proof["payload_hash"] == payload["payload_hash"]
        assert proof["one_time_token"]
        assert proof["one_time_token"] not in core.jdump(store.tickets[ticket_id])

        wrong = {**proof, "payload_hash": "d" * 64}
        code, mismatch = request(base, f"/approvals/{ticket_id}/consume", "ms-robot-limited-token", "POST", wrong)
        assert code == 409
        assert mismatch["error"] == "approval_payload_mismatch"

        code, consumed = request(base, f"/approvals/{ticket_id}/consume", "ms-robot-limited-token", "POST", proof)
        assert code == 200
        assert consumed["state"] == "CONSUMED"
        assert consumed["approval_ref"].startswith("ada:")

        code, replayed = request(base, f"/approvals/{ticket_id}/consume", "ms-robot-limited-token", "POST", proof)
        assert code == 409
        assert replayed["error"] == "approval_ticket_replay"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
