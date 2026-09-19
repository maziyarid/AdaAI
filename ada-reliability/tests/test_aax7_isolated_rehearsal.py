"""AAX-7 isolated inventory rehearsal. Never talks to production MariaDB."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LIVE_SOURCE = ROOT / "runtime" / "control-core-baseline" / "live" / "control_core.py"
SQL_DIR = ROOT / "ada-reliability" / "sql" / "mariadb"
DOC = ROOT / "docs" / "AAX7-SOURCE-VS-MIGRATION.md"
MIGRATIONS = (
    "001_ada_memory.sql",
    "002_ada_receipts_passports.sql",
    "003_ada_approvals_journal.sql",
    "004_ada_qalam_eval.sql",
    "005_ada_agiflow_projection.sql",
    "006_ada_failed_run_outbox.sql",
)
CREATE_RE = re.compile(r"CREATE TABLE IF NOT EXISTS\s+`?([A-Za-z0-9_]+)`?", re.I)
ALTER_RE = re.compile(r"ALTER\s+TABLE\s+`?([A-Za-z0-9_]+)`?", re.I)
INSERT_RE = re.compile(r"INSERT(?:\s+IGNORE)?\s+INTO\s+`?([A-Za-z0-9_]+)`?", re.I)
DROP_RE = re.compile(r"\bDROP\s+TABLE\b", re.I)
PROTECTED = frozenset(
    {
        "schema_migrations",
        "agent_events",
        "canonical_tasks",
        "jobs",
        "job_results",
        "schedules",
        "dead_letter_queue",
        "service_health",
        "operator_reachability",
        "operator_state",
        "cache_manifest",
        "harvest_provider_state",
        "tool_harvest_queue",
        "data_snapshots",
        "intelligence_findings",
        "forecasts",
        "content_gate_states",
        "green_buffers",
        "pending_external_sync",
        "audit_log",
    }
)


def _tables(sql: str) -> list[str]:
    return CREATE_RE.findall(sql)


def _live_tables() -> list[str]:
    return _tables(LIVE_SOURCE.read_text(encoding="utf-8"))


def _migration_sql() -> dict[str, str]:
    return {name: (SQL_DIR / name).read_text(encoding="utf-8") for name in MIGRATIONS}


def test_isolated_rehearsal_adds_only_ada_tables_and_rolls_back():
    live = _live_tables()
    assert set(live) == PROTECTED
    assert len(live) == len(PROTECTED)
    assert "ada_failed_runs" not in live
    assert "pd_worker_runs" not in live
    assert "pd_outbox" not in live

    before = set(live)
    added: list[str] = []
    for name, sql in _migration_sql().items():
        assert DROP_RE.search(sql) is None, name
        for altered in ALTER_RE.findall(sql):
            assert altered.startswith("ada_"), (name, altered)
            assert altered not in PROTECTED
        for inserted in INSERT_RE.findall(sql):
            assert inserted.startswith("ada_"), (name, inserted)
        created = _tables(sql)
        assert created, name
        for table in created:
            assert table.startswith("ada_"), (name, table)
            assert table not in PROTECTED
            assert table not in before
            added.append(table)
        before.update(created)

    after_apply = set(live) | set(added)
    assert set(live) <= after_apply
    assert after_apply - set(added) == set(live)
    for protected in PROTECTED:
        assert protected in after_apply

    after_rollback = after_apply - {name for name in after_apply if name.startswith("ada_")}
    assert after_rollback == set(live)
    assert not any(name.startswith("ada_") for name in after_rollback)


def test_isolated_rehearsal_does_not_claim_production_or_show_tables():
    text = DOC.read_text(encoding="utf-8")
    assert "isolated inventory rehearsal" in text.lower()
    assert "Production SQL this session: **NONE**" in text
    assert "not `SHOW TABLES`" in text or "not** `SHOW TABLES`" in text
    assert "conflict" in text.lower()
    for label in (
        "persistence",
        "failure records",
        "leases",
        "claim generation",
        "retry",
        "idempotency",
        "dead-letter",
        "quarantine",
        "external sync",
        "Agiflow handoff",
    ):
        assert label in text


def test_006_does_not_claim_live_pd_tables_exist():
    sql = (SQL_DIR / "006_ada_failed_run_outbox.sql").read_text(encoding="utf-8")
    assert "currently records" not in sql
    assert "Confirm with ada-inspect tables" in sql
    assert "CREATE TABLE IF NOT EXISTS jobs" not in sql
    assert "CREATE TABLE IF NOT EXISTS pending_external_sync" not in sql


def test_rehearsal_script_requires_disposable_instance_marker(tmp_path, monkeypatch):
    sys.path.insert(0, str(ROOT / "ada-reliability" / "scripts"))
    import isolated_mariadb_rehearsal as rehearsal

    assert rehearsal.DISPOSABLE_TOKEN == "ADA-ISOLATED-REHEARSAL-DISPOSABLE"
    assert rehearsal.variable_value("datadir\t/tmp/ada-rehearsal/data/\n") == "/tmp/ada-rehearsal/data/"
    rehearsal.require_tmp_path("datadir", "/tmp/ada-rehearsal/data/")
    with pytest.raises(SystemExit):
        rehearsal.require_tmp_path("datadir", "/var/lib/mysql/")
    with pytest.raises(SystemExit):
        rehearsal.require_tmp_path("datadir", "/tmp/../var/lib/mysql/")

    sock = Path("/tmp/ada-rehearsal.sock")
    missing = Path("/tmp/ada-rehearsal.sock.disposable")
    if missing.exists():
        missing.unlink()
    with pytest.raises(SystemExit):
        rehearsal.require_disposable_marker(sock)

    marker = tmp_path / "marker"
    # tmp_path is not under /tmp in some environments; force /tmp file
    real = Path("/tmp/ada-rehearsal-test.disposable")
    real.write_text("WRONG\n", encoding="utf-8")
    monkeypatch.setenv("ADA_REHEARSAL_MARKER", str(real))
    with pytest.raises(SystemExit):
        rehearsal.require_disposable_marker(sock)
    real.write_text(rehearsal.DISPOSABLE_TOKEN + "\n", encoding="utf-8")
    assert rehearsal.require_disposable_marker(sock) == real
    real.unlink()
    monkeypatch.delenv("ADA_REHEARSAL_MARKER", raising=False)
