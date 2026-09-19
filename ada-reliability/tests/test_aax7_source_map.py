"""AAX-7 source-vs-migration map is a STOP document, not an Apply."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "AAX7-SOURCE-VS-MIGRATION.md"
SQL006 = ROOT / "ada-reliability" / "sql" / "mariadb" / "006_ada_failed_run_outbox.sql"


def test_aax7_map_exists_and_stops_before_apply():
    text = DOC.read_text(encoding="utf-8")
    assert "STOP before Apply" in text
    assert "Production SQL this session: **NONE**" in text
    assert "not `SHOW TABLES`" in text or "not** `SHOW TABLES`" in text
    assert "006_ada_failed_run_outbox.sql" in text
    assert "ada_failed_runs" in text
    assert SQL006.is_file()
    sql = SQL006.read_text(encoding="utf-8")
    assert "ada_failed_runs" in sql
    assert "CREATE TABLE IF NOT EXISTS jobs" not in sql
    assert "CREATE TABLE IF NOT EXISTS schedules" not in sql
    # classification vocabulary present
    for label in ("already provided live", "complementary", "overlapping", "still missing"):
        assert label in text
    # do not claim live MariaDB proof
    assert "AC3 remains open" in text or "AAX-3 AC3 remains open" in text
