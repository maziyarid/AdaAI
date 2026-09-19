"""Schema contracts for MariaDB uniqueness — no live DB required."""
from pathlib import Path

SQL = Path(__file__).resolve().parents[1] / "sql" / "mariadb"


def test_qalam_assets_use_path_hash_not_prefix_unique():
    text = (SQL / "004_ada_qalam_eval.sql").read_text(encoding="utf-8")
    assert "path_hash CHAR(64) NOT NULL" in text
    assert "PRIMARY KEY (component, `release`, path_hash)" in text
    assert "PRIMARY KEY (component, release, path(191))" not in text


def test_policy_releases_enforce_one_active_per_component():
    text = (SQL / "002_ada_receipts_passports.sql").read_text(encoding="utf-8")
    assert "uq_ada_policy_one_active" in text
    assert "IF(status = 'ACTIVE', component, NULL)" in text


def test_memory_seed_insert_is_documented_ignore():
    text = (SQL / "001_ada_memory.sql").read_text(encoding="utf-8")
    assert "INSERT IGNORE INTO ada_scope_versions" in text


def test_agiflow_outbox_is_idempotent_and_additive():
    text = (SQL / "005_ada_agiflow_projection.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS ada_agiflow_task_map" in text
    assert "CREATE TABLE IF NOT EXISTS ada_agiflow_outbox" in text
    assert "UNIQUE KEY uq_ada_agiflow_outbox_idem (idempotency_key)" in text
    assert "UNIQUE KEY uq_ada_agiflow_task (agiflow_task_id)" in text
    assert "DROP TABLE" not in text
    # Must not claim ownership of control-core jobs/schedules.
    assert "CREATE TABLE IF NOT EXISTS jobs" not in text
    assert "CREATE TABLE IF NOT EXISTS schedules" not in text


def test_agiflow_evidence_and_close_grants_are_hmac_issued():
    """Greptile P1: Review/Done proof lives in HMAC tables, not caller flags."""
    text = (SQL / "005_ada_agiflow_projection.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS ada_agiflow_evidence" in text
    assert "CREATE TABLE IF NOT EXISTS ada_agiflow_close_grants" in text
    assert "signature CHAR(64) NOT NULL" in text
    assert "consumed TINYINT(1) NOT NULL DEFAULT 0" in text
    assert "verifier_identity VARCHAR(128) NOT NULL" in text
    assert "closer_identity VARCHAR(128) NOT NULL" in text
    assert "evidence_id CHAR(36) NOT NULL" in text
    # Outbox must not become a second forgeable evidence store.
    assert "Payload stores evidence_id / close_grant_id only" in text


def test_failed_run_outbox_is_distinct_from_agiflow_projection():
    text = (SQL / "006_ada_failed_run_outbox.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS ada_failed_runs" in text
    assert "CREATE TABLE IF NOT EXISTS ada_failed_run_events" in text
    assert "UNIQUE KEY uq_ada_failed_runs_idem (idempotency_key)" in text
    assert "DISTINCT from ada_agiflow_outbox" in text
    assert "claim_generation INT NOT NULL DEFAULT 0" in text
    assert "AND lifecycle='inflight'" in text
    assert "AND claim_generation <=> ?" in text
    assert "apply_if_claim" in text
    assert "DROP TABLE" not in text
    assert "CREATE TABLE IF NOT EXISTS jobs" not in text
    assert "CREATE TABLE IF NOT EXISTS schedules" not in text
    assert "CREATE TABLE IF NOT EXISTS ada_agiflow_outbox" not in text
    agiflow = (SQL / "005_ada_agiflow_projection.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS ada_failed_runs" not in agiflow


def test_runbook_stops_before_006_until_legacy_outbox_reconciled():
    """Greptile P1: reconciliation is a pre-apply stop, not a post-apply footnote."""
    runbook = (Path(__file__).resolve().parents[2] / "docs" / "MIGRATION-RUNBOOK.md").read_text(
        encoding="utf-8"
    )
    stop_at = runbook.find("Live durability reconciliation complete")
    apply_at = runbook.find("## Apply")
    assert stop_at != -1
    assert apply_at != -1
    assert stop_at < apply_at
    pre = runbook[:apply_at]
    assert "006_ada_failed_run_outbox.sql" in pre
    assert "ada_failed_runs" in pre
    assert "pd_worker_runs" in pre
    assert "pd_outbox" in pre
    assert "pending_external_sync" in pre
    assert "/srv/maziyar-wp-mcp/state/factory.sqlite3" in pre
    assert "006 HOLD" in pre
    assert "SQLite" in pre
    # Do not name the migration file 006_ada_failed_runs.
    assert "006_ada_failed_runs" not in runbook
