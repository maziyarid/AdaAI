#!/usr/bin/env python3
"""Bounded, read-only health inspection for the standalone Ada bot."""
import json
import os
from pathlib import Path
import sqlite3
import stat
import time

STATE = Path("/var/lib/ada-telegram-bot")
MAX_STATUS_BYTES = 4096
DATABASE_BUDGET_SECONDS = 2.0


def read_status(path):
    with path.open("rb") as stream:
        data = stream.read(MAX_STATUS_BYTES + 1)
    if len(data) > MAX_STATUS_BYTES:
        raise ValueError("status too large")
    try:
        result = json.loads(data)
    except RecursionError:
        raise ValueError("status nesting invalid") from None
    if not isinstance(result, dict):
        raise ValueError("status is not an object")
    return result


def positive_integer(value):
    return type(value) is int and value > 0


def inspect_health(state):
    result = {
        "ok": False, "ready": False, "heartbeat_age": None, "state": "unknown",
        "database_ok": False, "process_alive": False,
        "outbox_queued": None, "outbox_dead": None, "inbound_pending": None,
        "errors": [],
    }
    errors = result["errors"]
    ready = None
    heartbeat = None
    try:
        ready = read_status(state / "ready.json")
        result["ready"] = positive_integer(ready.get("pid")) and bool(
            isinstance(ready.get("ready_at"), str) and ready["ready_at"]
        )
    except (OSError, ValueError, TypeError):
        pass
    if not result["ready"]:
        errors.append("readiness_invalid")

    try:
        heartbeat = read_status(state / "heartbeat.json")
        epoch = heartbeat.get("epoch")
        if not positive_integer(epoch) or not positive_integer(heartbeat.get("pid")):
            raise ValueError("invalid heartbeat")
        result["heartbeat_age"] = int(time.time()) - epoch
        if heartbeat.get("state") in ("running", "degraded", "stopped"):
            result["state"] = heartbeat["state"]
        if not 0 <= result["heartbeat_age"] <= 90 or result["state"] not in ("running", "degraded"):
            raise ValueError("heartbeat unavailable")
    except (OSError, ValueError, TypeError, OverflowError):
        errors.append("heartbeat_invalid")

    if result["ready"] and heartbeat is not None:
        if ready["pid"] != heartbeat.get("pid"):
            errors.append("process_mismatch")
        else:
            try:
                os.kill(ready["pid"], 0)
                result["process_alive"] = True
            except (OSError, OverflowError):
                errors.append("process_unavailable")

    connection = None
    try:
        database = state / "state.sqlite3"
        metadata = database.stat()
        if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o600:
            raise ValueError("database permissions invalid")
        # mode=ro never creates a missing database; do not use immutable=1,
        # which can ignore uncheckpointed WAL transactions.
        connection = sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True, timeout=DATABASE_BUDGET_SECONDS)
        deadline = time.monotonic() + DATABASE_BUDGET_SECONDS
        connection.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
        connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN")
        if connection.execute("PRAGMA quick_check(1)").fetchone() != ("ok",):
            raise ValueError("database integrity invalid")
        counts = [
            connection.execute("SELECT count(*) FROM outbox WHERE status='queued'").fetchone()[0],
            connection.execute("SELECT count(*) FROM outbox WHERE status='dead'").fetchone()[0],
            connection.execute("SELECT count(*) FROM inbound WHERE state='pending'").fetchone()[0],
        ]
        result.update(zip(("outbox_queued", "outbox_dead", "inbound_pending"), counts))
        result["database_ok"] = True
    except (OSError, sqlite3.Error, ValueError):
        errors.append("database_unavailable")
    finally:
        if connection is not None:
            connection.close()

    result["ok"] = bool(
        result["ready"] and result["process_alive"] and result["database_ok"] and not errors
    )
    return result


def main():
    result = inspect_health(STATE)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
