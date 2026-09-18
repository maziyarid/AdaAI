"""AAX-15 durable failed-run outbox (execution recovery).

DISTINCT from `agiflow_steward` / `ada_agiflow_outbox` (AAX-12). That outbox
replays Agiflow *projection* when Agiflow is down. This outbox retains the
failed/blocked *scheduled execution itself* so it can be replayed after a
dependency recovers.

Not a scheduler. It must never enqueue jobs, create schedules, acquire leases
or apply WordPress/packet mutations. AdaEngine remains the mutation path.
MariaDB control-core remains runtime truth. Chat, in-memory objects and
Agiflow comments are not durable recovery.

Live VPS currently has `pd_worker_runs` / `pd_outbox` (ChatGPT AAX-15 canary).
The additive `ada_failed_runs` schema is the Phase-1 contract to reconcile at
apply time (AAX-7). Do not treat in-process tests as production persistence.
"""

from __future__ import annotations

import copy
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Protocol

from .crypto import sha256_obj, utcnow
from .engine import AdaError


# -- lifecycle (durable) ----------------------------------------------------

LIFECYCLE_QUEUED = "queued"          # persisted, waiting for replay worker
LIFECYCLE_RETRYABLE = "retryable"
LIFECYCLE_INFLIGHT = "inflight"
LIFECYCLE_PARKED = "parked"
LIFECYCLE_SUCCEEDED = "succeeded"
LIFECYCLE_DEAD_LETTER = "dead_letter"
LIFECYCLE_QUARANTINED = "quarantined"

OPEN_LIFECYCLES = frozenset({
    LIFECYCLE_QUEUED, LIFECYCLE_RETRYABLE, LIFECYCLE_INFLIGHT,
})
CLAIMABLE = frozenset({LIFECYCLE_QUEUED, LIFECYCLE_RETRYABLE})
TERMINAL = frozenset({
    LIFECYCLE_SUCCEEDED, LIFECYCLE_DEAD_LETTER, LIFECYCLE_QUARANTINED,
})

# -- RUN_STATUS.replay reports (only after persist succeeds) ----------------

REPLAY_QUEUED = "queued"
REPLAY_PARKED = "parked"
REPLAY_RETRYABLE = "retryable"
REPLAY_UNAVAILABLE = "UNAVAILABLE"

# -- failure classes --------------------------------------------------------

CLASS_TRANSIENT = "TRANSIENT_CONNECTIVITY"
CLASS_TIMEOUT = "TIMEOUT"
CLASS_AGIFLOW_UNAVAILABLE = "AGIFLOW_UNAVAILABLE"
CLASS_PENDING_EXTERNAL_SYNC = "PENDING_EXTERNAL_SYNC"
CLASS_FACTORY_PACKET_MISSING = "FACTORY_PACKET_MISSING"
CLASS_PACKET_PIPELINE = "PACKET_PIPELINE_FAILURE"
CLASS_OOM = "RESOURCE_OOM_SIGKILL"
CLASS_DETERMINISTIC = "DETERMINISTIC_BLOCKER"

PARKED_CLASSES = frozenset({
    CLASS_FACTORY_PACKET_MISSING,
    CLASS_PACKET_PIPELINE,
    CLASS_OOM,
    CLASS_DETERMINISTIC,
})
QUEUED_CLASSES = frozenset({
    CLASS_AGIFLOW_UNAVAILABLE,
    CLASS_PENDING_EXTERNAL_SYNC,
})
DEFAULT_RESET = {
    CLASS_FACTORY_PACKET_MISSING: "packet_available",
    CLASS_PACKET_PIPELINE: "pipeline_healthy",
    CLASS_OOM: "memory_pressure_resolved",
    CLASS_DETERMINISTIC: "blocker_cleared",
}

# Production mutation kinds this module must never apply directly.
PRODUCTION_MUTATION_KINDS = frozenset({
    "wordpress_mutation",
    "packet_ack",
    "agiflow_task",
    "agiflow_comment",
    "agiflow_transition",
})
# Persistence and replay both fail closed outside this set.
SUPPORTED_MUTATION_KINDS = frozenset({"none"}) | PRODUCTION_MUTATION_KINDS | frozenset({
    "agiflow_sync",
})
ENGINE_SUCCESS = frozenset({"APPLIED", "DUPLICATE_SKIPPED"})
ENGINE_RETRYABLE = frozenset({"FAILED", "EXECUTING", "REQUIRES_ENGINE", "UNAVAILABLE", "ENGINE_RETRY"})
# Actual engine replay attempts that must consume retry budget.
ENGINE_CONSUMES_ATTEMPT = frozenset({"FAILED", "EXECUTING", "ENGINE_RETRY"})

DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_BATCH_LIMIT = 10
HARD_BATCH_CAP = 32
DEFAULT_LEASE_SECONDS = 60

RUNTIME_WRITE_METHODS = (
    "enqueue", "create_job", "schedule", "create_schedule",
    "acquire_lease", "release_lease", "retry_job", "cancel_job",
)


def _now(clock: Optional[Callable[[], datetime]]) -> datetime:
    return clock() if clock else utcnow()


def classify_failure(
    *,
    failure_class: Optional[str] = None,
    exit_code: Optional[int] = None,
    reason: str = "",
) -> str:
    """Map worker/process evidence onto a durable failure class."""
    if exit_code in (137, -9) or failure_class == CLASS_OOM:
        return CLASS_OOM
    blob = f"{failure_class or ''} {reason or ''}"
    if failure_class in PARKED_CLASSES:
        return failure_class
    if "FACTORY_PACKET_MISSING" in blob:
        return CLASS_FACTORY_PACKET_MISSING
    if "PACKET_PIPELINE" in blob:
        return CLASS_PACKET_PIPELINE
    if failure_class in QUEUED_CLASSES:
        return failure_class
    if failure_class in (CLASS_TRANSIENT, CLASS_TIMEOUT):
        return failure_class
    if failure_class:
        return failure_class
    return CLASS_TRANSIENT


def _lifecycle_for(failure_class: str) -> str:
    if failure_class in PARKED_CLASSES:
        return LIFECYCLE_PARKED
    if failure_class in QUEUED_CLASSES:
        return LIFECYCLE_QUEUED
    return LIFECYCLE_RETRYABLE


def _replay_report(lifecycle: str) -> str:
    if lifecycle == LIFECYCLE_PARKED:
        return REPLAY_PARKED
    if lifecycle in (LIFECYCLE_QUEUED,):
        return REPLAY_QUEUED
    return REPLAY_RETRYABLE


def sync_marker(idempotency_key: str) -> str:
    return f"[sync:{idempotency_key}]"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

class FailedRunStore(Protocol):
    def put(self, rec: dict) -> dict: ...
    def get(self, idempotency_key: str) -> Optional[dict]: ...
    def get_by_id(self, rec_id: str) -> Optional[dict]: ...
    def all(self) -> list[dict]: ...
    def append_event(self, rec_id: str, event_type: str, details: dict) -> None: ...
    def mutation_seen(self, kind: str, key: str) -> bool: ...
    def mutation_record(self, kind: str, key: str) -> None: ...
    def claim_if_eligible(
        self, rec_id: str, *, owner: str, now: datetime, lease_seconds: int,
    ) -> Optional[dict]: ...
    def expire_lease_if_match(
        self,
        rec_id: str,
        *,
        expected_lifecycle: str,
        expected_owner: Optional[str],
        expected_until: Optional[str],
        expected_generation: Optional[int],
        now: datetime,
    ) -> Optional[dict]: ...
    def dump(self) -> dict: ...


