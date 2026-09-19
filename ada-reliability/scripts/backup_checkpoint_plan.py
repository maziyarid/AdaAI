#!/usr/bin/env python3
"""AAX-7 AC1 backup/checkpoint command plan. NEVER production by default.

Prints a secret-free JSON plan. Refuses TCP/3306, production hostnames,
env files, and password flags. Execute is isolated-rehearsal only.

  python3 backup_checkpoint_plan.py
  ADA_BACKUP_EXECUTE=isolated-rehearsal ADA_REHEARSAL_SOCKET=/tmp/ada-rehearsal.sock \\
    python3 backup_checkpoint_plan.py --execute
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "AAX7-BACKUP-CHECKPOINT.md"
FORBIDDEN_HOSTS = ("server.maziyarid.com", "127.0.0.1", "localhost", "0.0.0.0")
SECRET_RE = re.compile(
    r"(PASSWORD|PASSWD|SECRET|API_KEY|TOKEN|PRIVATE.?KEY)\s*=",
    re.I,
)
PASSWORD_FLAG_RE = re.compile(r"--password=|--pwd=", re.I)


def fail(msg: str, code: int = 2) -> None:
    print("backup-checkpoint: " + msg, file=sys.stderr)
    raise SystemExit(code)


def build_plan() -> dict:
    dest = "/var/backups/ada/control-core"
    ts = "$TS"
    db = "$CONTROL_DB_NAME"
    defaults = "/etc/ada/mysql.cnf"
    recipient = "$ADA_BACKUP_AGE_RECIPIENT"
    schema = f"{dest}/schema-{ts}.sql"
    full = f"{dest}/full-{ts}.sql.gz.age"
    drill_db = f"ada_restore_drill_{ts}"
    steps = [
        {
            "id": "preconditions",
            "title": "Stop unless ada-inspect or written waiver, disk, age, mysqldump, off-host dest",
            "execute": False,
        },
        {
            "id": "schema_checkpoint",
            "title": "Schema-only mysqldump (no INSERT, no row payloads)",
            "backup_kind": "SCHEMA_CHECKPOINT",
            "commands": [
                f"mysqldump --defaults-extra-file={defaults} --single-transaction "
                f"--no-data --skip-comments --skip-dump-date --routines --triggers "
                f"--events --databases {db} > {schema}",
                f"sha256sum {schema} | tee {schema}.sha256",
            ],
        },
        {
            "id": "encrypted_full",
            "title": "Encrypted logical dump via gzip|age (public recipient only)",
            "backup_kind": "ENCRYPTED_FULL",
            "commands": [
                f"mysqldump --defaults-extra-file={defaults} --single-transaction "
                f"--routines --triggers --events --hex-blob --databases {db} "
                f"| gzip -9 | age -r {recipient} -o {full}",
                f"sha256sum {full} | tee {full}.sha256",
                f"chmod 600 {full} {schema}.sha256 {full}.sha256",
            ],
        },
        {
            "id": "checksum_verify",
            "title": "Verify sha256; age -d off-host; gzip -t; schema has no INSERT INTO",
            "backup_kind": "CHECKSUM_VERIFY",
        },
        {
            "id": "offhost_copy",
            "title": "Copy schema + ciphertext + checksums only; re-hash after copy",
            "location": "operator-controlled off-host (not in git)",
        },
        {
            "id": "restore_drill",
            "title": "Restore ciphertext into throwaway schema; COUNT(*) only; DROP",
            "backup_kind": "RESTORE_DRILL",
            "commands": [
                f"mysql --defaults-extra-file={defaults} -e 'CREATE DATABASE {drill_db}'",
                "age -d -i $ADA_BACKUP_AGE_IDENTITY "
                f"{full} | gzip -dc | sed 's/`{db}`/`{drill_db}`/g' "
                f"| mysql --defaults-extra-file={defaults} {drill_db}",
                f"mysql --defaults-extra-file={defaults} {drill_db} "
                "-N -e 'SELECT COUNT(*) FROM jobs; SELECT COUNT(*) FROM schedules; "
                "SELECT COUNT(*) FROM pending_external_sync; SHOW TABLES LIKE \"ada_%\"; "
                "SHOW TABLES LIKE \"pd_%\";'",
                f"mysql --defaults-extra-file={defaults} -e 'DROP DATABASE {drill_db}'",
            ],
        },
    ]
    rollback_triggers = [
        "apply_never_started → keep backups, do nothing",
        "only ada_* created and protected hashes unchanged → drop ada_* only",
        "ALTER/DROP of live names or job/schedule drift → stop Apply; restore ciphertext with human approval",
        "restore drill checksum mismatch → do not Apply",
        "live pd_worker_runs/pd_outbox discovered → stop; remap 006",
        "control-core unhealthy after a future Apply → restore last checksum-passing dump",
    ]
    plan = {
        "aax": "AAX-7",
        "ac": "AC1",
        "production": False,
        "executed": False,
        "production_sql": False,
        "production_mutation": False,
        "engine": "MariaDB",
        "not_postgres": True,
        "defaults_extra_file_example": defaults,
        "destination": dest,
        "retention": {
            "encrypted_daily": 14,
            "encrypted_weekly": 4,
            "schema_days": 30,
            "mode": "0700",
            "owner": "mazcontrol:mazcontrol",
        },
        "protected_must_appear_in_schema_dump": [
            "jobs",
            "schedules",
            "job_results",
            "dead_letter_queue",
            "pending_external_sync",
        ],
        "forbidden": [
            "pg_dump",
            "--password=",
            "/etc/maziyar-control-core.env",
            "DROP TABLE jobs",
            "DROP TABLE schedules",
            "APPLY 001-006",
            "TCP 3306 execute",
        ],
        "steps": steps,
        "rollback_triggers": rollback_triggers,
        "doc": "docs/AAX7-BACKUP-CHECKPOINT.md",
        "human_approval_required_for_production": True,
    }
    refuse_secrets(plan)
    return plan


def refuse_secrets(plan: dict) -> None:
    commands: list[str] = []
    for step in plan.get("steps") or []:
        commands.extend(step.get("commands") or [])
    blob = "\n".join(commands) + "\n" + str(plan.get("defaults_extra_file_example") or "")
    if SECRET_RE.search(blob) or PASSWORD_FLAG_RE.search(blob):
        fail("plan must not contain secret assignment or --password=")
    if "BEGIN AGE" in blob or "BEGIN OPENSSH" in blob:
        fail("plan must not contain private keys")


def assert_dry_run_safe(plan: dict) -> None:
    if plan.get("production") or plan.get("executed") or plan.get("production_sql"):
        fail("plan claimed production execution")
    commands: list[str] = []
    for step in plan.get("steps") or []:
        commands.extend(step.get("commands") or [])
    blob = "\n".join(commands)
    if "mysql://" in blob or "mariadb://" in blob:
        fail("plan contains a DSN")
    if PASSWORD_FLAG_RE.search(blob):
        fail("password flag in plan")


def refuse_execute_target() -> Path:
    flag = os.environ.get("ADA_BACKUP_EXECUTE", "")
    if flag != "isolated-rehearsal":
        fail("execute refused: set ADA_BACKUP_EXECUTE=isolated-rehearsal (never production)")
    raw = os.environ.get("ADA_REHEARSAL_SOCKET", "")
    if not raw:
        fail("ADA_REHEARSAL_SOCKET is required for execute")
    if any(h in raw for h in FORBIDDEN_HOSTS) or "3306" in raw or "://" in raw:
        fail("refusing production/TCP socket: " + raw)
    path = Path(raw)
    if not str(path).startswith("/tmp/"):
        fail("socket must be under /tmp/: " + raw)
    if not path.is_socket():
        fail("not a unix socket (start skip-networking mysqld first): " + raw)
    return path


def main(argv: list[str]) -> int:
    plan = build_plan()
    assert_dry_run_safe(plan)
    if not DOC.is_file():
        fail("missing " + str(DOC))
    if "--execute" in argv:
        refuse_execute_target()
        fail("isolated execute not implemented in this cycle; dump/age need a local mariadb client")
    json.dump(plan, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
