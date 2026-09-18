"""Schema contracts for MariaDB uniqueness — no live DB required."""
from pathlib import Path

SQL = Path(__file__).resolve().parents[1] / "sql" / "mariadb"


def test_qalam_assets_use_path_hash_not_prefix_unique():
    text = (SQL / "004_ada_qalam_eval.sql").read_text(encoding="utf-8")
    assert "path_hash CHAR(64) NOT NULL" in text
    assert "PRIMARY KEY (component, release, path_hash)" in text
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
