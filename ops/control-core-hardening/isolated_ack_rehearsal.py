#!/usr/bin/env python3
"""Exercise the staged ACK protocol in disposable socket-only MariaDB."""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import uuid

import pymysql
from pymysql.cursors import DictCursor

CANDIDATE_SHA256 = "7cb3d84c7010d4902c96cd2eee5cb1df43b050519abb7d962e7a08d5836721cb"


def run(candidate: Path):
    raw = candidate.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CANDIDATE_SHA256:
        raise ValueError("CANDIDATE_HASH_MISMATCH")
    tree = ast.parse(raw.decode())
    schema_node = next(n for n in tree.body if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == "SCHEMA" for t in n.targets))
    schema = next(s for s in ast.literal_eval(schema_node.value)
                  if "CREATE TABLE IF NOT EXISTS pending_external_sync" in s)
    directory = Path(tempfile.mkdtemp(prefix="ada-ack-rehearsal-", dir="/tmp"))
    directory.chmod(0o700)
    (directory / "DISPOSABLE_ONLY").write_text("ada-ack-rehearsal")
    data, sock = directory / "data", directory / "mysql.sock"
    server = None
    try:
        init = subprocess.run(["/usr/bin/mariadb-install-db", "--no-defaults",
                               "--datadir=" + str(data), "--auth-root-authentication-method=normal",
                               "--skip-test-db"], capture_output=True, text=True, timeout=30)
        if init.returncode:
            raise RuntimeError("DISPOSABLE_DB_INIT_FAILED")
        log = (directory / "server-output.log").open("w")
        server = subprocess.Popen(["/usr/sbin/mariadbd", "--no-defaults",
                                   "--datadir=" + str(data), "--socket=" + str(sock),
                                   "--pid-file=" + str(directory / "mysql.pid"),
                                   "--log-error=" + str(directory / "error.log"),
                                   "--skip-networking", "--innodb-buffer-pool-size=32M",
                                   "--innodb-log-file-size=8M", "--max-connections=8"],
                                  stdout=log, stderr=log)
        log.close()
        deadline = time.monotonic() + 20
        while not sock.exists():
            if server.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError("DISPOSABLE_DB_START_FAILED")
            time.sleep(0.1)

        def connect(database="ada_rehearsal"):
            if (directory / "DISPOSABLE_ONLY").read_text() != "ada-ack-rehearsal":
                raise RuntimeError("DISPOSABLE_MARKER_MISSING")
            return pymysql.connect(unix_socket=str(sock), user="root", database=database,
                                   cursorclass=DictCursor, autocommit=False,
                                   init_command="SET time_zone='+00:00'")
        c = connect(None)
        with c.cursor() as cur:
            cur.execute("SELECT @@skip_networking AS isolated, VERSION() AS version")
            environment = cur.fetchone()
            assert environment["isolated"] == 1
            cur.execute("CREATE DATABASE ada_rehearsal")
        c.commit(); c.close()
        c = connect()
        with c.cursor() as cur:
            cur.execute(schema)
        c.commit(); c.close()
        def now():
            return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
        ns = {"db": connect, "now": now, "dt": dt,
              "jid": lambda: str(uuid.uuid4()), "jdump": lambda v: json.dumps(v),
              "audit": lambda *args, **kwargs: None}
        for name in ("queue_external_sync", "claim_external_sync", "ack_external_sync"):
            node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
            exec(compile(ast.Module(body=[node], type_ignores=[]), "<staged-control-core>", "exec"), ns)

        def read(target):
            c = connect()
            try:
                with c.cursor() as cur:
                    cur.execute("SELECT * FROM pending_external_sync WHERE id=%s", (target,))
                    return cur.fetchone()
            finally:
                c.close()
        def deny(fn):
            try:
                fn()
            except RuntimeError:
                return
            raise AssertionError("STALE_ACK_WAS_ACCEPTED")

        row = ns["queue_external_sync"]("agiflow", "task_comment", "fixture-task",
                 "create_task_comment", {"content": "fixture"}, "fixture-idem", "fixture-stable")
        first = ns["claim_external_sync"]("fixture-worker", "agiflow", 30)
        assert first["attempts"] == 1
        target = first["id"]
        deny(lambda: ns["ack_external_sync"](target, "succeeded", worker_id="wrong-worker", claim_attempt=1))
        assert read(target)["status"] == "in_progress"
        c = connect()
        with c.cursor() as cur:
            cur.execute("UPDATE pending_external_sync SET lease_until=%s WHERE id=%s",
                        (now()-dt.timedelta(seconds=1), target))
        c.commit(); c.close()
        deny(lambda: ns["ack_external_sync"](target, "succeeded", worker_id="fixture-worker", claim_attempt=1))
        second = ns["claim_external_sync"]("fixture-worker", "agiflow", 30)
        assert second["attempts"] == 2
        deny(lambda: ns["ack_external_sync"](target, "succeeded", worker_id="fixture-worker", claim_attempt=1))
        result = ns["ack_external_sync"](target, "succeeded", "fixture-comment",
                                         worker_id="fixture-worker", claim_attempt=2)
        assert result["status"] == "succeeded"
        repeated = ns["ack_external_sync"](target, "succeeded", "fixture-comment",
                                           worker_id="fixture-worker", claim_attempt=2)
        assert repeated["status"] == "succeeded"
        assert ns["claim_external_sync"]("fixture-worker", "agiflow", 30) is None
        return {"production": False, "skip_networking": True,
                "mariadb_version": environment["version"], "wrong_owner_denied": True,
                "expired_lease_denied": True, "same_worker_old_attempt_denied": True,
                "current_attempt_ack_succeeded": True, "repeated_ack_no_reclaim": True,
                "candidate_sha256": CANDIDATE_SHA256, "disposable_destroyed": True}
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill(); server.wait(timeout=5)
        if directory.parent != Path("/tmp") or not directory.name.startswith("ada-ack-rehearsal-"):
            raise RuntimeError("DISPOSABLE_CLEANUP_SCOPE_INVALID")
        shutil.rmtree(directory)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.candidate), sort_keys=True))


if __name__ == "__main__":
    main()
