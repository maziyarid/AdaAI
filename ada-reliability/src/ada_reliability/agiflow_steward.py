"""Agiflow coordination projection (AAX-12 / ADR-0003).

MariaDB control-core remains runtime truth for jobs, schedules, leases,
heartbeats and retries. This steward projects meaningful coordination state
onto Agiflow. It must never:

- enqueue, schedule, lease or otherwise mutate runtime jobs;
- treat Agiflow remote execution as the scheduler;
- require ClickUp for new execution or completion;
- overwrite a newer human Agiflow edit;
- project Done/Review from a model assertion or caller-constructed evidence.

HMAC receipts and WordPress mutation stay in AdaEngine. This module is a
side-channel projection with a durable outbox so an Agiflow outage does not
stop authorised runtime work.
"""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Optional

from .crypto import hmac_sign, hmac_verify, sha256_obj, utcnow
from .engine import AdaError


# Agiflow board statuses used by the Other Projects project.
AGIFLOW_TODO = "Todo"
AGIFLOW_IN_PROGRESS = "In Progress"
AGIFLOW_REVIEW = "Review"
AGIFLOW_DONE = "Done"
AGIFLOW_BLOCKED = "Blocked"
AGIFLOW_CANCELLED = "Cancelled"

HUMAN_PROTECTED_STATUSES = {AGIFLOW_DONE, AGIFLOW_CANCELLED}

RUNTIME_TO_AGIFLOW = {
    "queued": AGIFLOW_TODO,
    "pending": AGIFLOW_TODO,
    "leased": AGIFLOW_IN_PROGRESS,
    "running": AGIFLOW_IN_PROGRESS,
    "executing": AGIFLOW_IN_PROGRESS,
    "succeeded": AGIFLOW_REVIEW,  # only if issued evidence is verified
    "failed": AGIFLOW_BLOCKED,
    "dead_letter": AGIFLOW_BLOCKED,
    "parked": AGIFLOW_BLOCKED,
    "blocked": AGIFLOW_BLOCKED,
}

RUNTIME_WRITE_METHODS = (
    "enqueue",
    "create_job",
    "schedule",
    "create_schedule",
    "acquire_lease",
    "release_lease",
    "retry_job",
    "cancel_job",
)

AGIFLOW_EXECUTE_METHODS = ("execute", "run_task", "dispatch")
TRUSTED_SOURCES = frozenset({"runtime", "live"})
DEFAULT_TRUSTED_VERIFIERS = frozenset({"verifier", "ada_service"})
DEFAULT_TRUSTED_CLOSERS = frozenset({"human_approver"})


def _now(clock: Optional[Callable[[], datetime]]) -> datetime:
    return clock() if clock else utcnow()


# ---------------------------------------------------------------------------
# Read-only runtime view — steward must not own jobs/schedules/leases
# ---------------------------------------------------------------------------

class ReadOnlyRuntime:
    """In-memory stand-in for a MariaDB control-core read. Writes fail closed."""

    def __init__(self, jobs: Optional[dict[str, dict]] = None):
        self.jobs: dict[str, dict] = jobs or {}
        self.write_attempts: list[str] = []

    def get_job(self, job_id: str) -> Optional[dict]:
        job = self.jobs.get(job_id)
        return copy.deepcopy(job) if job else None

    def __getattr__(self, name: str):
        if name in RUNTIME_WRITE_METHODS:
            def _blocked(*_a, **_k):
                self.write_attempts.append(name)
                raise AdaError(
                    "STEWARD_MUST_NOT_WRITE_RUNTIME",
                    f"Agiflow steward cannot call runtime.{name}",
                )
            return _blocked
        raise AttributeError(name)


# ---------------------------------------------------------------------------
# Fake Agiflow — tests and shadow mode. Live adapter replaces this later.
# ---------------------------------------------------------------------------

