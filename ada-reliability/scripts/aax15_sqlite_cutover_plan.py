#!/usr/bin/env python3
"""Build a READ-ONLY AAX-15 SQLite -> MariaDB cutover plan.

This does not apply SQL, mutate the SQLite source, stop services, or switch
runtime authority. It refuses an unsafe snapshot (inflight/retryable/queued or
unknown lifecycle rows) so operators cannot accidentally plan a dual-authority
cutover while replay work is active.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

SAFE_TERMINAL = {"succeeded", "dead_letter"}
SAFE_PARKED = {"parked"}
UNSAFE_ACTIVE = {"queued", "retryable", "inflight"}
KNOWN = SAFE_TERMINAL | SAFE_PARKED | UNSAFE_ACTIVE
NAMESPACE = uuid.UUID("151ff1b8-a238-4bb7-91fb-8e4e10f88a15")

OUTBOX_REQUIRED = {
    "stable_id", "idempotency_key", "worker", "run_id", "event_type", "state",
    "failure_class", "reason", "schedule", "factory_task_id", "packet_ref",
    "artifact_ref", "payload_json", "reset_condition", "attempts", "max_attempts",
    "first_failed_at", "last_failed_at", "next_eligible_at", "leased_by",
    "lease_until", "external_sync_state", "completed_at", "created_at", "updated_at",
}
RUN_REQUIRED = {
    "worker", "run_id", "schedule", "site", "state", "status_json",
    "evidence_ref", "created_at", "updated_at",
}


class CutoverError(RuntimeError):
    pass


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {str(r[1]) for r in conn.execute(f"PRAGMA table_info({table})")}


def parse_payload(raw: str | None) -> dict:
    if not raw:
        return {}
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise CutoverError("pd_outbox payload_json must contain a JSON object")
    return obj


def normalise_external_sync_state(raw: str | None, delegated: bool = False) -> str:
    value = str(raw or "").strip()
    if delegated:
        return "delegated_control_core"
    if not value:
        return "none"
    if value.startswith("AGIFLOW_SYNCED:"):
        return "agiflow_synced"
    if value.startswith("CONTROL_CORE_PENDING:"):
        return "control_core_pending"
    if len(value) <= 32:
        return value
    return "legacy_external_state"


def mutation_kind(event_type: str, state: str, delegated: bool = False) -> str:
    if delegated:
        return "none"
    if state == "parked" and event_type == "agiflow_sync":
        return "agiflow_sync"
    return "none"
