"""AAX-3: live /opt/maziyar-control-core snapshot contracts.

Parse the imported source. Do not import/run it (needs pymysql + secrets).
Do not call the VPS. Live SHOW TABLES remains a separate AC3 stop.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "runtime" / "control-core-baseline" / "live"
SOURCE = LIVE / "control_core.py"
UNIT = LIVE / "maziyar-control-core.service"
MANIFEST = LIVE / "MANIFEST.json"

EXPECTED_TABLES = [
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
]

SEEDED_SCHEDULES = {
    ("schedule:blackout-sentinel", "BLACKOUT_SENTINEL", "blackout_sentinel.run", 300),
    ("schedule:project-controller", "PROJECT_CONTROLLER", "project_controller.run", 600),
    ("schedule:clickup-state-steward", "CLICKUP_STATE_STEWARD", "clickup_state_steward.run", 600),
    ("schedule:seo-scout", "SEO_SCOUT", "seo_scout.run", 3600),
    ("schedule:temp-tool-harvester", "TEMP_TOOL_HARVESTER", "temp_tool_harvester.run", 900),
    ("schedule:oracle-daily", "ORACLE_FORECASTER", "oracle_forecaster.run", 86400),
}


def _src() -> str:
    return SOURCE.read_text(encoding="utf-8")


def test_snapshot_bytes_and_captured_hash_match_manifest():
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    raw = SOURCE.read_bytes()
    assert len(raw) == 65370 == man["bytes"]
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == man["sha256_captured_bytes"]
    assert digest == "aec6639acf761dfb01a72feb670b4d841c25fb1e8000abdea41bca0dcf4a94f3"
    assert _src().count("\n") == man["lines"]
    assert man["host_sha256sum"] is None
    assert man["live_show_tables"] is None
    assert man["ada_star_in_source"] is False


def test_source_schema_has_twenty_control_core_tables_and_no_ada_star():
    src = _src()
    tables = re.findall(r"CREATE TABLE IF NOT EXISTS ([a-z_]+)", src)
    assert tables == EXPECTED_TABLES
    assert "ada_" not in src
    assert "pd_worker_runs" not in src
    assert "pd_outbox" not in src
    assert "CREATE TABLE IF NOT EXISTS ada_" not in src


def test_jobs_are_idempotent_leased_and_skip_locked():
    src = _src()
    assert "UNIQUE KEY uq_jobs_idempotency (idempotency_key)" in src
    assert "KEY ix_jobs_claim (status, available_at, priority, created_at)" in src
    assert "KEY ix_jobs_lease (lease_until)" in src
    assert "INSERT IGNORE INTO jobs" in src
    assert "FOR UPDATE SKIP LOCKED" in src
    claim = src[src.find("def claim_job") : src.find("def fetch_fixed")]
    assert "status='queued' AND available_at<=" in claim
    assert "lease_until<%s" in claim
    assert "status='running'" in claim
    finish = src[src.find("def finish_job") : src.find("def worker_loop")]
    assert "dead_letter_queue" in finish
    assert 'status = "succeeded" if ok else ("dead" if job["attempts"] >= job["max_attempts"] else "queued")' in finish


def test_pending_external_sync_is_leased_idempotent_outbox():
    src = _src()
    assert "UNIQUE KEY uq_sync_idempotency (idempotency_key)" in src
    assert "KEY ix_sync_lease (lease_until)" in src
    claim = src[src.find("def claim_external_sync") : src.find("def ack_external_sync")]
    assert "FOR UPDATE SKIP LOCKED" in claim
    assert "status='in_progress'" in claim
    assert "lease expired; safely requeued" in claim


def test_seeded_schedules_and_health_targets_are_exact():
    src = _src()
    found = set(
        re.findall(
            r'\("(schedule:[^"]+)", "([A-Z_]+)", "([a-z_.]+)", (\d+)\)',
            src,
        )
    )
    found_typed = {(a, b, c, int(d)) for a, b, c, d in found}
    assert found_typed == SEEDED_SCHEDULES
    assert '("control-core", "http://127.0.0.1:8770/health", (401,))' in src
    assert '("mistral-worker", "http://127.0.0.1:9102/healthz", (200,))' in src
    assert 'ThreadingHTTPServer((os.getenv("CONTROL_BIND","127.0.0.1"),int(os.getenv("CONTROL_PORT","8770"))),API)' in src


def test_health_json_is_behind_bearer_compare_digest():
    src = _src()
    api = src[src.find("class API") : src.find("def serve")]
    assert 'expected = os.environ["CONTROL_API_TOKEN"]' in api
    assert "hmac.compare_digest(expected, supplied)" in api
    auth_at = api.find("def auth")
    health_at = api.find('p=="/health"')
    deny_at = api.find('if not self.auth(): return self.sendj(401')
    assert 0 <= deny_at < health_at
    assert auth_at < deny_at
    assert "backend" in api[health_at : health_at + 200]


def test_credentials_are_env_names_not_literals():
    src = _src()
    assert 'password=os.environ["CONTROL_DB_PASSWORD"]' in src
    assert 'os.environ["CONTROL_DB_USER"]' in src
    assert 'os.environ["CONTROL_DB_NAME"]' in src
    assert 'os.environ["MISTRAL_API_KEY"]' in src
    assert 'os.environ["CONTROL_API_TOKEN"]' in src
    assert 'os.getenv("CONTROL_DB_HOST", "127.0.0.1")' in src
    assert re.search(r'CONTROL_DB_PASSWORD\s*=\s*["\'][^"\']+["\']', src) is None
    assert re.search(r'CONTROL_API_TOKEN\s*=\s*["\'][^"\']+["\']', src) is None
    assert "BEGIN OPENSSH" not in src
    assert "sk-" not in src


def test_systemd_unit_is_mazcontrol_loopback_hardened():
    unit = UNIT.read_text(encoding="utf-8")
    assert "User=mazcontrol" in unit
    assert "Group=mazcontrol" in unit
    assert "Requires=mariadb.service" in unit
    assert "EnvironmentFile=/etc/maziyar-control-core.env" in unit
    assert "control_core.py serve" in unit
    assert "ProtectSystem=strict" in unit
    assert "ReadWritePaths=/opt/maziyar-control-core/state" in unit
    assert "ProtectHome=true" in unit
