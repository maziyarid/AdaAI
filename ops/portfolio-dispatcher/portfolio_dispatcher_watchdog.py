#!/usr/bin/env python3
"""Read-only health check for the staged portfolio dispatcher supervisor."""
from __future__ import annotations

import argparse
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any

COMPONENT = "portfolio-dispatcher-01"


class WatchdogError(RuntimeError):
    pass


def parse_iso_epoch(raw: str) -> float:
    value = str(raw or "").strip()
    if not value:
        raise WatchdogError("empty heartbeat timestamp")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError as exc:
        raise WatchdogError("invalid heartbeat timestamp") from exc


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return bool(conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone())


def inspect(
    sqlite_path: Path,
    *,
    component: str = COMPONENT,
    max_heartbeat_age: int = 180,
    now_epoch: float | None = None,
) -> dict[str, Any]:
    if max_heartbeat_age < 30:
        raise WatchdogError("max heartbeat age must be >= 30 seconds")
    if not sqlite_path.is_file():
        return {"status": "blocked", "restart_recommended": False,
                "reason": "state_db_missing", "sqlite": str(sqlite_path)}

    now = time.time() if now_epoch is None else float(now_epoch)
    uri = "file:" + str(sqlite_path.resolve()) + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        needed = {"pd_heartbeat", "pd_leases", "pd_circuits"}
        missing = sorted(t for t in needed if not table_exists(conn, t))
        if missing:
            return {"status": "blocked", "restart_recommended": False,
                    "reason": "dispatcher_schema_missing", "missing_tables": missing}

        hb = conn.execute(
            "SELECT component,heartbeat_at,state_json FROM pd_heartbeat WHERE component=?",
            (component,),
        ).fetchone()
        stale_leases = [dict(r) for r in conn.execute(
            "SELECT resource,lease_owner,lease_expires_at,attempt,state "
            "FROM pd_leases WHERE state='active' AND lease_expires_at<=? ORDER BY resource",
            (now,),
        )]
        open_circuits = [dict(r) for r in conn.execute(
            "SELECT resource,state,failure_count,opened_at,reset_after_epoch "
            "FROM pd_circuits WHERE state='open' ORDER BY resource"
        )]
    finally:
        conn.close()

    common = {"component": component, "stale_leases": stale_leases,
              "open_circuits": open_circuits}
    if hb is None:
        return {**common, "status": "unhealthy", "restart_recommended": True,
                "reason": "heartbeat_missing"}

    try:
        hb_epoch = parse_iso_epoch(hb["heartbeat_at"])
    except WatchdogError:
        return {**common, "status": "unhealthy", "restart_recommended": True,
                "reason": "heartbeat_invalid", "heartbeat_at": hb["heartbeat_at"]}

    age = max(0.0, now - hb_epoch)
    try:
        state_json = json.loads(hb["state_json"] or "{}")
    except json.JSONDecodeError:
        state_json = {"_invalid_json": True}

    common.update({
        "heartbeat_at": hb["heartbeat_at"],
        "heartbeat_age_seconds": round(age, 3),
        "max_heartbeat_age_seconds": max_heartbeat_age,
        "dispatcher_state": state_json,
    })
    if age > max_heartbeat_age:
        return {**common, "status": "unhealthy", "restart_recommended": True,
                "reason": "heartbeat_stale"}

    if stale_leases or open_circuits:
        return {**common, "status": "degraded", "restart_recommended": False,
                "reason": "durable_recovery_attention"}
    return {**common, "status": "healthy", "restart_recommended": False, "reason": "ok"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sqlite", required=True, type=Path)
    ap.add_argument("--component", default=COMPONENT)
    ap.add_argument("--max-heartbeat-age", type=int, default=180)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    try:
        result = inspect(args.sqlite, component=args.component,
                         max_heartbeat_age=args.max_heartbeat_age)
    except (WatchdogError, sqlite3.Error) as exc:
        result = {"status": "blocked", "restart_recommended": False,
                  "reason": "watchdog_error", "error": str(exc)}
    print(json.dumps(result, sort_keys=True))
    if result.get("restart_recommended"):
        return 2
    if args.strict and result.get("status") != "healthy":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