class InMemoryFailedRunStore:
    """Test double. dump()/load() simulate process restart, not VPS MariaDB.

    claim_if_eligible is a compare-and-set: it succeeds only if the row is
    still queued/retryable and due. expire_lease_if_match is the matching CAS
    for reclaim: it succeeds only if the stored row still has the expected
    expired inflight lease (id, lifecycle, owner, until, generation).
    A threading.Lock makes those CAS operations atomic in-process; MariaDB
    must use UPDATE ... WHERE lifecycle / lease_owner / lease_until /
    claim_generation. An in-process mutex alone is not the production lock.
    """

    def __init__(self):
        self.rows: dict[str, dict] = {}
        self.by_id: dict[str, str] = {}
        self.events: list[dict] = []
        self.mutations: set[tuple[str, str]] = set()
        self._lock = threading.Lock()

    def put(self, rec: dict) -> dict:
        stored = copy.deepcopy(rec)
        with self._lock:
            self.rows[stored["idempotency_key"]] = stored
            self.by_id[stored["id"]] = stored["idempotency_key"]
        return copy.deepcopy(stored)

    def get(self, idempotency_key: str) -> Optional[dict]:
        with self._lock:
            rec = self.rows.get(idempotency_key)
            return copy.deepcopy(rec) if rec else None

    def get_by_id(self, rec_id: str) -> Optional[dict]:
        with self._lock:
            key = self.by_id.get(rec_id)
            rec = self.rows.get(key) if key else None
            return copy.deepcopy(rec) if rec else None

    def all(self) -> list[dict]:
        with self._lock:
            return [copy.deepcopy(r) for r in self.rows.values()]

    def append_event(self, rec_id: str, event_type: str, details: dict) -> None:
        with self._lock:
            self.events.append({
                "failed_run_id": rec_id,
                "event_type": event_type,
                "details": copy.deepcopy(details),
            })

    def mutation_seen(self, kind: str, key: str) -> bool:
        with self._lock:
            return (kind, key) in self.mutations

    def mutation_record(self, kind: str, key: str) -> None:
        with self._lock:
            self.mutations.add((kind, key))

    def claim_if_eligible(
        self, rec_id: str, *, owner: str, now: datetime, lease_seconds: int,
    ) -> Optional[dict]:
        """CAS: transition queued/retryable → inflight only if still eligible."""
        with self._lock:
            key = self.by_id.get(rec_id)
            if key is None:
                return None
            rec = self.rows.get(key)
            if rec is None:
                return None
            if rec.get("lifecycle") not in CLAIMABLE:
                return None
            nxt = rec.get("next_retry_at")
            if nxt is not None and datetime.fromisoformat(nxt) > now:
                return None
            rec["lifecycle"] = LIFECYCLE_INFLIGHT
            rec["lease_owner"] = owner
            rec["lease_until"] = (now + timedelta(seconds=lease_seconds)).isoformat()
            rec["claim_generation"] = int(rec.get("claim_generation") or 0) + 1
            return copy.deepcopy(rec)

    def expire_lease_if_match(
        self,
        rec_id: str,
        *,
        expected_lifecycle: str,
        expected_owner: Optional[str],
        expected_until: Optional[str],
        expected_generation: Optional[int],
        now: datetime,
    ) -> Optional[dict]:
        """CAS: inflight → retryable only if the stored lease is still that lease.

        MariaDB equivalent:
          UPDATE ada_failed_runs
             SET lifecycle='retryable', lease_owner=NULL, lease_until=NULL,
                 next_retry_at=?
           WHERE id=?
             AND lifecycle='inflight'
             AND lease_owner <=> ?
             AND lease_until <=> ?
             AND (lease_until IS NULL OR lease_until <= ?)
             AND claim_generation <=> ?
        """
        with self._lock:
            key = self.by_id.get(rec_id)
            if key is None:
                return None
            rec = self.rows.get(key)
            if rec is None:
                return None
            if rec.get("lifecycle") != expected_lifecycle:
                return None
            if rec.get("lease_owner") != expected_owner:
                return None
            if rec.get("lease_until") != expected_until:
                return None
            if expected_generation is not None:
                if int(rec.get("claim_generation") or 0) != int(expected_generation):
                    return None
            until = rec.get("lease_until")
            if until and datetime.fromisoformat(until) > now:
                return None
            rec["lifecycle"] = LIFECYCLE_RETRYABLE
            rec["lease_owner"] = None
            rec["lease_until"] = None
            rec["next_retry_at"] = now.isoformat()
            return copy.deepcopy(rec)

    def dump(self) -> dict:
        with self._lock:
            return {
                "rows": copy.deepcopy(self.rows),
                "by_id": copy.deepcopy(self.by_id),
                "events": copy.deepcopy(self.events),
                "mutations": [list(t) for t in sorted(self.mutations)],
            }

    @classmethod
    def load(cls, snapshot: dict) -> "InMemoryFailedRunStore":
        store = cls()
        store.rows = copy.deepcopy(snapshot.get("rows") or {})
        store.by_id = copy.deepcopy(snapshot.get("by_id") or {})
        store.events = copy.deepcopy(snapshot.get("events") or [])
        store.mutations = {tuple(t) for t in snapshot.get("mutations") or []}
        return store


