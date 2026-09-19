#!/usr/bin/env python3
"""AAX-7 isolated MariaDB rehearsal. NEVER production.

Requires a local unix socket of a disposable mariadbd started with
--skip-networking. Refuses TCP, remote hosts, default 3306, and missing
sockets. Does not read production env files.

Usage (example, disposable instance only):

  ADA_REHEARSAL_SOCKET=/tmp/ada-rehearsal.sock \\
  MARIADB_CLIENT=/path/to/mariadb \\
  python3 isolated_mariadb_rehearsal.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SQL_DIR = REPO / "ada-reliability" / "sql" / "mariadb"
LIVE_SOURCE = REPO / "runtime" / "control-core-baseline" / "live" / "control_core.py"
MIGRATIONS = (
    "001_ada_memory.sql",
    "002_ada_receipts_passports.sql",
    "003_ada_approvals_journal.sql",
    "004_ada_qalam_eval.sql",
    "005_ada_agiflow_projection.sql",
    "006_ada_failed_run_outbox.sql",
)
PROTECTED = (
    "jobs",
    "schedules",
    "job_results",
    "dead_letter_queue",
    "pending_external_sync",
    "audit_log",
)
DB = "ada_isolated_rehearsal"
CREATE_RE = re.compile(r"CREATE TABLE IF NOT EXISTS\s+`?([A-Za-z0-9_]+)`?", re.I)


def fail(msg: str, code: int = 2) -> None:
    print("isolated-rehearsal: " + msg, file=sys.stderr)
    raise SystemExit(code)


def require_socket() -> Path:
    raw = os.environ.get("ADA_REHEARSAL_SOCKET", "")
    if not raw:
        fail("ADA_REHEARSAL_SOCKET is required")
    if "://" in raw or raw.startswith("tcp") or ":" in raw.replace(":", "", 0) and raw.count(":") == 1 and not raw.startswith("/"):
        fail("refusing TCP/DSN socket: " + raw)
    path = Path(raw)
    if not str(path).startswith("/tmp/"):
        fail("socket must be under /tmp/ (disposable): " + raw)
    if not path.is_socket():
        fail("not a unix socket: " + raw)
    return path


def client_bin() -> str:
    env = os.environ.get("MARIADB_CLIENT")
    if env:
        return env
    for cand in ("mariadb", "mysql"):
        from shutil import which

        found = which(cand)
        if found:
            return found
    fail("mariadb client not found; set MARIADB_CLIENT")


def run_sql(client: str, sock: Path, sql: str, db: str | None = None) -> str:
    cmd = [client, f"--socket={sock}", "-N", "-B", "--batch"]
    if db:
        cmd += ["-D", db]
    proc = subprocess.run(cmd, input=sql, text=True, capture_output=True)
    if proc.returncode != 0:
        fail(f"sql failed ({proc.returncode}): {proc.stderr.strip()}\nSQL:\n{sql[:500]}")
    return proc.stdout


def source_file(client: str, sock: Path, db: str, path: Path) -> None:
    cmd = [client, f"--socket={sock}", "-D", db]
    proc = subprocess.run(cmd, input=path.read_text(encoding="utf-8"), text=True, capture_output=True)
    if proc.returncode != 0:
        fail(f"source {path.name} failed: {proc.stderr.strip()}")


def live_schema_sql() -> str:
    text = LIVE_SOURCE.read_text(encoding="utf-8")
    start = text.find("SCHEMA = [")
    if start < 0:
        fail("SCHEMA list missing from live control_core.py")
    end = text.find("]\n\n\ndef init_db", start)
    if end < 0:
        end = text.find("]\n\ndef init_db", start)
    if end < 0:
        fail("could not bound SCHEMA list")
    blob = text[start:end]
    stmts = re.findall(r'"""(.*?)"""', blob, re.S)
    if len(stmts) < 10:
        fail(f"expected live CREATE TABLE statements, got {len(stmts)}")
    return ";\n".join(s.strip().rstrip(";") for s in stmts) + ";\n"


def tables(client: str, sock: Path, db: str) -> list[str]:
    out = run_sql(client, sock, "SHOW TABLES;", db)
    return [line.strip() for line in out.splitlines() if line.strip()]


def create_sql(client: str, sock: Path, db: str, name: str) -> str:
    out = run_sql(client, sock, f"SHOW CREATE TABLE `{name}`\\G", db)
    return out


def checksums(client: str, sock: Path, db: str, names: tuple[str, ...]) -> dict[str, str]:
    got = {}
    for name in names:
        body = create_sql(client, sock, db, name)
        got[name] = hashlib.sha256(body.encode()).hexdigest()
    return got


def seed_sql() -> str:
    return """
