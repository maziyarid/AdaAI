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


def map_outbox_row(
    row: dict,
    job_bindings: dict[str, str] | None = None,
    external_sync_delegations: dict[str, str] | None = None,
) -> dict:
    state = str(row["state"])
    stable_id = str(row["stable_id"])
    payload = parse_payload(row.get("payload_json"))
    job_bindings = job_bindings or {}
    external_sync_delegations = external_sync_delegations or {}
    delegation = str(external_sync_delegations.get(stable_id) or "").strip() or None
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
            "external_sync_state": row.get("external_sync_state") or "",
            "delegated_external_sync_stable_id": delegation,
        },
    }
    return {
        "id": str(uuid.uuid5(NAMESPACE, "pd_outbox:" + stable_id)),
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
        "external_sync_state": normalise_external_sync_state(
            row.get("external_sync_state"), delegated=bool(delegation)
        ),
        "mutation_kind": mutation_kind(
            str(row.get("event_type") or ""), state, delegated=bool(delegation)
        ),
        "mutation_idempotency_key": str(row["idempotency_key"]),
        "sync_marker": stable_id[:96],
        "payload": payload,
        "last_error": None if state == "succeeded" else (row.get("reason") or None),
        "lease_owner": None,
        "lease_until": None,
        "claim_generation": 0,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def load_control_core_catalog(catalog: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    """Independent control-core ownership map.

    Keys are control-core record ids. Values must bind the same external
    stable id and legacy idempotency key that the SQLite row carries.
    Caller-supplied proof text is not authority by itself.
    """
    if not catalog:
        return {}
    loaded: dict[str, dict[str, str]] = {}
    for record_id, raw in catalog.items():
        rid = str(record_id).strip()
        if not rid:
            raise CutoverError("control-core catalog contains an empty record id")
        if not isinstance(raw, dict):
            raise CutoverError("control-core catalog record must be an object: " + rid)
        external = str(raw.get("external_stable_id") or "").strip()
        idem = str(raw.get("idempotency_key") or "").strip()
        source = str(raw.get("source") or "control-core").strip() or "control-core"
        if not external or not idem:
            raise CutoverError(
                "control-core catalog record must bind external_stable_id and idempotency_key: "
                + rid
            )
        if rid in {external, idem} or rid.startswith("agiflow:"):
            raise CutoverError(
                "control-core catalog record id must be independent of the SQLite row: " + rid
            )
        loaded[rid] = {
            "external_stable_id": external,
            "idempotency_key": idem,
            "source": source,
        }
    return loaded


def build_plan(
    sqlite_path: Path,
    job_bindings: dict[str, str] | None = None,
    external_sync_delegations: dict[str, str] | None = None,
    control_core_catalog: dict[str, Any] | None = None,
) -> dict:
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
    external_sync_delegations = external_sync_delegations or {}
    unknown_bindings = sorted(set(job_bindings) - set(stable))
    if unknown_bindings:
        raise CutoverError(
            "job binding supplied for unknown stable_id(s): " + ",".join(unknown_bindings)
        )
    unknown_delegations = sorted(set(external_sync_delegations) - set(stable))
    if unknown_delegations:
        raise CutoverError(
            "external-sync delegation supplied for unknown stable_id(s): "
            + ",".join(unknown_delegations)
        )
    overlap = sorted(set(job_bindings) & set(external_sync_delegations))
    if overlap:
        raise CutoverError(
            "row cannot have both durable job binding and external-sync delegation: "
            + ",".join(overlap)
        )

    by_stable = {str(r["stable_id"]): r for r in outbox}
    parsed_delegations: dict[str, dict[str, str]] = {}
    for stable_id, proof in external_sync_delegations.items():
        row = by_stable[stable_id]
        if str(row.get("event_type") or "") != "agiflow_sync":
            raise CutoverError(
                "external-sync delegation is only valid for agiflow_sync row: " + stable_id
            )
        parts = [p.strip() for p in str(proof).split("|")]
        if len(parts) != 3 or not all(parts):
            raise CutoverError(
                "external-sync delegation requires control-core proof "
                "agiflow:<stable_id>|<idempotency_key>|<control_core_record_id> for "
                + stable_id
            )
        external_stable, proof_idem, control_core_record_id = parts
        expected = "agiflow:" + stable_id
        if external_stable != expected:
            raise CutoverError(
                "external-sync delegation stable_id mismatch for "
                + stable_id
                + ": expected="
                + expected
            )
        row_idem = str(row.get("idempotency_key") or "").strip()
        if proof_idem != row_idem:
            raise CutoverError(
                "external-sync delegation idempotency_key mismatch for "
                + stable_id
                + ": expected="
                + row_idem
            )
        if control_core_record_id in {stable_id, expected, row_idem}:
            raise CutoverError(
                "external-sync delegation control-core record must be independent of the SQLite row: "
                + stable_id
            )
        catalog = load_control_core_catalog(control_core_catalog)
        if not catalog:
            raise CutoverError(
                "external-sync delegation requires an authoritative control-core catalog "
                "bound to the legacy idempotency key for " + stable_id
            )
        record = catalog.get(control_core_record_id)
        if record is None:
            raise CutoverError(
                "control-core catalog does not contain record "
                + control_core_record_id
                + " for "
                + stable_id
            )
        if record["external_stable_id"] != expected or record["idempotency_key"] != row_idem:
            raise CutoverError(
                "control-core catalog record does not own the exact recovery obligation for "
                + stable_id
            )
        parsed_delegations[stable_id] = {
            "external_stable_id": external_stable,
            "idempotency_key": proof_idem,
            "control_core_record_id": control_core_record_id,
            "catalog_source": record["source"],
        }

    for row in outbox:
        stable_id = str(row["stable_id"])
        explicit = str(job_bindings.get(stable_id) or "").strip()
        payload_job = str(parse_payload(row.get("payload_json")).get("durable_job_id") or "").strip()
        if explicit and payload_job and explicit != payload_job:
            raise CutoverError(
                "conflicting durable job binding for "
                + stable_id
                + ": payload="
                + payload_job
                + " explicit="
                + explicit
            )

    mapped = [map_outbox_row(r, job_bindings, external_sync_delegations) for r in outbox]
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
            "delegated_external_sync_rows": sorted(external_sync_delegations),
            "delegated_control_core_records": {
                sid: parsed_delegations[sid]["control_core_record_id"]
                for sid in sorted(parsed_delegations)
            },
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
    ap.add_argument(
        "--external-sync-delegation",
        action="append",
        default=[],
        metavar="STABLE_ID=PROOF",
        help="Verified control-core ownership: STABLE_ID=agiflow:STABLE_ID|IDEMPOTENCY_KEY|CONTROL_CORE_RECORD_ID",
    )
    ap.add_argument(
        "--control-core-catalog",
        type=Path,
        help="JSON map of control-core record_id -> {external_stable_id, idempotency_key, source}",
    )
    args = ap.parse_args()
    bindings: dict[str, str] = {}
    delegations: dict[str, str] = {}
    try:
        for raw in args.job_binding:
            stable_id, sep, job_id = raw.partition("=")
            stable_id, job_id = stable_id.strip(), job_id.strip()
            if not sep or not stable_id or not job_id:
                raise CutoverError("--job-binding must be STABLE_ID=DURABLE_JOB_ID")
            if stable_id in bindings and bindings[stable_id] != job_id:
                raise CutoverError("conflicting --job-binding for " + stable_id)
            bindings[stable_id] = job_id
        for raw in args.external_sync_delegation:
            stable_id, sep, external_stable = raw.partition("=")
            stable_id, external_stable = stable_id.strip(), external_stable.strip()
            if not sep or not stable_id or not external_stable:
                raise CutoverError(
                    "--external-sync-delegation must be STABLE_ID=agiflow:STABLE_ID|IDEMPOTENCY_KEY|CONTROL_CORE_RECORD_ID"
                )
            if stable_id in delegations and delegations[stable_id] != external_stable:
                raise CutoverError("conflicting --external-sync-delegation for " + stable_id)
            delegations[stable_id] = external_stable
        catalog = None
        if args.control_core_catalog is not None:
            raw_catalog = json.loads(args.control_core_catalog.read_text(encoding="utf-8"))
            if not isinstance(raw_catalog, dict):
                raise CutoverError("--control-core-catalog must be a JSON object")
            catalog = raw_catalog
        plan = build_plan(args.sqlite, bindings, delegations, control_core_catalog=catalog)
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
