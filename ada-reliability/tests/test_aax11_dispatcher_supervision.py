from __future__ import annotations

import importlib.util
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPS = ROOT / "ops" / "portfolio-dispatcher"
SCRIPT = OPS / "portfolio_dispatcher_watchdog.py"
spec = importlib.util.spec_from_file_location("aax11_watchdog", SCRIPT)
watchdog = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(watchdog)


def make_db(path: Path, heartbeat_at: str | None) -> Path:
    c = sqlite3.connect(path)
    c.executescript(
        """
        CREATE TABLE pd_heartbeat (
          component TEXT PRIMARY KEY, heartbeat_at TEXT NOT NULL, state_json TEXT
        );
        CREATE TABLE pd_leases (
          resource TEXT PRIMARY KEY, lease_owner TEXT NOT NULL,
          lease_started_at TEXT NOT NULL, lease_expires_at REAL NOT NULL,
          heartbeat_at TEXT, attempt INTEGER NOT NULL DEFAULT 1,
          state TEXT NOT NULL, idempotency_key TEXT
        );
        CREATE TABLE pd_circuits (
          resource TEXT PRIMARY KEY, state TEXT NOT NULL,
          failure_count INTEGER NOT NULL DEFAULT 0, opened_at TEXT,
          reset_after_epoch REAL
        );
        """
    )
    if heartbeat_at is not None:
        c.execute(
            "INSERT INTO pd_heartbeat(component,heartbeat_at,state_json) VALUES(?,?,?)",
            ("portfolio-dispatcher-01", heartbeat_at, '{"dispatch_enabled":false}'),
        )
    c.commit()
    c.close()
    return path


def test_fresh_heartbeat_is_healthy_and_read_only(tmp_path):
    now = 2_000_000_000.0
    hb = datetime.fromtimestamp(now - 60, tz=timezone.utc).isoformat()
    db = make_db(tmp_path / "factory.sqlite3", hb)
    before = db.read_bytes()
    result = watchdog.inspect(db, now_epoch=now, max_heartbeat_age=180)
    assert result["status"] == "healthy"
    assert result["restart_recommended"] is False
    assert result["dispatcher_state"]["dispatch_enabled"] is False
    assert db.read_bytes() == before


def test_stale_heartbeat_requests_recovery(tmp_path):
    now = 2_000_000_000.0
    hb = datetime.fromtimestamp(now - 181, tz=timezone.utc).isoformat()
    db = make_db(tmp_path / "factory.sqlite3", hb)
    result = watchdog.inspect(db, now_epoch=now, max_heartbeat_age=180)
    assert result["status"] == "unhealthy"
    assert result["reason"] == "heartbeat_stale"
    assert result["restart_recommended"] is True


def test_degraded_lease_or_circuit_does_not_restart_dispatcher(tmp_path):
    now = 2_000_000_000.0
    hb = datetime.fromtimestamp(now - 10, tz=timezone.utc).isoformat()
    db = make_db(tmp_path / "factory.sqlite3", hb)
    c = sqlite3.connect(db)
    c.execute(
        "INSERT INTO pd_leases(resource,lease_owner,lease_started_at,lease_expires_at,"
        "heartbeat_at,attempt,state,idempotency_key) VALUES(?,?,?,?,?,?,?,?)",
        ("shadow/x", "worker", hb, now - 1, hb, 2, "active", "idem"),
    )
    c.execute(
        "INSERT INTO pd_circuits(resource,state,failure_count,opened_at,reset_after_epoch) "
        "VALUES(?,?,?,?,?)",
        ("shadow/x", "open", 3, hb, now + 300),
    )
    c.commit()
    c.close()
    result = watchdog.inspect(db, now_epoch=now, max_heartbeat_age=180)
    assert result["status"] == "degraded"
    assert result["restart_recommended"] is False
    assert len(result["stale_leases"]) == 1
    assert len(result["open_circuits"]) == 1


def test_missing_schema_fails_closed_without_restart_loop(tmp_path):
    db = tmp_path / "empty.sqlite3"
    sqlite3.connect(db).close()
    result = watchdog.inspect(db)
    assert result["status"] == "blocked"
    assert result["restart_recommended"] is False
    assert result["reason"] == "dispatcher_schema_missing"


def test_staged_service_forces_observation_only_and_rate_limits_restart():
    service = (OPS / "maziyar-portfolio-dispatcher.service").read_text()
    recovery = (OPS / "maziyar-portfolio-dispatcher-recover.service").read_text()
    watchdog_unit = (OPS / "maziyar-portfolio-dispatcher-watchdog.service").read_text()
    timer = (OPS / "maziyar-portfolio-dispatcher-watchdog.timer").read_text()
    readme = (OPS / "README.md").read_text()
    assert "EnvironmentFile=-/etc/maziyar-portfolio-dispatcher.env" in service
    assert "Environment=DISPATCH_ENABLED=false" in service
    assert "ExecStart=/usr/bin/env DISPATCH_ENABLED=false " in service
    assert "--serve" in service
    assert "Restart=on-failure" in service
    assert "StartLimitBurst=3" in service
    assert "OnFailure=maziyar-portfolio-dispatcher-recover.service" in watchdog_unit
    assert "ConditionPathExists=/srv/maziyar-wp-mcp/deploy/portfolio_dispatcher_watchdog.py" in watchdog_unit
    assert "ExecStartPre=/usr/bin/test -r /srv/maziyar-wp-mcp/deploy/portfolio_dispatcher_watchdog.py" in watchdog_unit
    assert "/usr/bin/python3 /srv/maziyar-wp-mcp/deploy/portfolio_dispatcher_watchdog.py" in watchdog_unit
    assert "/srv/maziyar-ai-src/AdaAI/ops/portfolio-dispatcher" not in watchdog_unit
    assert "ReadOnlyPaths=/srv/maziyar-wp-mcp/state /srv/maziyar-wp-mcp/deploy" in watchdog_unit
    assert "--max-heartbeat-age 180" in watchdog_unit
    assert "Group=maziyarid" in watchdog_unit
    assert "install -o root -g root -m 0644" in readme
    assert "install -o maziyarid" not in readme
    assert "OnUnitActiveSec=2min" in timer
    assert "StartLimitIntervalSec=3600" in recovery
    assert "StartLimitBurst=3" in recovery
    assert "systemctl restart maziyar-portfolio-dispatcher.service" in recovery
    assert "try-restart maziyar-portfolio-dispatcher.service" not in recovery


def test_materially_future_heartbeat_requests_recovery(tmp_path):
    now = 2_000_000_000.0
    hb = datetime.fromtimestamp(now + 31, tz=timezone.utc).isoformat()
    db = make_db(tmp_path / "factory.sqlite3", hb)
    result = watchdog.inspect(db, now_epoch=now, max_heartbeat_age=180, max_future_skew=30)
    assert result["status"] == "unhealthy"
    assert result["reason"] == "heartbeat_future"
    assert result["restart_recommended"] is True


def test_small_future_clock_skew_is_tolerated(tmp_path):
    now = 2_000_000_000.0
    hb = datetime.fromtimestamp(now + 10, tz=timezone.utc).isoformat()
    db = make_db(tmp_path / "factory.sqlite3", hb)
    result = watchdog.inspect(db, now_epoch=now, max_heartbeat_age=180, max_future_skew=30)
    assert result["status"] == "healthy"
    assert result["restart_recommended"] is False
