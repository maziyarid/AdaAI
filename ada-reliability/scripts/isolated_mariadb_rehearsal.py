#!/usr/bin/env python3
"""AAX-7 isolated MariaDB rehearsal. NEVER production.

Requires a local unix socket of a disposable mariadbd started with
--skip-networking, datadir under /tmp, and a disposable marker file
whose first line is ADA-ISOLATED-REHEARSAL-DISPOSABLE. Refuses TCP,
remote hosts, default 3306, long-lived datadirs, and missing markers.
Does not read production env files.

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
import select
import subprocess
import sys
import tempfile
import time
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
DISPOSABLE_TOKEN = "ADA-ISOLATED-REHEARSAL-DISPOSABLE"
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


def variable_value(raw: str) -> str:
    line = raw.strip().splitlines()[0] if raw.strip() else ""
    if "\t" in line:
        return line.split("\t", 1)[1].strip()
    parts = line.split()
    return parts[-1] if parts else ""


def require_tmp_path(name: str, value: str) -> str:
    if not value.startswith("/tmp/") or ".." in value:
        fail(f"refusing rehearsal: {name} is not under /tmp/: {value}")
    return value


def require_disposable_marker(sock: Path) -> Path:
    raw = os.environ.get("ADA_REHEARSAL_MARKER", str(sock) + ".disposable")
    path = Path(raw)
    if not str(path).startswith("/tmp/"):
        fail("disposable marker must be under /tmp/")
    if not path.is_file():
        fail("refusing rehearsal: missing disposable marker " + str(path))
    token = path.read_text(encoding="utf-8").splitlines()[0].strip() if path.stat().st_size else ""
    if token != DISPOSABLE_TOKEN:
        fail("refusing rehearsal: disposable marker token mismatch")
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
    cmd = [client, "--no-defaults", f"--socket={sock}", "-N", "-B", "--batch"]
    if db:
        cmd += ["-D", db]
    proc = subprocess.run(cmd, input=sql, text=True, capture_output=True)
    if proc.returncode != 0:
        fail(f"sql failed ({proc.returncode}): {proc.stderr.strip()}\nSQL:\n{sql[:500]}")
    return proc.stdout


def source_file(client: str, sock: Path, db: str, path: Path) -> None:
    cmd = [client, "--no-defaults", f"--socket={sock}", "-D", db]
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
    cmd = [client, "--no-defaults", f"--socket={sock}", "-D", db]
    proc = subprocess.run(cmd, input=sql, text=True, capture_output=True)
    blob = (proc.stderr or "") + (proc.stdout or "")
    if proc.returncode == 0:
        fail(f"expected error containing {needle!r}, SQL succeeded:\n{sql}")
    if needle.lower() not in blob.lower() and "duplicate" not in blob.lower():
        fail(f"expected duplicate/unique error, got: {blob}")
    return blob.splitlines()[-1] if blob else "error"


def control_core_behavior_probe(client: str, sock: Path, db: str, label: str) -> dict[str, object]:
    """Exercise the existing control-core job/schedule/lease/retry/DLQ contract.

    This uses only disposable rehearsal rows in the isolated schema and cleans
    them up before returning. SQL mirrors the live control_core.py transitions;
    it never imports or contacts the production service.
    """
    if label not in {"before", "after"}:
        fail("invalid behavior probe label")
    digit = "1" if label == "before" else "2"
    schedule_id = f"{digit * 8}-{digit * 4}-{digit * 4}-{digit * 4}-{digit * 12}"
    lease_job_id = f"{digit * 7}a-{digit * 4}-{digit * 4}-{digit * 4}-{digit * 12}"
    retry_job_id = f"{digit * 7}b-{digit * 4}-{digit * 4}-{digit * 4}-{digit * 12}"
    order_job_a = f"{digit * 7}c-{digit * 4}-{digit * 4}-{digit * 4}-{digit * 12}"
    order_job_b = f"{digit * 7}d-{digit * 4}-{digit * 4}-{digit * 4}-{digit * 12}"
    result1 = f"{digit * 7}e-{digit * 4}-{digit * 4}-{digit * 4}-{digit * 12}"
    result2 = f"{digit * 7}f-{digit * 4}-{digit * 4}-{digit * 4}-{digit * 12}"
    dlq_id = f"{digit * 7}9-{digit * 4}-{digit * 4}-{digit * 4}-{digit * 12}"
    schedule_stable = f"schedule:behavior:{label}"
    schedule_idem = f"schedule:{schedule_stable}:fixed"
    retry_idem = f"behavior-retry:{label}"

    run_sql(
        client,
        sock,
        f"""INSERT INTO schedules(
          id,stable_id,agent,job_type,payload_json,interval_seconds,enabled,next_run_at,max_attempts
        ) VALUES(
          '{schedule_id}','{schedule_stable}','TEST','test.echo','{{"behavior":true}}',
          300,1,NOW(6),2
        );""",
        db,
    )
    release_first = run_sql(
        client,
        sock,
        f"""INSERT IGNORE INTO jobs(
          id,stable_id,idempotency_key,agent,job_type,payload_json,status,
          priority,max_attempts,available_at
        ) VALUES(
          '{lease_job_id}','job:{schedule_idem}','{schedule_idem}',
          'TEST','test.echo','{{"behavior":true}}','queued',100,2,NOW(6)
        );
        SELECT ROW_COUNT();""",
        db,
    ).strip()
    release_duplicate = run_sql(
        client,
        sock,
        f"""INSERT IGNORE INTO jobs(
          id,stable_id,idempotency_key,agent,job_type,payload_json,status,
          priority,max_attempts,available_at
        ) VALUES(
          '{digit * 7}f-{digit * 4}-{digit * 4}-{digit * 4}-{digit * 12}',
          'job:{schedule_idem}:dup','{schedule_idem}',
          'TEST','test.echo','{{"behavior":true}}','queued',100,2,NOW(6)
        );
        SELECT ROW_COUNT();""",
        db,
    ).strip()

    # Runtime ordering + SKIP LOCKED semantics. The lower-priority-number
    # job must win normally; while it is locked by another transaction,
    # the exact live SELECT shape must skip it and return the next job.
    run_sql(
        client,
        sock,
        f"""INSERT INTO jobs(
          id,stable_id,idempotency_key,agent,job_type,payload_json,status,
          priority,attempts,max_attempts,available_at,created_at
        ) VALUES
        (
          '{order_job_a}','job:order-a:{label}','order-a:{label}',
          'TEST','test.echo','{{"behavior":true}}','queued',10,0,2,NOW(6),
          DATE_SUB(NOW(6),INTERVAL 2 SECOND)
        ),
        (
          '{order_job_b}','job:order-b:{label}','order-b:{label}',
          'TEST','test.echo','{{"behavior":true}}','queued',20,0,2,NOW(6),
          DATE_SUB(NOW(6),INTERVAL 1 SECOND)
        );""",
        db,
    )
    ordered_first = run_sql(
        client,
        sock,
        """SELECT id FROM jobs
           WHERE status='queued' AND available_at<=NOW(6)
             AND idempotency_key LIKE 'order-%'
           ORDER BY priority ASC,created_at ASC
           LIMIT 1;""",
        db,
    ).strip()
    # Keep one interactive MariaDB connection open for the entire contention
    # probe. Its LOCK_CONFIRMED marker is emitted only after FOR UPDATE
    # returns, and the transaction is committed only after the competing
    # SKIP LOCKED query completes. This removes timing from lock lifetime.
    holder = subprocess.Popen(
        [
            client,
            "--no-defaults",
            f"--socket={sock}",
            "-N",
            "-B",
            "--unbuffered",
            "-D",
            db,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    if holder.stdin is None or holder.stdout is None or holder.stderr is None:
        holder.terminate()
        fail("SKIP LOCKED holder pipes unavailable")
    expected_lock_marker = f"LOCK_CONFIRMED:{order_job_a}"
    holder.stdin.write(
        "START TRANSACTION;\n"
        f"SELECT CONCAT('LOCK_CONFIRMED:',id) "
        f"FROM jobs WHERE id='{order_job_a}' FOR UPDATE;\n"
    )
    holder.stdin.flush()
    lock_confirmed = False
    holder_output: list[str] = []
    lock_deadline = time.monotonic() + 5.0
    while time.monotonic() < lock_deadline:
        if holder.poll() is not None:
            herr = holder.stderr.read()
            fail("SKIP LOCKED holder exited before lock confirmation: " + herr.strip())
        readable, _, _ = select.select([holder.stdout], [], [], 0.1)
        if not readable:
            continue
        line = holder.stdout.readline().strip()
        if line:
            holder_output.append(line)
        if line == expected_lock_marker:
            lock_confirmed = True
            break
    if not lock_confirmed:
        holder.terminate()
        try:
            holder.wait(timeout=2)
        except subprocess.TimeoutExpired:
            holder.kill()
            holder.wait(timeout=2)
        herr = holder.stderr.read()
        fail(
            "SKIP LOCKED holder did not confirm row-lock acquisition: "
            + herr.strip()
            + " output="
            + repr(holder_output)
        )
    skip_locked_selected = run_sql(
        client,
        sock,
        """START TRANSACTION;
           SELECT id FROM jobs
            WHERE status='queued' AND available_at<=NOW(6)
              AND idempotency_key LIKE 'order-%'
            ORDER BY priority ASC,created_at ASC
            LIMIT 1 FOR UPDATE SKIP LOCKED;
           COMMIT;""",
        db,
    ).strip()
    holder.stdin.write("COMMIT;\n")
    holder.stdin.flush()
    holder.stdin.close()
    try:
        holder.wait(timeout=5)
    except subprocess.TimeoutExpired:
        holder.terminate()
        try:
            holder.wait(timeout=2)
        except subprocess.TimeoutExpired:
            holder.kill()
            holder.wait(timeout=2)
        fail("SKIP LOCKED holder did not exit after COMMIT")
    herr = holder.stderr.read()
    if holder.returncode != 0:
        fail("SKIP LOCKED holder failed: " + herr.strip())
    if ordered_first != order_job_a:
        fail(f"priority ordering mismatch: {ordered_first} != {order_job_a}")
    if skip_locked_selected != order_job_b:
        fail(f"SKIP LOCKED mismatch: {skip_locked_selected} != {order_job_b}")

    lease_claim = run_sql(
        client,
        sock,
        f"""UPDATE jobs SET
          status='running',locked_by='behavior-worker',
          lease_until=DATE_ADD(NOW(6),INTERVAL 120 SECOND),attempts=attempts+1
        WHERE id='{lease_job_id}' AND status='queued' AND available_at<=NOW(6);
        SELECT ROW_COUNT(),status,attempts,(locked_by IS NOT NULL),(lease_until IS NOT NULL)
        FROM jobs WHERE id='{lease_job_id}';""",
        db,
    ).strip()
    run_sql(
        client,
        sock,
        f"UPDATE jobs SET lease_until=DATE_SUB(NOW(6),INTERVAL 1 SECOND) WHERE id='{lease_job_id}';",
        db,
    )
    lease_reap = run_sql(
        client,
        sock,
        f"""UPDATE jobs SET status='queued',locked_by=NULL,lease_until=NULL
        WHERE id='{lease_job_id}' AND status='running' AND lease_until<NOW(6);
        SELECT ROW_COUNT(),status,(locked_by IS NULL),(lease_until IS NULL)
        FROM jobs WHERE id='{lease_job_id}';""",
        db,
    ).strip()

    run_sql(
        client,
        sock,
        f"""INSERT INTO jobs(
          id,stable_id,idempotency_key,agent,job_type,payload_json,status,
          priority,attempts,max_attempts,available_at
        ) VALUES(
          '{retry_job_id}','job:{retry_idem}','{retry_idem}',
          'TEST','test.fail','{{"message":"behavior"}}','queued',100,0,2,NOW(6)
        );""",
        db,
    )
    first_claim = run_sql(
        client,
        sock,
        f"""UPDATE jobs SET status='running',locked_by='behavior-worker',
          lease_until=DATE_ADD(NOW(6),INTERVAL 120 SECOND),attempts=attempts+1
        WHERE id='{retry_job_id}' AND status='queued' AND available_at<=NOW(6);
        SELECT ROW_COUNT(),attempts FROM jobs WHERE id='{retry_job_id}';""",
        db,
    ).strip()
    first_failure = run_sql(
        client,
        sock,
        f"""INSERT INTO job_results(
          id,job_id,attempt,status,result_json,error_text,started_at,finished_at
        ) VALUES(
          '{result1}','{retry_job_id}',1,'failed',NULL,'behavior failure',NOW(6),NOW(6)
        );
        SET @finish_now=NOW(6);
        UPDATE jobs SET status='queued',
          available_at=DATE_ADD(@finish_now,INTERVAL 2 SECOND),
          locked_by=NULL,lease_until=NULL,last_error='behavior failure',finished_at=NULL
        WHERE id='{retry_job_id}';
        SELECT status,attempts,
          TIMESTAMPDIFF(SECOND,@finish_now,available_at),
          (SELECT COUNT(*) FROM dead_letter_queue WHERE job_id='{retry_job_id}')
        FROM jobs WHERE id='{retry_job_id}';""",
        db,
    ).strip()
    retry_blocked_during_backoff = run_sql(
        client,
        sock,
        f"""SELECT COUNT(*) FROM jobs
        WHERE id='{retry_job_id}' AND status='queued' AND available_at<=NOW(6);""",
        db,
    ).strip()
    if retry_blocked_during_backoff != "0":
        fail("retry became claimable before exponential backoff elapsed")
    run_sql(
        client,
        sock,
        f"UPDATE jobs SET available_at=DATE_SUB(NOW(6),INTERVAL 1 SECOND) WHERE id='{retry_job_id}';",
        db,
    )

    second_claim = run_sql(
        client,
        sock,
        f"""UPDATE jobs SET status='running',locked_by='behavior-worker',
          lease_until=DATE_ADD(NOW(6),INTERVAL 120 SECOND),attempts=attempts+1
        WHERE id='{retry_job_id}' AND status='queued' AND available_at<=NOW(6);
        SELECT ROW_COUNT(),attempts FROM jobs WHERE id='{retry_job_id}';""",
        db,
    ).strip()
    terminal_failure = run_sql(
        client,
        sock,
        f"""INSERT INTO job_results(
          id,job_id,attempt,status,result_json,error_text,started_at,finished_at
        ) VALUES(
          '{result2}','{retry_job_id}',2,'failed',NULL,'behavior terminal',NOW(6),NOW(6)
        );
        UPDATE jobs SET status='dead',available_at=NOW(6),locked_by=NULL,
          lease_until=NULL,last_error='behavior terminal',finished_at=NOW(6)
        WHERE id='{retry_job_id}';
        INSERT IGNORE INTO dead_letter_queue(
          id,job_id,stable_id,agent,job_type,payload_json,attempts,error_text
        ) VALUES(
          '{dlq_id}','{retry_job_id}','dlq:job:{retry_idem}',
          'TEST','test.fail','{{"message":"behavior"}}',2,'behavior terminal'
        );
        SELECT status,attempts,(SELECT COUNT(*) FROM dead_letter_queue WHERE job_id='{retry_job_id}')
        FROM jobs WHERE id='{retry_job_id}';""",
        db,
    ).strip()
    retry_from_dlq = run_sql(
        client,
        sock,
        f"""UPDATE jobs SET status='queued',available_at=NOW(6),locked_by=NULL,
          lease_until=NULL,finished_at=NULL,last_error=NULL
        WHERE id='{retry_job_id}' AND status='dead';
        UPDATE dead_letter_queue SET resolved_at=NOW(6),resolution_note='retried'
        WHERE job_id='{retry_job_id}' AND resolved_at IS NULL;
        SELECT status,
          (SELECT COUNT(*) FROM dead_letter_queue WHERE job_id='{retry_job_id}' AND resolved_at IS NULL),
          (SELECT COUNT(*) FROM dead_letter_queue WHERE job_id='{retry_job_id}' AND resolved_at IS NOT NULL)
        FROM jobs WHERE id='{retry_job_id}';""",
        db,
    ).strip()

    outcome = {
        "schedule_release_first_row_count": release_first,
        "schedule_release_duplicate_row_count": release_duplicate,
        "priority_order_selected_expected": ordered_first == order_job_a,
        "skip_locked_selected_expected_next": skip_locked_selected == order_job_b,
        "lease_claim": lease_claim,
        "expired_lease_reap": lease_reap,
        "retry_first_claim": first_claim,
        "retry_after_first_failure": first_failure,
        "retry_blocked_during_backoff": retry_blocked_during_backoff,
        "retry_second_claim": second_claim,
        "dead_letter_after_terminal_failure": terminal_failure,
        "retry_from_dlq": retry_from_dlq,
    }

    run_sql(
        client,
        sock,
        f"""DELETE FROM job_results WHERE job_id IN ('{lease_job_id}','{retry_job_id}');
        DELETE FROM dead_letter_queue WHERE job_id IN ('{lease_job_id}','{retry_job_id}');
        DELETE FROM jobs WHERE id IN ('{lease_job_id}','{retry_job_id}','{order_job_a}','{order_job_b}');
        DELETE FROM schedules WHERE id='{schedule_id}';""",
        db,
    )
    return outcome

def main() -> int:
    sock = require_socket()
    marker = require_disposable_marker(sock)
    client = client_bin()
    skip_net = run_sql(client, sock, "SHOW VARIABLES LIKE 'skip_networking';")
    if "ON" not in skip_net.upper() and "1" not in skip_net.split():
        fail("refusing rehearsal: skip_networking is not ON")
    datadir = variable_value(run_sql(client, sock, "SHOW VARIABLES LIKE 'datadir';"))
    require_tmp_path("datadir", datadir)
    pid_file = variable_value(run_sql(client, sock, "SHOW VARIABLES LIKE 'pid_file';"))
    if pid_file:
        require_tmp_path("pid_file", pid_file)
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

    behavior_before = control_core_behavior_probe(client, sock, DB, "before")
    if run_sql(client, sock, "SELECT COUNT(*) FROM jobs;", DB).strip() != job_count:
        fail("behavior probe did not restore jobs baseline")
    if run_sql(client, sock, "SELECT COUNT(*) FROM schedules;", DB).strip() != sched_count:
        fail("behavior probe did not restore schedules baseline")

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

    behavior_after = control_core_behavior_probe(client, sock, DB, "after")
    if behavior_after != behavior_before:
        fail(f"control-core AC3 surface changed after migrations: {behavior_before} != {behavior_after}")
    if run_sql(client, sock, "SELECT COUNT(*) FROM jobs;", DB).strip() != job_count:
        fail("post-migration behavior probe did not restore jobs baseline")
    if run_sql(client, sock, "SELECT COUNT(*) FROM schedules;", DB).strip() != sched_count:
        fail("post-migration behavior probe did not restore schedules baseline")

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
        "datadir_scope": "/tmp/",
        "disposable_marker_verified": True,
        "mariadb_version": version,
        "database": DB,
        "socket_scope": "/tmp/",
        "live_source": str(LIVE_SOURCE.relative_to(REPO)),
        "applied": applied,
        "reapplied_idempotent": True,
        "protected_unchanged": True,
        "control_core_ac3_surface_equivalent": True,
        "control_core_behavior_before": behavior_before,
        "control_core_behavior_after": behavior_after,
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
        "live_vps_schema_evidence": "docs/AAX7-LIVE-RECOVERY-STORES.json",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    run_sql(client, sock, f"DROP DATABASE IF EXISTS `{DB}`;")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
