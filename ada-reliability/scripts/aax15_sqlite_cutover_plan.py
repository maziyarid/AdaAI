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


def mutation_kind(event_type: str, state: str) -> str:
    # Only the currently parked live class must retain executable replay meaning.
    # Terminal rows are historical evidence and must never become replayable by import.
    if state == "parked" and event_type == "agiflow_sync":
        return "agiflow_sync"
    return "none"


def map_outbox_row(row: dict, job_bindings: dict[str, str] | None = None) -> dict:
    state = str(row["state"])
    stable_id = str(row["stable_id"])
    payload = parse_payload(row.get("payload_json"))
    job_bindings = job_bindings or {}
    payload_job_id = str(payload.get("durable_job_id") or "").strip()
    durable_job_id = str(job_bindings.get(stable_id) or payload_job_id or "").strip() or None
    payload = {
        **payload,
        "_legacy_pd_outbox": {
            "stable_id": stable_id,
            "event_type": row.get("event_type"),
            "completed_at": row.get("completed_at"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
    }
    return {
        "id": str(uuid.uuid5(NAMESPACE, "pd_outbox:" + stable_id)),
        # Preserve the live idempotency key exactly. Re-keying would break
        # duplicate suppression across the authority switch.
        "idempotency_key": str(row["idempotency_key"]),
        "run_id": str(row["run_id"]),
        "worker": str(row["worker"]),
        "schedule_id": row.get("schedule") or None,
        "durable_job_id": durable_job_id,
        "factory_task_id": row.get("factory_task_id") or None,
        "packet_id": row.get("packet_ref") or None,
        "artifact_id": row.get("artifact_ref") or None,
        "failure_class": row.get("failure_class") or "LEGACY_UNCLASSIFIED",
        "failure_reason": row.get("reason") or "",
        "lifecycle": state,
        "attempt_count": int(row.get("attempts") or 0),
        "max_attempts": int(row.get("max_attempts") or 5),
        "first_failed_at": row.get("first_failed_at"),
        "last_failed_at": row.get("last_failed_at"),
        "next_retry_at": row.get("next_eligible_at") or None,
        "reset_condition": row.get("reset_condition") or None,
        "external_sync_state": row.get("external_sync_state") or "none",
        "mutation_kind": mutation_kind(str(row.get("event_type") or ""), state),
        "mutation_idempotency_key": str(row["idempotency_key"]),
        "sync_marker": stable_id[:96],
        "payload": payload,
        "last_error": None if state == "succeeded" else (row.get("reason") or None),
        # Safe cutover requires no active claims. Never carry SQLite lease state.
        "lease_owner": None,
        "lease_until": None,
        "claim_generation": 0,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def build_plan(sqlite_path: Path, job_bindings: dict[str, str] | None = None) -> dict:
    if not sqlite_path.is_file():
        raise CutoverError(f"SQLite source not found: {sqlite_path}")
    uri = "file:" + str(sqlite_path.resolve()) + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        quick = conn.execute("PRAGMA quick_check").fetchone()[0]
        if quick != "ok":
            raise CutoverError(f"SQLite quick_check failed: {quick}")
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        missing_tables = {"pd_worker_runs", "pd_outbox"} - tables
        if missing_tables:
            raise CutoverError("missing required tables: " + ",".join(sorted(missing_tables)))
        missing_outbox = OUTBOX_REQUIRED - columns(conn, "pd_outbox")
        missing_runs = RUN_REQUIRED - columns(conn, "pd_worker_runs")
        if missing_outbox or missing_runs:
            raise CutoverError(
                "schema mismatch outbox_missing="
                + ",".join(sorted(missing_outbox))
                + " runs_missing="
                + ",".join(sorted(missing_runs))
            )

        outbox = [dict(r) for r in conn.execute("SELECT * FROM pd_outbox ORDER BY id")]
        worker_runs = [dict(r) for r in conn.execute(
            "SELECT worker,run_id,schedule,site,state,status_json,evidence_ref,created_at,updated_at "
            "FROM pd_worker_runs ORDER BY worker,run_id"
        )]
    finally:
        conn.close()

    states: dict[str, int] = {}
    for row in outbox:
        state = str(row.get("state") or "")
        states[state] = states.get(state, 0) + 1

    unsafe = sorted(s for s in states if s in UNSAFE_ACTIVE)
    unknown = sorted(s for s in states if s not in KNOWN)
    if unsafe:
        raise CutoverError("active replay rows must be drained or deliberately parked before cutover: " + ",".join(unsafe))
    if unknown:
        raise CutoverError("unknown pd_outbox lifecycle(s): " + ",".join(unknown))

    stable = [str(r["stable_id"]) for r in outbox]
    idem = [str(r["idempotency_key"]) for r in outbox]
    if len(stable) != len(set(stable)) or len(idem) != len(set(idem)):
        raise CutoverError("pd_outbox uniqueness invariant violated")

    job_bindings = job_bindings or {}
    unknown_bindings = sorted(set(job_bindings) - set(stable))
    if unknown_bindings:
        raise CutoverError(
            "job binding supplied for unknown stable_id(s): " + ",".join(unknown_bindings)
        )

    mapped = [map_outbox_row(r, job_bindings) for r in outbox]
    missing_job_bindings = sorted(
        row["sync_marker"]
        for row in mapped
        if row["mutation_kind"] == "agiflow_sync" and not row["durable_job_id"]
    )
    cutover_ready = not missing_job_bindings
    return {
        "format": "aax15-cutover-plan-v1",
        "source": {
            "kind": "sqlite",
            "path": str(sqlite_path),
            "outbox_rows": len(outbox),
            "worker_run_rows": len(worker_runs),
            "state_counts": states,
            "outbox_digest": digest(outbox),
            "worker_runs_digest": digest(worker_runs),
            "schema_verified": True,
            "quick_check": "ok",
        },
        "decision": {
            "future_recovery_authority": "control-core MariaDB ada_failed_runs",
            "legacy_recovery_authority": "SQLite pd_outbox",
            "authority_switch": "quiescent-single-writer",
            "dual_write_allowed": False,
            "legacy_after_cutover": "read-only historical evidence only",
            "pd_worker_runs_strategy": "retain read-only as historical run ledger; do not use for replay after cutover",
        },
        "preconditions": {
            "active_replay_rows": 0,
            "parked_rows": states.get("parked", 0),
            "explicit_human_apply_approval_required": True,
            "encrypted_backup_and_off_host_key_required": True,
            "runtime_writer_switch_required_before_reenable": True,
            "missing_durable_job_bindings": missing_job_bindings,
        },
        "target": {
            "migration": "006_ada_failed_run_outbox.sql",
            "table": "ada_failed_runs",
            "rows": mapped,
            "row_digest": digest(mapped),
        },
        "cutover_ready_for_approved_maintenance_window": cutover_ready,
        "production_sql_applied": False,
        "runtime_switched": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sqlite", required=True, type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument(
        "--job-binding",
        action="append",
        default=[],
        metavar="STABLE_ID=DURABLE_JOB_ID",
        help="Explicit durable control-core job binding for replayable legacy Agiflow rows.",
    )
    args = ap.parse_args()
    bindings: dict[str, str] = {}
    try:
        for raw in args.job_binding:
            stable_id, sep, job_id = raw.partition("=")
            stable_id, job_id = stable_id.strip(), job_id.strip()
            if not sep or not stable_id or not job_id:
                raise CutoverError("--job-binding must be STABLE_ID=DURABLE_JOB_ID")
            if stable_id in bindings and bindings[stable_id] != job_id:
                raise CutoverError("conflicting --job-binding for " + stable_id)
            bindings[stable_id] = job_id
        plan = build_plan(args.sqlite, bindings)
    except (CutoverError, sqlite3.Error, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 2
    text = json.dumps(plan, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