class FakeAgiflow:
    """Deterministic Agiflow double. Remote execution is recorded and denied."""

    def __init__(self):
        self.unavailable = False
        self.tasks: dict[str, dict] = {}
        self.comments: list[dict] = []
        self.comment_keys: set[str] = set()
        self.execute_calls: list[str] = []
        self.status_writes: list[tuple[str, str]] = []
        self._seq = 0

    def _require_up(self) -> None:
        if self.unavailable:
            raise AdaError("AGIFLOW_UNAVAILABLE", "agiflow projection target is down")

    def create_task(self, *, project_id: str, title: str, status: str) -> dict:
        self._require_up()
        self._seq += 1
        task_id = f"agiflow-{self._seq:04d}"
        task = {
            "id": task_id,
            "project_id": project_id,
            "title": title,
            "status": status,
            "version": 1,
            "updated_by": "steward",
            "updated_at": utcnow().isoformat(),
            "human_edited": False,
        }
        self.tasks[task_id] = task
        return copy.deepcopy(task)

    def get_task(self, task_id: str) -> Optional[dict]:
        self._require_up()
        t = self.tasks.get(task_id)
        return copy.deepcopy(t) if t else None

    def update_status(self, task_id: str, status: str, *, actor: str = "steward") -> dict:
        self._require_up()
        t = self.tasks.get(task_id)
        if t is None:
            raise AdaError("UNKNOWN_AGIFLOW_TASK", task_id)
        t["status"] = status
        t["version"] = int(t.get("version") or 0) + 1
        t["updated_by"] = actor
        t["updated_at"] = utcnow().isoformat()
        if actor == "human":
            t["human_edited"] = True
        self.status_writes.append((task_id, status))
        return copy.deepcopy(t)

    def add_comment(self, task_id: str, body: str, *, idempotency_key: str, actor: str = "steward") -> dict:
        self._require_up()
        if task_id not in self.tasks:
            raise AdaError("UNKNOWN_AGIFLOW_TASK", task_id)
        if idempotency_key in self.comment_keys:
            existing = next(c for c in self.comments if c["idempotency_key"] == idempotency_key)
            return copy.deepcopy(existing)
        comment = {
            "id": str(uuid.uuid4()),
            "task_id": task_id,
            "body": body,
            "idempotency_key": idempotency_key,
            "actor": actor,
            "created_at": utcnow().isoformat(),
        }
        self.comment_keys.add(idempotency_key)
        self.comments.append(comment)
        return copy.deepcopy(comment)

    def simulate_human_edit(self, task_id: str, *, status: Optional[str] = None, title: Optional[str] = None) -> dict:
        """Test helper: a human edits the board without going through the steward."""
        t = self.tasks.get(task_id)
        if t is None:
            raise AdaError("UNKNOWN_AGIFLOW_TASK", task_id)
        if status is not None:
            t["status"] = status
        if title is not None:
            t["title"] = title
        t["version"] = int(t.get("version") or 0) + 1
        t["updated_by"] = "human"
        t["human_edited"] = True
        t["updated_at"] = utcnow().isoformat()
        return copy.deepcopy(t)

    def __getattr__(self, name: str):
        if name in AGIFLOW_EXECUTE_METHODS:
            def _blocked(*_a, **_k):
                self.execute_calls.append(name)
                raise AdaError(
                    "STEWARD_MUST_NOT_EXECUTE_AGIFLOW",
                    f"Agiflow remote execution is not the runtime scheduler ({name})",
                )
            return _blocked
        raise AttributeError(name)


# ---------------------------------------------------------------------------
# Issued evidence — callers cannot construct a Review/Done proof
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IssuedEvidence:
    """Handle returned by issue_evidence. Fields are informational; projection
    looks up the HMAC-signed record by id and rejects anything not in store."""
    id: str
    durable_job_id: str
    live_hash: str
    verifier_identity: str
    source: str
    signature: str


