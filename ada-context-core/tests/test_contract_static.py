from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=(ROOT/'sql/001_schema.sql').read_text()

def test_scoped_versions_exist():
    assert 'scope_versions' in SCHEMA and 'receipt_dependencies' in SCHEMA

def test_recovery_tables_exist():
    assert 'backup_runs' in SCHEMA and 'audit_events' in SCHEMA

def test_approval_is_payload_bound():
    assert 'payload_hash' in SCHEMA and 'snapshot_hash' in SCHEMA and 'dependency_hash' in SCHEMA

def test_external_input_quarantine_exists():
    assert 'UNTRUSTED_EXTERNAL' in SCHEMA and 'QUARANTINED' in SCHEMA