class UnavailableFailedRunStore:
    """Persist always fails — workers must report replay=UNAVAILABLE."""

    def put(self, rec: dict) -> dict:
        raise AdaError("DURABLE_STORE_UNAVAILABLE", "failed-run store is down")

    def get(self, idempotency_key: str) -> Optional[dict]:
        raise AdaError("DURABLE_STORE_UNAVAILABLE", "failed-run store is down")

    def get_by_id(self, rec_id: str) -> Optional[dict]:
        raise AdaError("DURABLE_STORE_UNAVAILABLE", "failed-run store is down")

    def all(self) -> list[dict]:
        raise AdaError("DURABLE_STORE_UNAVAILABLE", "failed-run store is down")

    def append_event(self, rec_id: str, event_type: str, details: dict) -> None:
        raise AdaError("DURABLE_STORE_UNAVAILABLE", "failed-run store is down")

    def mutation_seen(self, kind: str, key: str) -> bool:
        raise AdaError("DURABLE_STORE_UNAVAILABLE", "failed-run store is down")

    def mutation_record(self, kind: str, key: str) -> None:
        raise AdaError("DURABLE_STORE_UNAVAILABLE", "failed-run store is down")

    def claim_if_eligible(
        self, rec_id: str, *, owner: str, now: datetime, lease_seconds: int,
    ) -> Optional[dict]:
        raise AdaError("DURABLE_STORE_UNAVAILABLE", "failed-run store is down")

    def expire_lease_if_match(
        self,
        rec_id: str,
        *,
        expected_lifecycle: str,
        expected_owner: Optional[str],
        expected_until: Optional[str],
        expected_generation: Optional[int],
        now: datetime,
    ) -> Optional[dict]:
        raise AdaError("DURABLE_STORE_UNAVAILABLE", "failed-run store is down")

    def dump(self) -> dict:
        raise AdaError("DURABLE_STORE_UNAVAILABLE", "failed-run store is down")


# ---------------------------------------------------------------------------
# Outbox
# ---------------------------------------------------------------------------

@dataclass
class RunStatus:
    replay: str
    durable: bool
    idempotency_key: Optional[str] = None
    failed_run_id: Optional[str] = None
    lifecycle: Optional[str] = None
    failure_class: Optional[str] = None
    reason: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "replay": self.replay,
            "durable": self.durable,
            "idempotency_key": self.idempotency_key,
            "failed_run_id": self.failed_run_id,
            "lifecycle": self.lifecycle,
            "failure_class": self.failure_class,
            "reason": self.reason,
        }