@dataclass(frozen=True)
class CloseGrant:
    id: str
    durable_job_id: str
    evidence_id: str
    closer_identity: str
    signature: str


# ---------------------------------------------------------------------------
# Steward
# ---------------------------------------------------------------------------

@dataclass
class Mapping:
    durable_job_id: str
    agiflow_task_id: str
    project_id: str
    last_projected_status: Optional[str] = None
    last_projected_version: int = 0
    previous_projected_status: Optional[str] = None


class AgiflowStateSteward:
    """One-way, fail-closed projection from durable runtime jobs to Agiflow."""

    def __init__(
        self,
        *,
        agiflow: FakeAgiflow,
        runtime: ReadOnlyRuntime,
        project_id: str,
        hmac_key: str,
        clock: Optional[Callable[[], datetime]] = None,
        clickup: Any = None,
        trusted_verifiers: Optional[frozenset[str]] = None,
        trusted_closers: Optional[frozenset[str]] = None,
    ):
        if len(hmac_key) < 32:
            raise RuntimeError("HMAC key too short")
        self.agiflow = agiflow
        self.runtime = runtime
        self.project_id = project_id
        self.hmac_key = hmac_key
        self._clock = clock
        self.trusted_verifiers = trusted_verifiers or DEFAULT_TRUSTED_VERIFIERS
        self.trusted_closers = trusted_closers or DEFAULT_TRUSTED_CLOSERS
        # ClickUp is legacy. The constructor accepts a spy so tests can prove
        # it is never invoked; the steward stores nothing usable.
        self._clickup_ignored = clickup is not None
        self._clickup_calls = 0
        self.mappings: dict[str, Mapping] = {}
        self.outbox: dict[str, dict] = {}
        self.audit: list[dict] = []
        self.issued_evidence: dict[str, dict] = {}
        self.close_grants: dict[str, dict] = {}

    def now(self) -> datetime:
        return _now(self._clock)

    # -- issued evidence / close grants ------------------------------------

    def issue_evidence(
        self,
        *,
        durable_job_id: str,
        live_hash: str,
        verifier_identity: str,
        source: str = "runtime",
    ) -> IssuedEvidence:
        if self.runtime.get_job(durable_job_id) is None:
            raise AdaError("UNKNOWN_RUNTIME_JOB", durable_job_id)
        if verifier_identity not in self.trusted_verifiers:
            raise AdaError("UNTRUSTED_VERIFIER", verifier_identity)
        if source not in TRUSTED_SOURCES:
            raise AdaError("UNTRUSTED_EVIDENCE_SOURCE", source)
        if not live_hash:
            raise AdaError("MISSING_LIVE_HASH", durable_job_id)
        payload = {
            "durable_job_id": durable_job_id,
            "live_hash": live_hash,
            "verifier_identity": verifier_identity,
            "source": source,
        }
        rec_id = str(uuid.uuid4())
        signature = hmac_sign(payload, self.hmac_key)
        stored = {
            **payload,
            "id": rec_id,
            "signature": signature,
            "issued_at": self.now().isoformat(),
        }
        self.issued_evidence[rec_id] = stored
        self._audit("evidence_issued", durable_job_id, {"evidence_id": rec_id})
        return IssuedEvidence(
            id=rec_id,
            durable_job_id=durable_job_id,
            live_hash=live_hash,
            verifier_identity=verifier_identity,
            source=source,
            signature=signature,
        )

    def issue_close_grant(
        self,
        *,
        durable_job_id: str,
        evidence_id: str,
        closer_identity: str,
    ) -> CloseGrant:
        if closer_identity not in self.trusted_closers:
            raise AdaError("UNTRUSTED_CLOSER", closer_identity)
        evidence = self._require_issued_evidence(evidence_id, durable_job_id)
        payload = {
            "durable_job_id": durable_job_id,
            "evidence_id": evidence.id,
            "closer_identity": closer_identity,
        }
        rec_id = str(uuid.uuid4())
        signature = hmac_sign(payload, self.hmac_key)
        stored = {
            **payload,
            "id": rec_id,
            "signature": signature,
            "consumed": False,
            "issued_at": self.now().isoformat(),
        }
        self.close_grants[rec_id] = stored
        self._audit("close_grant_issued", durable_job_id, {"grant_id": rec_id})
        return CloseGrant(
            id=rec_id,
            durable_job_id=durable_job_id,
            evidence_id=evidence.id,
            closer_identity=closer_identity,
            signature=signature,
        )

    def _require_issued_evidence(self, evidence_id: str, durable_job_id: str) -> IssuedEvidence:
        stored = self.issued_evidence.get(evidence_id)
        if stored is None:
            raise AdaError("UNKNOWN_EVIDENCE", evidence_id)
        payload = {
            "durable_job_id": stored["durable_job_id"],
            "live_hash": stored["live_hash"],
            "verifier_identity": stored["verifier_identity"],
            "source": stored["source"],
        }
        if not hmac_verify(payload, stored["signature"], self.hmac_key):
            raise AdaError("FORGED_EVIDENCE", evidence_id)
        if stored["durable_job_id"] != durable_job_id:
            raise AdaError("EVIDENCE_JOB_MISMATCH", evidence_id)
        if stored["verifier_identity"] not in self.trusted_verifiers:
            raise AdaError("UNTRUSTED_VERIFIER", stored["verifier_identity"])
        if stored["source"] not in TRUSTED_SOURCES:
            raise AdaError("UNTRUSTED_EVIDENCE_SOURCE", stored["source"])
        return IssuedEvidence(
            id=stored["id"],
            durable_job_id=stored["durable_job_id"],
            live_hash=stored["live_hash"],
            verifier_identity=stored["verifier_identity"],
            source=stored["source"],
            signature=stored["signature"],
        )

    def _require_close_grant(
        self, grant_id: str, durable_job_id: str, evidence: IssuedEvidence,
    ) -> CloseGrant:
        stored = self.close_grants.get(grant_id)
        if stored is None:
            raise AdaError("UNKNOWN_CLOSE_GRANT", grant_id)
        payload = {
            "durable_job_id": stored["durable_job_id"],
            "evidence_id": stored["evidence_id"],
            "closer_identity": stored["closer_identity"],
        }
        if not hmac_verify(payload, stored["signature"], self.hmac_key):
            raise AdaError("FORGED_CLOSE_GRANT", grant_id)
        if stored["consumed"]:
            raise AdaError("CLOSE_GRANT_CONSUMED", grant_id)
        if stored["durable_job_id"] != durable_job_id:
            raise AdaError("CLOSE_GRANT_JOB_MISMATCH", grant_id)
        if stored["evidence_id"] != evidence.id:
            raise AdaError("CLOSE_GRANT_EVIDENCE_MISMATCH", grant_id)
        if stored["closer_identity"] not in self.trusted_closers:
            raise AdaError("UNTRUSTED_CLOSER", stored["closer_identity"])
        return CloseGrant(
            id=stored["id"],
            durable_job_id=stored["durable_job_id"],
            evidence_id=stored["evidence_id"],
            closer_identity=stored["closer_identity"],
            signature=stored["signature"],
        )

    def _consume_close_grant(self, grant_id: str) -> None:
        rec = self.close_grants.get(grant_id)
        if rec is not None:
            rec["consumed"] = True

    # -- mapping ------------------------------------------------------------

    def mapping_for(self, durable_job_id: str) -> Optional[Mapping]:
        return self.mappings.get(durable_job_id)

    def ensure_mapping(self, durable_job_id: str, title: str) -> dict:
        existing = self.mappings.get(durable_job_id)
        if existing is not None:
            return {"status": "existing", "mapping": existing, "created": False}
        job = self.runtime.get_job(durable_job_id)
        desired = AGIFLOW_TODO if job is None else self._desired_status(job, evidence=None, grant=None)
        try:
            task = self.agiflow.create_task(
                project_id=self.project_id, title=title, status=desired,
            )
        except AdaError as err:
            if err.code == "AGIFLOW_UNAVAILABLE":
                rec = self._enqueue_outbox(
                    kind="create_task",
                    durable_job_id=durable_job_id,
                    payload={"title": title, "status": desired, "project_id": self.project_id},
                )
                return {"status": "PENDING_SYNC", "outbox_id": rec["id"], "created": False}
            raise
        mapping = Mapping(
            durable_job_id=durable_job_id,
            agiflow_task_id=task["id"],
            project_id=self.project_id,
            last_projected_status=task["status"],
            last_projected_version=int(task["version"]),
        )
        self.mappings[durable_job_id] = mapping
        self._audit("mapped", durable_job_id, {"agiflow_task_id": task["id"]})
        return {"status": "created", "mapping": mapping, "created": True}

    # -- projection ---------------------------------------------------------

    def project(
        self,
        durable_job_id: str,
        *,
        evidence_id: Optional[str] = None,
        close_grant_id: Optional[str] = None,
    ) -> dict:
        job = self.runtime.get_job(durable_job_id)
        if job is None:
            raise AdaError("UNKNOWN_RUNTIME_JOB", durable_job_id)
        evidence = (
            self._require_issued_evidence(evidence_id, durable_job_id)
            if evidence_id else None
        )
        if close_grant_id and evidence is None:
            raise AdaError("CLOSE_GRANT_REQUIRES_EVIDENCE", close_grant_id)
        grant = (
            self._require_close_grant(close_grant_id, durable_job_id, evidence)
            if close_grant_id else None
        )
        title = job.get("title") or durable_job_id
        ensured = self.ensure_mapping(durable_job_id, title)
        if ensured.get("status") == "PENDING_SYNC":
            self._enqueue_outbox(
                kind="project",
                durable_job_id=durable_job_id,
                payload={"evidence_id": evidence_id, "close_grant_id": close_grant_id},
            )
            return {"status": "PENDING_SYNC", "reason": "agiflow_unavailable"}

        mapping = self.mappings[durable_job_id]
        return self._project_mapped(mapping, job, evidence, grant)

    def _project_mapped(
        self,
        mapping: Mapping,
        job: dict,
        evidence: Optional[IssuedEvidence],
        grant: Optional[CloseGrant],
    ) -> dict:
        desired = self._desired_status(job, evidence, grant)
        comment_kind, comment_body = self._comment_for(job, evidence, desired)
        idem_key = self._comment_key(mapping.durable_job_id, comment_kind, evidence)

        try:
            remote = self.agiflow.get_task(mapping.agiflow_task_id)
        except AdaError as err:
            if err.code == "AGIFLOW_UNAVAILABLE":
                self._enqueue_outbox(
                    kind="project",
                    durable_job_id=mapping.durable_job_id,
                    payload={
                        "evidence_id": evidence.id if evidence else None,
                        "close_grant_id": grant.id if grant else None,
                    },
                )
                return {"status": "PENDING_SYNC", "reason": "agiflow_unavailable"}
            raise

        conflict = self._human_conflict(mapping, remote)
        if conflict:
            self._audit("conflict", mapping.durable_job_id, {
                "remote_status": remote["status"],
                "remote_version": remote["version"],
                "desired": desired,
            })
            return {
                "status": "CONFLICT",
                "reason": "newer_human_edit",
                "remote_status": remote["status"],
                "desired_status": desired,
                "agiflow_task_id": mapping.agiflow_task_id,
            }

        actions: list[str] = []
        if remote["status"] != desired:
            updated = self.agiflow.update_status(
                mapping.agiflow_task_id, desired, actor="steward",
            )
            mapping.previous_projected_status = mapping.last_projected_status
            mapping.last_projected_status = desired
            mapping.last_projected_version = int(updated["version"])
            actions.append(f"status:{desired}")
        else:
            mapping.last_projected_version = max(
                mapping.last_projected_version, int(remote.get("version") or 0),
            )

        comment = self.agiflow.add_comment(
            mapping.agiflow_task_id, comment_body, idempotency_key=idem_key,
        )
        actions.append("comment")
        if desired == AGIFLOW_DONE and grant is not None:
            self._consume_close_grant(grant.id)
        self._audit("projected", mapping.durable_job_id, {
            "desired": desired,
            "actions": actions,
            "comment_id": comment["id"],
        })
        return {
            "status": "PROJECTED",
            "agiflow_task_id": mapping.agiflow_task_id,
            "agiflow_status": desired,
            "actions": actions,
            "comment_id": comment["id"],
        }

    def _desired_status(
        self,
        job: dict,
        evidence: Optional[IssuedEvidence],
        grant: Optional[CloseGrant],
    ) -> str:
        runtime_state = str(job.get("state") or "queued").lower()
        if runtime_state in ("succeeded", "success", "completed"):
            if evidence is None:
                return AGIFLOW_IN_PROGRESS
            if grant is not None:
                return AGIFLOW_DONE
            return AGIFLOW_REVIEW
        return RUNTIME_TO_AGIFLOW.get(runtime_state, AGIFLOW_TODO)

    def _comment_for(
        self,
        job: dict,
        evidence: Optional[IssuedEvidence],
        desired: str,
    ) -> tuple[str, str]:
        state = str(job.get("state") or "queued")
        job_id = job.get("id") or ""
        if desired == AGIFLOW_REVIEW:
            kind = "verified_review"
            body = (
                f"Runtime job {job_id} succeeded with independent verification "
                f"live_hash={evidence.live_hash if evidence else ''} "
                f"verifier={evidence.verifier_identity if evidence else ''} "
                f"evidence_id={evidence.id if evidence else ''}."
            )
        elif desired == AGIFLOW_DONE:
            kind = "verified_done"
            body = f"Runtime job {job_id} closed with human-backed live evidence."
        elif desired == AGIFLOW_IN_PROGRESS and state.lower() in ("succeeded", "success", "completed"):
            kind = "awaiting_evidence"
            body = (
                f"Runtime job {job_id} reports {state} but Review/Done is withheld: "
                "no independent live evidence."
            )
        elif desired == AGIFLOW_IN_PROGRESS:
            kind = "checkpoint"
            body = f"Runtime job {job_id} is {state}."
        elif desired == AGIFLOW_BLOCKED:
            kind = "blocked"
            body = f"Runtime job {job_id} is {state}."
        else:
            kind = "queued"
            body = f"Runtime job {job_id} mapped; state={state}."
        return kind, body

    def _comment_key(
        self,
        durable_job_id: str,
        kind: str,
        evidence: Optional[IssuedEvidence],
    ) -> str:
        return sha256_obj({
            "job": durable_job_id,
            "kind": kind,
            "evidence_id": evidence.id if evidence else "",
            "live_hash": evidence.live_hash if evidence else "",
        })

    def _human_conflict(self, mapping: Mapping, remote: dict) -> bool:
        if remote.get("updated_by") != "human" and not remote.get("human_edited"):
            return False
        remote_version = int(remote.get("version") or 0)
        if remote_version <= mapping.last_projected_version:
            return False
        if remote.get("status") in HUMAN_PROTECTED_STATUSES:
            return True
        return True

    # -- outbox / replay ----------------------------------------------------

    def _enqueue_outbox(self, *, kind: str, durable_job_id: str, payload: dict) -> dict:
        key = sha256_obj({"kind": kind, "job": durable_job_id, "payload": payload})
        existing = self.outbox.get(key)
        if existing is not None:
            return existing
        rec = {
            "id": str(uuid.uuid4()),
            "idempotency_key": key,
            "kind": kind,
            "durable_job_id": durable_job_id,
            "payload": copy.deepcopy(payload),
            "status": "PENDING",
            "attempts": 0,
            "created_at": self.now().isoformat(),
            "last_error": None,
        }
        self.outbox[key] = rec
        self._audit("outbox_enqueued", durable_job_id, {"kind": kind, "id": rec["id"]})
        return rec

    def pending_outbox(self) -> list[dict]:
        return [copy.deepcopy(r) for r in self.outbox.values() if r["status"] == "PENDING"]

    def replay_outbox(self) -> dict:
        applied = 0
        skipped = 0
        conflicts = 0
        still_pending = 0
        for rec in list(self.outbox.values()):
            if rec["status"] in ("APPLIED", "CONFLICT"):
                skipped += 1
                continue
            rec["attempts"] += 1
            try:
                result = self._replay_one(rec)
            except AdaError as err:
                if err.code == "AGIFLOW_UNAVAILABLE":
                    rec["last_error"] = err.code
                    still_pending += 1
                    continue
                rec["status"] = "DEAD"
                rec["last_error"] = err.code
                continue
            if result.get("status") == "CONFLICT":
                rec["status"] = "CONFLICT"
                conflicts += 1
            elif result.get("status") in ("PROJECTED", "created", "existing", "PENDING_SYNC"):
                if result.get("status") == "PENDING_SYNC":
                    still_pending += 1
                else:
                    rec["status"] = "APPLIED"
                    applied += 1
            else:
                rec["status"] = "APPLIED"
                applied += 1
        return {
            "applied": applied,
            "skipped": skipped,
            "conflicts": conflicts,
            "still_pending": still_pending,
        }

    def _replay_one(self, rec: dict) -> dict:
        kind = rec["kind"]
        job_id = rec["durable_job_id"]
        payload = rec["payload"]
        if kind == "create_task":
            return self.ensure_mapping(job_id, payload.get("title") or job_id)
        if kind == "project":
            return self.project(
                job_id,
                evidence_id=payload.get("evidence_id"),
                close_grant_id=payload.get("close_grant_id"),
            )
        raise AdaError("UNKNOWN_OUTBOX_KIND", kind)

    # -- rollback of last steward status (not of runtime jobs) --------------

    def rollback_projection(self, durable_job_id: str) -> dict:
        mapping = self.mappings.get(durable_job_id)
        if mapping is None:
            raise AdaError("UNKNOWN_MAPPING", durable_job_id)
        if mapping.previous_projected_status is None:
            raise AdaError("NOTHING_TO_ROLLBACK", durable_job_id)
        remote = self.agiflow.get_task(mapping.agiflow_task_id)
        if remote is None:
            raise AdaError("UNKNOWN_AGIFLOW_TASK", mapping.agiflow_task_id)
        if self._human_conflict(mapping, remote):
            return {
                "status": "CONFLICT",
                "reason": "newer_human_edit",
                "agiflow_task_id": mapping.agiflow_task_id,
            }
        restored = mapping.previous_projected_status
        updated = self.agiflow.update_status(
            mapping.agiflow_task_id, restored, actor="steward",
        )
        mapping.last_projected_status, mapping.previous_projected_status = restored, mapping.last_projected_status
        mapping.last_projected_version = int(updated["version"])
        self._audit("rollback", durable_job_id, {"restored": restored})
        return {
            "status": "ROLLED_BACK",
            "agiflow_status": restored,
            "agiflow_task_id": mapping.agiflow_task_id,
        }

    # -- invariants ---------------------------------------------------------

    def clickup_was_used(self) -> bool:
        return self._clickup_calls > 0

    def _audit(self, event: str, durable_job_id: str, details: dict) -> None:
        self.audit.append({
            "event": event,
            "durable_job_id": durable_job_id,
            "details": details,
            "at": self.now().isoformat(),
        })
