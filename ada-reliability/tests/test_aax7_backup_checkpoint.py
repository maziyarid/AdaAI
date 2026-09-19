"""AAX-7 AC1 backup/checkpoint contract. Never talks to production MariaDB."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "AAX7-BACKUP-CHECKPOINT.md"
SCRIPT = ROOT / "ada-reliability" / "scripts" / "backup_checkpoint_plan.py"
LIVE_EVIDENCE = ROOT / "docs" / "AAX7-LIVE-SCHEMA-CHECKPOINT-RESTORE.json"
sys.path.insert(0, str(SCRIPT.parent))
from backup_checkpoint_plan import (  # noqa: E402
    assert_dry_run_safe,
    build_plan,
    refuse_execute_target,
)


def test_backup_doc_is_stop_not_apply():
    text = DOC.read_text(encoding="utf-8")
    assert "STOP, not Apply" in text
    assert "AC1 schema checkpoint + restore drill PASS" in text
    assert "pg_dump" in text  # named so we can forbid it
    assert "not** the production path" in text or "not the production path" in text
    assert "SCHEMA_CHECKPOINT" not in text or "Schema-only" in text
    for needle in (
        "encrypted",
        "schema-only",
        "checksum",
        "restore",
        "retention",
        "rollback trigger",
        "ADA_BACKUP_AGE_RECIPIENT",
        "--password=",
        "/etc/maziyar-control-core.env",
    ):
        assert needle.lower() in text.lower()
    assert "PRODUCTION_SQL_WRITE: **NONE**" in text
    assert "INSERT INTO" in text  # schema dump must not contain it


def test_plan_is_secret_free_and_not_executed():
    plan = build_plan()
    assert_dry_run_safe(plan)
    assert plan["production"] is False
    assert plan["executed"] is False
    assert plan["production_sql"] is False
    assert plan["human_approval_required_for_production"] is True
    assert plan["not_postgres"] is True
    blob = json.dumps(plan)
    commands = "\n".join(
        cmd for step in plan["steps"] for cmd in step.get("commands") or []
    )
    assert "--password=" not in commands
    assert "CONTROL_DB_PASSWORD" not in blob
    assert "--password=" in plan["forbidden"]
    assert "pg_dump" in plan["forbidden"]

    ids = [s["id"] for s in plan["steps"]]
    assert ids == [
        "preconditions",
        "schema_checkpoint",
        "encrypted_full",
        "checksum_verify",
        "offhost_copy",
        "restore_drill",
    ]
    assert "jobs" in plan["protected_must_appear_in_schema_dump"]
    assert any("drop ada_*" in t for t in plan["rollback_triggers"])
    recovery = plan["runtime_recovery_store"]
    assert recovery["path"] == "/srv/maziyar-wp-mcp/state/factory.sqlite3"
    assert recovery["engine"] == "SQLite"
    assert recovery["tables"] == ["pd_worker_runs", "pd_outbox"]
    assert "HOLD" in recovery["migration_006"]
    assert any("SQLite" in t and "006 HOLD" in t for t in plan["rollback_triggers"])


def test_script_dry_run_prints_json():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    plan = json.loads(proc.stdout)
    assert plan["aax"] == "AAX-7"
    assert plan["executed"] is False


def test_execute_refuses_production_and_missing_socket(monkeypatch):
    monkeypatch.delenv("ADA_BACKUP_EXECUTE", raising=False)
    monkeypatch.delenv("ADA_REHEARSAL_SOCKET", raising=False)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--execute"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode != 0
    assert "isolated-rehearsal" in proc.stderr

    monkeypatch.setenv("ADA_BACKUP_EXECUTE", "isolated-rehearsal")
    monkeypatch.setenv("ADA_REHEARSAL_SOCKET", "mysql://server.maziyarid.com:3306")
    with pytest.raises(SystemExit):
        refuse_execute_target()


def test_live_schema_checkpoint_restore_evidence():
    evidence = json.loads(LIVE_EVIDENCE.read_text(encoding="utf-8"))
    assert evidence["checkpoint_kind"] == "table-schema-only"
    assert evidence["contains_rows"] is False
    assert evidence["insert_statements"] == 0
    assert evidence["table_count"] == 20
    assert evidence["create_table_count"] == 20
    assert evidence["restore_table_inventory_match"] is True
    assert evidence["critical_ddl_hashes_match"] is True
    assert evidence["production_sql_write"] is False
    assert evidence["production_mutation"] is False
    assert evidence["full_row_backup_created"] is False
    assert evidence["encrypted_full_backup_created"] is False
    assert evidence["pre_apply_full_encrypted_backup_still_required"] is True
    assert evidence["schema_sha256"] == "bbe20ae5e6482a988562de16e5faa5634c34a75207e4cd4d846ff240f9e3a488"
    for table in (
        "jobs",
        "schedules",
        "job_results",
        "dead_letter_queue",
        "pending_external_sync",
        "audit_log",
    ):
        assert table in evidence["tables"]
        assert table in evidence["critical_ddl_sha256"]