INSERT INTO jobs (
  id, stable_id, idempotency_key, agent, job_type, payload_json, status,
  priority, attempts, max_attempts, available_at
) VALUES (
  'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  'job:rehearsal-echo',
  'idem-rehearsal-echo',
  'TEST',
  'test.echo',
  '{"rehearsal":true}',
  'queued',
  100, 0, 5, NOW(6)
);
INSERT INTO schedules (
  id, stable_id, agent, job_type, payload_json, interval_seconds, enabled, next_run_at
) VALUES (
  'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
  'schedule:rehearsal-echo',
  'TEST',
  'test.echo',
  '{"rehearsal":true}',
  300, 1, NOW(6)
);
INSERT INTO pending_external_sync (
  id, stable_id, target_service, entity_type, entity_id, operation,
  payload_json, idempotency_key, status, attempts, max_attempts, available_at
) VALUES (
  'cccccccc-cccc-cccc-cccc-cccccccccccc',
  'sync:rehearsal-1',
  'agiflow',
  'task',
  'rehearsal',
  'comment',
  '{"rehearsal":true}',
  'idem-sync-rehearsal-1',
  'pending',
  0, 5, NOW(6)
);
INSERT INTO audit_log (
  id, stable_id, actor, action, details_json
) VALUES (
  'dddddddd-dddd-dddd-dddd-dddddddddddd',
  'audit:rehearsal-1',
  'rehearsal',
  'seed',
  '{"rehearsal":true}'
);
"""


def expect_error(client: str, sock: Path, db: str, sql: str, needle: str) -> str:
    cmd = [client, f"--socket={sock}", "-D", db]
    proc = subprocess.run(cmd, input=sql, text=True, capture_output=True)
    blob = (proc.stderr or "") + (proc.stdout or "")
    if proc.returncode == 0:
        fail(f"expected error containing {needle!r}, SQL succeeded:\n{sql}")
    if needle.lower() not in blob.lower() and "duplicate" not in blob.lower():
        fail(f"expected duplicate/unique error, got: {blob}")
    return blob.splitlines()[-1] if blob else "error"


def main() -> int:
    sock = require_socket()
    client = client_bin()
    skip_net = run_sql(client, sock, "SHOW VARIABLES LIKE 'skip_networking';")
    if "ON" not in skip_net.upper() and "1" not in skip_net.split():
        fail("refusing rehearsal: skip_networking is not ON")
    version = run_sql(client, sock, "SELECT VERSION();").strip()
    run_sql(client, sock, f"DROP DATABASE IF EXISTS `{DB}`; CREATE DATABASE `{DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")

    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as fh:
        fh.write(live_schema_sql())
        schema_path = Path(fh.name)
    try:
        source_file(client, sock, DB, schema_path)
    finally:
        schema_path.unlink(missing_ok=True)
    run_sql(client, sock, seed_sql(), DB)

    before_tables = tables(client, sock, DB)
    before_hash = checksums(client, sock, DB, PROTECTED)
    job_count = run_sql(client, sock, "SELECT COUNT(*) FROM jobs;", DB).strip()
    sched_count = run_sql(client, sock, "SELECT COUNT(*) FROM schedules;", DB).strip()
    sync_count = run_sql(client, sock, "SELECT COUNT(*) FROM pending_external_sync;", DB).strip()

    applied = []
    for name in MIGRATIONS:
        path = SQL_DIR / name
        if not path.is_file():
            fail("missing migration " + name)
        source_file(client, sock, DB, path)
        applied.append(name)
        # IF NOT EXISTS / INSERT IGNORE must be re-runnable.
        source_file(client, sock, DB, path)

    after_tables = tables(client, sock, DB)
    after_hash = checksums(client, sock, DB, PROTECTED)
    if after_hash != before_hash:
        fail("PROTECTED table CREATE SQL changed after 001-006")
    if run_sql(client, sock, "SELECT COUNT(*) FROM jobs;", DB).strip() != job_count:
        fail("jobs row count changed")
    if run_sql(client, sock, "SELECT COUNT(*) FROM schedules;", DB).strip() != sched_count:
        fail("schedules row count changed")
    if run_sql(client, sock, "SELECT COUNT(*) FROM pending_external_sync;", DB).strip() != sync_count:
        fail("pending_external_sync row count changed")

    ada = sorted(t for t in after_tables if t.startswith("ada_"))
    if not ada:
        fail("no ada_* tables after apply")
    if any(t.startswith("ada_") for t in before_tables):
        fail("ada_* existed before apply")
    live_only = [t for t in after_tables if not t.startswith("ada_")]
    if sorted(live_only) != sorted(before_tables):
        fail("non-ada table set changed: " + str(live_only))

    dup_job = expect_error(
        client,
        sock,
        DB,
        """INSERT INTO jobs (
          id, stable_id, idempotency_key, agent, job_type, payload_json, status,
          priority, attempts, max_attempts, available_at
        ) VALUES (
          'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
          'job:rehearsal-echo-2',
          'idem-rehearsal-echo',
          'TEST', 'test.echo', '{}', 'queued', 100, 0, 5, NOW(6)
        );""",
        "duplicate",
    )
    run_sql(
        client,
        sock,
        """INSERT INTO ada_policy_releases (component, `release`, content_hash, status)
           VALUES ('qalam', 'r1', REPEAT('a',64), 'ACTIVE');""",
        DB,
    )
    dup_active = expect_error(
        client,
        sock,
        DB,
        """INSERT INTO ada_policy_releases (component, `release`, content_hash, status)
           VALUES ('qalam', 'r2', REPEAT('b',64), 'ACTIVE');""",
        "duplicate",
    )
    run_sql(
        client,
        sock,
        """INSERT INTO ada_failed_runs (
          id, idempotency_key, run_id, worker, failure_class, failure_reason,
          lifecycle, first_failed_at, last_failed_at, sync_marker, payload
        ) VALUES (
          'ffffffff-ffff-ffff-ffff-ffffffffffff',
          REPEAT('c',64),
          'run-1',
          'rehearsal',
          'test',
          'isolated',
          'queued',
          NOW(6), NOW(6),
          'marker',
          '{}'
        );""",
        DB,
    )
    dup_fail = expect_error(
        client,
        sock,
        DB,
        """INSERT INTO ada_failed_runs (
          id, idempotency_key, run_id, worker, failure_class, failure_reason,
          lifecycle, first_failed_at, last_failed_at, sync_marker, payload
        ) VALUES (
          'ffffffff-ffff-ffff-ffff-fffffffffffe',
          REPEAT('c',64),
          'run-2',
          'rehearsal',
          'test',
          'isolated',
          'queued',
          NOW(6), NOW(6),
          'marker',
          '{}'
        );""",
        "duplicate",
    )
    cas = run_sql(
        client,
        sock,
        """UPDATE ada_failed_runs
              SET lifecycle='inflight', lease_owner='rehearsal', claim_generation=claim_generation+1
            WHERE id='ffffffff-ffff-ffff-ffff-ffffffffffff'
              AND lifecycle IN ('queued','retryable')
              AND claim_generation <=> 0;
           SELECT ROW_COUNT(), claim_generation FROM ada_failed_runs
            WHERE id='ffffffff-ffff-ffff-ffff-ffffffffffff';""",
        DB,
    )
    cas2 = run_sql(
        client,
        sock,
        """UPDATE ada_failed_runs
              SET lifecycle='inflight', lease_owner='other', claim_generation=claim_generation+1
            WHERE id='ffffffff-ffff-ffff-ffff-ffffffffffff'
              AND lifecycle IN ('queued','retryable')
              AND claim_generation <=> 0;
           SELECT ROW_COUNT();""",
        DB,
    )

    engines = run_sql(
        client,
        sock,
        """SELECT table_name, engine, table_collation
             FROM information_schema.tables
            WHERE table_schema=DATABASE() AND table_name LIKE 'ada_%'
            ORDER BY table_name;""",
        DB,
    )
    if "InnoDB" not in engines:
        fail("ada_* tables are not InnoDB")

    # Rollback: drop ada_* only.
    drop_list = run_sql(
        client,
        sock,
        """SELECT table_name FROM information_schema.tables
            WHERE table_schema=DATABASE() AND table_name LIKE 'ada_%';""",
        DB,
    )
    ada_to_drop = [n.strip() for n in drop_list.splitlines() if n.strip()]
    for name in ada_to_drop:
        if not name.startswith("ada_"):
            fail("refusing to drop non-ada table " + name)
        run_sql(client, sock, f"DROP TABLE `{name}`;", DB)

    rolled = tables(client, sock, DB)
    if any(t.startswith("ada_") for t in rolled):
        fail("ada_* remained after rollback")
    if sorted(rolled) != sorted(before_tables):
        fail(f"rollback table set mismatch: {rolled} vs {before_tables}")
    if checksums(client, sock, DB, PROTECTED) != before_hash:
        fail("PROTECTED CREATE SQL changed after rollback")
    if run_sql(client, sock, "SELECT COUNT(*) FROM jobs;", DB).strip() != job_count:
        fail("jobs changed after rollback")

    report = {
        "production": False,
        "skip_networking": True,
        "mariadb_version": version,
        "database": DB,
        "socket": str(sock),
        "live_source": str(LIVE_SOURCE.relative_to(REPO)),
        "applied": applied,
        "reapplied_idempotent": True,
        "protected_unchanged": True,
        "ada_tables_applied": ada,
        "ada_table_count": len(ada),
        "baseline_tables": sorted(before_tables),
        "duplicate_job_idempotency": dup_job,
        "duplicate_one_active_policy": dup_active,
        "duplicate_failed_run_idempotency": dup_fail,
        "cas_first": cas.strip(),
        "cas_stale_generation_row_count": cas2.strip(),
        "rollback_dropped": ada_to_drop,
        "rollback_restored_baseline": True,
        "show_tables_live_vps": False,
        "aax3_ac3": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    run_sql(client, sock, f"DROP DATABASE IF EXISTS `{DB}`;")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
