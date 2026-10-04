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
MAX_STATUS_DEPTH = 64
DATABASE_BUDGET_SECONDS = 2.0


def open_regular_no_follow(path):
    try:
        no_follow = os.O_NOFOLLOW
    except AttributeError:
        raise OSError("no-follow file opens are unsupported") from None
    directory_flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | no_follow
    file_flags = os.O_RDONLY | os.O_CLOEXEC | no_follow
    directory_fd = os.open(path.parent, directory_flags)
    try:
        fd = os.open(path.name, file_flags, dir_fd=directory_fd)
    finally:
        os.close(directory_fd)
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise OSError("state entry is not a regular file")
        return fd, metadata
    except Exception:
        os.close(fd)
        raise


def unique_status_object(pairs):
    # Do not discard earlier values before depth validation, or a duplicate
    # member could conceal an overdeep value (including escaped key spellings).
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate status member")
        result[key] = value
    return result


def read_status(path):
    fd, _ = open_regular_no_follow(path)
    with os.fdopen(fd, "rb", closefd=True) as stream:
        data = stream.read(MAX_STATUS_BYTES + 1)
    if len(data) > MAX_STATUS_BYTES:
        raise ValueError("status too large")
    try:
        result = json.loads(data, object_pairs_hook=unique_status_object)
    except RecursionError:
        raise ValueError("status nesting invalid") from None
    if not isinstance(result, dict):
        raise ValueError("status is not an object")
    # Decoder recursion allowances differ between Python versions/builds.
    # Enforce our own bound without recursing or changing global interpreter
    # limits. The existing byte cap also bounds the size of this worklist.
    pending = [(result, 1)]
    while pending:
        value, depth = pending.pop()
        if isinstance(value, (dict, list)):
            if depth > MAX_STATUS_DEPTH:
                raise ValueError("status nesting invalid")
            children = value.values() if isinstance(value, dict) else value
            pending.extend((child, depth + 1) for child in children)
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
    database_fd = None
    try:
        database = state / "state.sqlite3"
        database_fd, metadata = open_regular_no_follow(database)
        if stat.S_IMODE(metadata.st_mode) != 0o600:
            raise ValueError("database permissions invalid")
        # Use the already-open no-follow descriptor so a writable state directory
        # cannot redirect health inspection through a symlink or path swap.
        # mode=ro never creates a missing database; do not use immutable=1,
        # which can ignore uncheckpointed WAL transactions.
        database_uri = f"file:/proc/self/fd/{database_fd}?mode=ro"
        connection = sqlite3.connect(database_uri, uri=True, timeout=DATABASE_BUDGET_SECONDS)
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
        if database_fd is not None:
            os.close(database_fd)

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