@dataclass
class FailedRunOutbox:
    """Bounded, idempotent failed-run ledger. Not a job scheduler."""

    store: FailedRunStore
    clock: Optional[Callable[[], datetime]] = None
    steward: Any = None
    runtime: Any = None
    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    batch_limit: int = DEFAULT_BATCH_LIMIT
    lease_seconds: int = DEFAULT_LEASE_SECONDS
    engine_retry: Optional[Callable[[dict], dict]] = None
    _write_attempts: list[str] = field(default_factory=list)

    def now(self) -> datetime:
        return _now(self.clock)

    # -- worker surface -----------------------------------------------------

    def record_failure(
        self,
        *,
        run_id: str,
        worker: str,
        reason: str,
        idempotency_key: Optional[str] = None,
        failure_class: Optional[str] = None,
        exit_code: Optional[int] = None,
        schedule_id: Optional[str] = None,
        durable_job_id: Optional[str] = None,
        factory_task_id: Optional[str] = None,
        packet_id: Optional[str] = None,
        artifact_id: Optional[str] = None,
        mutation_kind: str = "none",
        mutation_idempotency_key: Optional[str] = None,
        payload: Optional[dict] = None,
        retry_after: Optional[timedelta] = None,
        reset_condition: Optional[str] = None,
        max_attempts: Optional[int] = None,
    ) -> RunStatus:
        if not run_id or not worker or not reason:
            return RunStatus(
                replay=REPLAY_UNAVAILABLE, durable=False,
                reason="missing run_id/worker/reason",
            )
        classified = classify_failure(
            failure_class=failure_class, exit_code=exit_code, reason=reason,
        )
        unknown_kind = mutation_kind not in SUPPORTED_MUTATION_KINDS
        key = idempotency_key or sha256_obj({
            "run_id": run_id, "worker": worker, "schedule_id": schedule_id or "",
            "durable_job_id": durable_job_id or "", "packet_id": packet_id or "",
            "reason": classified,
        })
        now = self.now()
        try:
            existing = self.store.get(key)
        except AdaError as err:
            if err.code == "DURABLE_STORE_UNAVAILABLE":
                return RunStatus(
                    replay=REPLAY_UNAVAILABLE, durable=False,
                    idempotency_key=key, reason=err.code,
                )
            raise

        if existing is not None:
            return self._touch_existing(existing, classified, reason, now)

        lifecycle = LIFECYCLE_PARKED if unknown_kind else _lifecycle_for(classified)
        next_retry = None
        if lifecycle != LIFECYCLE_PARKED:
            next_retry = (now + retry_after) if retry_after else now
        rec = {
            "id": str(uuid.uuid4()),
            "idempotency_key": key,
            "run_id": run_id,
            "worker": worker,
            "schedule_id": schedule_id,
            "durable_job_id": durable_job_id,
            "factory_task_id": factory_task_id,
            "packet_id": packet_id,
            "artifact_id": artifact_id,
            "failure_class": classified,
            "failure_reason": reason,
            "lifecycle": lifecycle,
            "attempt_count": 1,
            "max_attempts": int(max_attempts or self.max_attempts),
            "first_failed_at": now.isoformat(),
            "last_failed_at": now.isoformat(),
            "next_retry_at": next_retry.isoformat() if next_retry else None,
            "reset_condition": (
                "mutation_kind_supported" if unknown_kind
                else (reset_condition or DEFAULT_RESET.get(classified))
            ),
            "external_sync_state": (
                "pending" if classified in QUEUED_CLASSES else "none"
            ),
            "mutation_kind": mutation_kind,
            "mutation_idempotency_key": mutation_idempotency_key or key,
            "sync_marker": sync_marker(key),
            "payload": copy.deepcopy(payload or {}),
            "last_error": "UNKNOWN_MUTATION_KIND" if unknown_kind else reason,
            "lease_owner": None,
            "lease_until": None,
            "claim_generation": 0,
        }
        try:
            stored = self.store.put(rec)
            self.store.append_event(stored["id"], "recorded", {
                "lifecycle": lifecycle, "failure_class": classified,
            })
        except AdaError as err:
            if err.code == "DURABLE_STORE_UNAVAILABLE":
                return RunStatus(
                    replay=REPLAY_UNAVAILABLE, durable=False,
                    idempotency_key=key, reason=err.code,
                )
            raise
        return RunStatus(
            replay=_replay_report(lifecycle),
            durable=True,
            idempotency_key=key,
            failed_run_id=stored["id"],
            lifecycle=lifecycle,
            failure_class=classified,
        )

    def _touch_existing(
        self, existing: dict, classified: str, reason: str, now: datetime,
    ) -> RunStatus:
        if existing["lifecycle"] in TERMINAL:
            replay = REPLAY_PARKED if existing["lifecycle"] == LIFECYCLE_PARKED else REPLAY_QUEUED
            if existing["lifecycle"] == LIFECYCLE_SUCCEEDED:
                replay = REPLAY_QUEUED
            return RunStatus(
                replay=replay,
                durable=True,
                idempotency_key=existing["idempotency_key"],
                failed_run_id=existing["id"],
                lifecycle=existing["lifecycle"],
                failure_class=existing["failure_class"],
                reason="already_terminal",
            )
        existing["attempt_count"] = int(existing.get("attempt_count") or 0) + 1
        existing["last_failed_at"] = now.isoformat()
        existing["last_error"] = reason
        existing["failure_class"] = classified
        if existing["lifecycle"] != LIFECYCLE_PARKED:
            if existing["attempt_count"] >= int(existing.get("max_attempts") or self.max_attempts):
                existing["lifecycle"] = LIFECYCLE_DEAD_LETTER
                existing["next_retry_at"] = None
            elif existing["lifecycle"] == LIFECYCLE_INFLIGHT:
                # Lost worker: keep row, do not create a duplicate.
                pass
        try:
            stored = self.store.put(existing)
            self.store.append_event(stored["id"], "retouched", {
                "attempt_count": stored["attempt_count"],
                "lifecycle": stored["lifecycle"],
            })
        except AdaError as err:
            if err.code == "DURABLE_STORE_UNAVAILABLE":
                return RunStatus(
                    replay=REPLAY_UNAVAILABLE, durable=False,
                    idempotency_key=existing["idempotency_key"], reason=err.code,
                )
            raise
        return RunStatus(
            replay=_replay_report(stored["lifecycle"]),
            durable=True,
            idempotency_key=stored["idempotency_key"],
            failed_run_id=stored["id"],
            lifecycle=stored["lifecycle"],
            failure_class=stored["failure_class"],
        )

    # -- claim / replay -----------------------------------------------------

    def eligible(self, now: Optional[datetime] = None) -> list[dict]:
        ts = now or self.now()
        rows = []
        for rec in self.store.all():
            rec = self._expire_lease(rec, ts)
            if rec["lifecycle"] not in CLAIMABLE:
                continue
            nxt = rec.get("next_retry_at")
            if nxt is not None and datetime.fromisoformat(nxt) > ts:
                continue
            rows.append(rec)
        rows.sort(key=lambda r: (r.get("first_failed_at") or "", r["id"]))
        return rows

    def claim_batch(
        self, *, limit: Optional[int] = None, owner: str = "replay-worker",
    ) -> list[dict]:
        cap = min(int(limit or self.batch_limit), HARD_BATCH_CAP)
        if cap < 1:
            return []
        claimed: list[dict] = []
        now = self.now()
        for rec in self.eligible(now):
            if len(claimed) >= cap:
                break
            owned = self.store.claim_if_eligible(
                rec["id"], owner=owner, now=now, lease_seconds=self.lease_seconds,
            )
            if owned is None:
                continue
            self.store.append_event(owned["id"], "claimed", {"owner": owner})
            claimed.append(owned)
        return claimed

    def replay_batch(self, *, limit: Optional[int] = None) -> dict:
        claimed = self.claim_batch(limit=limit)
        applied = skipped = parked = conflicts = engine = unavailable = 0
        dead = 0
        for rec in claimed:
            result = self.replay_one(rec)
            status = result.get("status")
            if status in ("SUCCEEDED", "DUPLICATE_SKIPPED"):
                applied += 1 if status == "SUCCEEDED" else 0
                skipped += 1 if status == "DUPLICATE_SKIPPED" else 0
            elif status == "PARKED":
                parked += 1
            elif status == "CONFLICT":
                conflicts += 1
            elif status == "REQUIRES_ENGINE":
                engine += 1
            elif status == "UNAVAILABLE":
                unavailable += 1
            elif status == "DEAD_LETTER":
                dead += 1
        return {
            "claimed": len(claimed),
            "applied": applied,
            "skipped": skipped,
            "parked": parked,
            "conflicts": conflicts,
            "requires_engine": engine,
            "unavailable": unavailable,
            "dead_letter": dead,
        }

    def replay_one(self, rec: dict) -> dict:
        snapshot_owner = rec.get("lease_owner")
        snapshot_gen = rec.get("claim_generation")
        rec = self.store.get_by_id(rec["id"]) or rec
        if rec["lifecycle"] == LIFECYCLE_PARKED:
            return {"status": "PARKED", "reason": "deterministic_blocker"}
        if rec["lifecycle"] in TERMINAL:
            return {"status": rec["lifecycle"].upper(), "reason": "already_terminal"}
        if snapshot_owner is not None:
            if rec.get("lease_owner") != snapshot_owner:
                return {"status": "CONFLICT", "reason": "stale_lease"}
            if snapshot_gen is not None and int(rec.get("claim_generation") or 0) != int(snapshot_gen):
                return {"status": "CONFLICT", "reason": "stale_lease"}
        kind = rec.get("mutation_kind") or "none"
        key = rec.get("mutation_idempotency_key") or rec["idempotency_key"]

        if kind not in SUPPORTED_MUTATION_KINDS:
            return self._park(rec, "UNKNOWN_MUTATION_KIND")

        if kind in PRODUCTION_MUTATION_KINDS:
            if self.store.mutation_seen(kind, key):
                return self._succeed(rec, "duplicate_mutation_skipped", skipped=True)
            if kind in ("wordpress_mutation", "packet_ack"):
                if self.engine_retry is None:
                    return self._requeue(rec, "REQUIRES_ENGINE")
                try:
                    outcome = self.engine_retry(copy.deepcopy(rec))
                except AdaError as err:
                    if err.code == "DURABLE_STORE_UNAVAILABLE":
                        return self._requeue(rec, "UNAVAILABLE")
                    return self._fail_attempt(rec, err.code)
                return self._handle_engine_outcome(
                    rec, outcome or {}, kind=kind, key=key,
                )

            if kind.startswith("agiflow_"):
                return self._handoff_agiflow(rec, kind, key)

        if rec.get("failure_class") in QUEUED_CLASSES or kind == "agiflow_sync":
            return self._handoff_agiflow(rec, "agiflow_sync", key)

        # Transient non-mutation work: only an explicit engine success is
        # terminal. FAILED / EXECUTING / unknown results must not fall through
        # to replayed_without_mutation.
        if self.engine_retry is not None:
            try:
                outcome = self.engine_retry(copy.deepcopy(rec))
            except AdaError as err:
                if err.code == "DURABLE_STORE_UNAVAILABLE":
                    return self._requeue(rec, "UNAVAILABLE")
                return self._fail_attempt(rec, err.code)
            return self._handle_engine_outcome(
                rec, outcome or {}, kind=kind, key=key,
            )
        return self._succeed(rec, "replayed_without_mutation")

    def _handoff_agiflow(self, rec: dict, kind: str, key: str) -> dict:
        if self.store.mutation_seen(kind, key) or self.store.mutation_seen(
            "agiflow_comment", rec["sync_marker"],
        ):
            return self._succeed(rec, "duplicate_agiflow_skipped", skipped=True)
        if self.steward is None:
            rec["external_sync_state"] = "pending"
            rec["lifecycle"] = LIFECYCLE_QUEUED
            rec["lease_owner"] = None
            rec["lease_until"] = None
            self.store.put(rec)
            return {"status": "QUEUED", "reason": "no_steward", "replay": REPLAY_QUEUED}
        job_id = rec.get("durable_job_id")
        if not job_id:
            return self._park(rec, "missing_durable_job_id")
        evidence_id = (rec.get("payload") or {}).get("evidence_id")
        close_grant_id = (rec.get("payload") or {}).get("close_grant_id")
        try:
            result = self.steward.project(
                job_id, evidence_id=evidence_id, close_grant_id=close_grant_id,
            )
        except AdaError as err:
            if err.code == "AGIFLOW_UNAVAILABLE":
                rec["external_sync_state"] = "pending"
                rec["lifecycle"] = LIFECYCLE_QUEUED
                rec["lease_owner"] = None
                rec["lease_until"] = None
                rec["last_error"] = err.code
                self.store.put(rec)
                self.store.append_event(rec["id"], "pending_external_sync", {"code": err.code})
                return {"status": "QUEUED", "reason": err.code, "replay": REPLAY_QUEUED}
            if err.code in ("UNKNOWN_EVIDENCE", "FORGED_EVIDENCE", "FORGED_CLOSE_GRANT"):
                return self._park(rec, err.code)
            return self._fail_attempt(rec, err.code)
        if result.get("status") == "PENDING_SYNC":
            rec["external_sync_state"] = "pending"
            rec["lifecycle"] = LIFECYCLE_QUEUED
            rec["lease_owner"] = None
            rec["lease_until"] = None
            self.store.put(rec)
            self.store.append_event(rec["id"], "pending_external_sync", result)
            return {"status": "QUEUED", "reason": "agiflow_unavailable", "replay": REPLAY_QUEUED}
        if result.get("status") == "CONFLICT":
            rec["external_sync_state"] = "conflict"
            rec["reset_condition"] = "human_agiflow_conflict_resolved"
            return self._park(rec, "newer_human_edit")
        self.store.mutation_record(kind, key)
        self.store.mutation_record("agiflow_comment", rec["sync_marker"])
        rec["external_sync_state"] = "succeeded"
        rec["payload"] = {
            **(rec.get("payload") or {}),
            "agiflow_task_id": result.get("agiflow_task_id"),
            "agiflow_status": result.get("agiflow_status"),
            "comment_id": result.get("comment_id"),
        }
        return self._succeed(rec, "agiflow_projected")

    def acknowledge_reset(self, idempotency_key: str, *, condition: str) -> dict:
        rec = self.store.get(idempotency_key)
        if rec is None:
            raise AdaError("UNKNOWN_FAILED_RUN", idempotency_key)
        if rec["lifecycle"] != LIFECYCLE_PARKED:
            raise AdaError("NOT_PARKED", idempotency_key)
        if rec.get("reset_condition") != condition:
            raise AdaError("RESET_CONDITION_MISMATCH", condition)
        rec["lifecycle"] = LIFECYCLE_RETRYABLE
        rec["next_retry_at"] = self.now().isoformat()
        rec["lease_owner"] = None
        rec["lease_until"] = None
        stored = self.store.put(rec)
        self.store.append_event(stored["id"], "unparked", {"condition": condition})
        return {"status": "RETRYABLE", "idempotency_key": idempotency_key}

    def quarantine(self, idempotency_key: str, *, reason: str) -> dict:
        rec = self.store.get(idempotency_key)
        if rec is None:
            raise AdaError("UNKNOWN_FAILED_RUN", idempotency_key)
        rec["lifecycle"] = LIFECYCLE_QUARANTINED
        rec["next_retry_at"] = None
        rec["last_error"] = reason
        stored = self.store.put(rec)
        self.store.append_event(stored["id"], "quarantined", {"reason": reason})
        return {"status": "QUARANTINED", "idempotency_key": idempotency_key}

    # -- internals ----------------------------------------------------------

    def _handle_engine_outcome(
        self, rec: dict, outcome: dict, *, kind: str, key: str,
    ) -> dict:
        status = (outcome or {}).get("status")
        if status in ENGINE_SUCCESS:
            if kind in PRODUCTION_MUTATION_KINDS:
                self.store.mutation_record(kind, key)
            skipped = status == "DUPLICATE_SKIPPED"
            reason = "duplicate_mutation_skipped" if skipped else "engine_applied"
            return self._succeed(rec, reason, skipped=skipped)
        if status in ENGINE_CONSUMES_ATTEMPT:
            return self._fail_attempt(rec, status)
        if status in ENGINE_RETRYABLE:
            return self._requeue(rec, status)
        return self._park(rec, f"UNKNOWN_ENGINE_STATUS:{status!s}")

    def _expire_lease(self, rec: dict, now: datetime) -> dict:
        if rec["lifecycle"] != LIFECYCLE_INFLIGHT:
            return rec
        until = rec.get("lease_until")
        if until and datetime.fromisoformat(until) > now:
            return rec
        stored = self.store.expire_lease_if_match(
            rec["id"],
            expected_lifecycle=LIFECYCLE_INFLIGHT,
            expected_owner=rec.get("lease_owner"),
            expected_until=rec.get("lease_until"),
            expected_generation=rec.get("claim_generation"),
            now=now,
        )
        if stored is None:
            return self.store.get_by_id(rec["id"]) or rec
        self.store.append_event(stored["id"], "lease_expired", {})
        return stored

    def _succeed(self, rec: dict, reason: str, *, skipped: bool = False) -> dict:
        rec["lifecycle"] = LIFECYCLE_SUCCEEDED
        rec["lease_owner"] = None
        rec["lease_until"] = None
        rec["next_retry_at"] = None
        if rec.get("external_sync_state") == "pending":
            rec["external_sync_state"] = "succeeded"
        stored = self.store.put(rec)
        self.store.append_event(stored["id"], "succeeded", {"reason": reason})
        return {
            "status": "DUPLICATE_SKIPPED" if skipped else "SUCCEEDED",
            "reason": reason,
            "idempotency_key": stored["idempotency_key"],
        }

    def _park(self, rec: dict, reason: str) -> dict:
        rec["lifecycle"] = LIFECYCLE_PARKED
        rec["next_retry_at"] = None
        rec["lease_owner"] = None
        rec["lease_until"] = None
        rec["last_error"] = reason
        stored = self.store.put(rec)
        self.store.append_event(stored["id"], "parked", {"reason": reason})
        return {"status": "PARKED", "reason": reason, "replay": REPLAY_PARKED}

    def _requeue(self, rec: dict, reason: str) -> dict:
        rec["lease_owner"] = None
        rec["lease_until"] = None
        rec["last_error"] = reason
        if int(rec.get("attempt_count") or 0) >= int(rec.get("max_attempts") or self.max_attempts):
            rec["lifecycle"] = LIFECYCLE_DEAD_LETTER
            rec["next_retry_at"] = None
            stored = self.store.put(rec)
            self.store.append_event(stored["id"], "dead_letter", {"reason": reason})
            return {"status": "DEAD_LETTER", "reason": reason}
        rec["lifecycle"] = LIFECYCLE_RETRYABLE if reason != "REQUIRES_ENGINE" else LIFECYCLE_QUEUED
        rec["next_retry_at"] = self.now().isoformat()
        stored = self.store.put(rec)
        self.store.append_event(stored["id"], "requeued", {"reason": reason})
        if reason == "UNAVAILABLE":
            status = "UNAVAILABLE"
        elif reason == "REQUIRES_ENGINE":
            status = "REQUIRES_ENGINE"
        else:
            status = "REQUEUED"
        return {"status": status, "reason": reason, "replay": REPLAY_RETRYABLE}

    def _fail_attempt(self, rec: dict, reason: str) -> dict:
        rec["attempt_count"] = int(rec.get("attempt_count") or 0) + 1
        return self._requeue(rec, reason)

    def clickup_was_used(self) -> bool:
        return False

    def must_not_write_runtime(self, method: str) -> None:
        self._write_attempts.append(method)
        raise AdaError(
            "OUTBOX_MUST_NOT_WRITE_RUNTIME",
            f"failed-run outbox cannot call runtime.{method}",
        )

    def __getattr__(self, name: str):
        if name in RUNTIME_WRITE_METHODS:
            def _blocked(*_a, **_k):
                self.must_not_write_runtime(name)
            return _blocked
        raise AttributeError(name)
