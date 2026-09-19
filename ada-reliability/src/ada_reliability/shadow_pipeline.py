"""AAX-8 non-mutating shadow pipeline.

Binds live control-core snapshot identities + Qalam to
AdaEngine.shadow_mistral. Never writes WordPress, never applies SQL,
never creates a second scheduler or lease authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from .crypto import hmac_sign, hmac_verify
from .engine import AdaEngine, AdaError

REPO_ROOT = Path(__file__).resolve().parents[3]
LIVE_SOURCE = (
    REPO_ROOT / "runtime" / "control-core-baseline" / "live" / "control_core.py"
)

# Copied from the live snapshot seed_schedules(). Tests fail if the snapshot
# drifts. This is identity metadata, not a second scheduler.
LIVE_SEEDED_SCHEDULES = (
    ("schedule:blackout-sentinel", "BLACKOUT_SENTINEL", "blackout_sentinel.run", 300),
    ("schedule:project-controller", "PROJECT_CONTROLLER", "project_controller.run", 600),
    ("schedule:clickup-state-steward", "CLICKUP_STATE_STEWARD", "clickup_state_steward.run", 600),
    ("schedule:seo-scout", "SEO_SCOUT", "seo_scout.run", 3600),
    ("schedule:temp-tool-harvester", "TEMP_TOOL_HARVESTER", "temp_tool_harvester.run", 900),
    ("schedule:oracle-daily", "ORACLE_FORECASTER", "oracle_forecaster.run", 86400),
)
KNOWN_SCHEDULE_IDS = frozenset(row[0] for row in LIVE_SEEDED_SCHEDULES)

# From live snapshot handle_job(). Identity metadata, not a job queue.
LIVE_JOB_TYPES = frozenset(
    {
        "test.echo",
        "agent.tick",
        "blackout_sentinel.run",
        "seo_scout.run",
        "project_controller.run",
        "clickup_state_steward.run",
        "oracle_forecaster.run",
        "temp_tool_harvester.run",
        "mistral.chat",
        "test.fail",
    }
)
LIVE_JOB_SHAPE_KEYS = ("id", "stable_id", "agent", "job_type", "status")

# Adapter may only read. A write/lease/SQL method appearing here is a contract break.
FORBIDDEN_ADAPTER_ATTRS = (
    "create_schedule",
    "acquire_lease",
    "claim_job",
    "release_due_schedules",
    "enqueue",
    "enqueue_local",
    "create_job",
    "run_forever",
    "apply_sql",
    "mysqldump",
    "wp_update",
    "wp_publish",
)


def assert_adapter_is_read_only(adapter: Any) -> None:
    for name in FORBIDDEN_ADAPTER_ATTRS:
        if hasattr(adapter, name):
            raise AdaError("SHADOW_ADAPTER_WRITES", name)


def unsigned_evidence(record: dict[str, Any]) -> dict[str, Any]:
    """HMAC body: every field except the signature itself.

    Evaluation verdict, proposal, postcondition, and Qalam release are
    integrity-relevant. A whitelist that omitted them let a retained
    sealed record be tampered and still verify. alg/key_id must be set
    on the record before signing so they are bound too.
    """
    return {k: v for k, v in record.items() if k != "evidence_hmac"}


def live_schedule_binding(stable_id: str) -> Optional[dict[str, Any]]:
    """Snapshot identity only. Not a live Mistral job and not a scheduler."""
    for sid, agent, job_type, interval in LIVE_SEEDED_SCHEDULES:
        if sid == stable_id:
            return {
                "stable_id": sid,
                "agent": agent,
                "job_type": job_type,
                "interval_seconds": interval,
                "source": "runtime/control-core-baseline/live/control_core.py",
                "live_mistral_job": False,
            }
    return None


def live_job_context(job: Any) -> Optional[dict[str, Any]]:
    """Secret-free job identity from a read. Never copies payload_json."""
    if not isinstance(job, dict):
        return None
    for key in LIVE_JOB_SHAPE_KEYS:
        if not job.get(key):
            return None
    job_type = str(job["job_type"])
    if job_type not in LIVE_JOB_TYPES:
        return None
    return {
        "id": str(job["id"]),
        "stable_id": str(job["stable_id"]),
        "agent": str(job["agent"]),
        "job_type": job_type,
        "status": str(job["status"]),
        "source": "adapter.get_job",
        "live_mistral_job": False,
        "mistral_participated": False,
        "payload_copied": False,
    }


class ShadowPipeline:
    """bootstrap → inspect → propose → validate → authorize → record → STOP.

    Independent postcondition/rollback proof is a separate HMAC-sealed
    stage. It never applies a mutation and never executes production
    rollback.
    """

    def __init__(self, engine: AdaEngine, adapter: Optional[Any] = None):
        self.engine = engine
        self.adapter = adapter
        self.evidence: list[dict[str, Any]] = []
        if adapter is not None:
            assert_adapter_is_read_only(adapter)

    def _seal(self, record: dict[str, Any]) -> dict[str, Any]:
        record["evidence_alg"] = "hmac-sha256"
        record["evidence_key_id"] = self.engine.key_id
        body = unsigned_evidence(record)
        record["evidence_hmac"] = hmac_sign(body, self.engine.hmac_key)
        self.evidence.append(record)
        return record

    def verify_evidence(self, record: dict[str, Any]) -> bool:
        sig = record.get("evidence_hmac")
        if not sig or not isinstance(sig, str):
            return False
        return hmac_verify(unsigned_evidence(record), sig, self.engine.hmac_key)

    def evaluate(
        self,
        *,
        agent_id: str,
        task_type: str,
        project_id: str,
        site_id: str,
        proposal: dict[str, Any],
        risk_class: str = "low",
        live_schedule_stable_id: Optional[str] = None,
        live_job_id: Optional[str] = None,
    ) -> dict[str, Any]:
        context = {
            "agent_id": agent_id,
            "task_type": task_type,
            "project_id": project_id,
            "site_id": site_id,
            "live_schedule_stable_id": live_schedule_stable_id,
            "live_schedule_binding": (
                live_schedule_binding(live_schedule_stable_id)
                if live_schedule_stable_id is not None
                else None
            ),
            "live_job_id": live_job_id,
            "live_job_context": None,
            "evidence_kind": "repository_shadow",
            "live_mistral_job": False,
            "mistral_participated": False,
        }
        if live_job_id is not None:
            if self.adapter is None or not hasattr(self.adapter, "get_job"):
                return self._seal(
                    {
                        "pipeline": "AAX-8",
                        "stage": "EVALUATE",
                        "mode": "SHADOW",
                        "mutated": False,
                        "production_sql": False,
                        "production_mutation": False,
                        **context,
                        "authorization": {
                            "decision": "DENY",
                            "reason": "missing_read_adapter",
                        },
                        "qalam_ok": False,
                        "zwnj_fail": False,
                        "adaeval": {
                            "validation_failures": ["missing_read_adapter"],
                            "target_correctness": False,
                        },
                    }
                )
            try:
                job = self.adapter.get_job(live_job_id)
            except Exception:
                return self._seal(
                    {
                        "pipeline": "AAX-8",
                        "stage": "EVALUATE",
                        "mode": "SHADOW",
                        "mutated": False,
                        "production_sql": False,
                        "production_mutation": False,
                        **context,
                        "authorization": {
                            "decision": "DENY",
                            "reason": "adapter_job_read_failed",
                        },
                        "qalam_ok": False,
                        "zwnj_fail": False,
                        "adaeval": {
                            "validation_failures": ["adapter_job_read_failed"],
                            "target_correctness": False,
                        },
                    }
                )
            bound = live_job_context(job)
            if bound is None:
                return self._seal(
                    {
                        "pipeline": "AAX-8",
                        "stage": "EVALUATE",
                        "mode": "SHADOW",
                        "mutated": False,
                        "production_sql": False,
                        "production_mutation": False,
                        **context,
                        "authorization": {
                            "decision": "DENY",
                            "reason": "invalid_live_job_shape",
                        },
                        "qalam_ok": False,
                        "zwnj_fail": False,
                        "adaeval": {
                            "validation_failures": ["invalid_live_job_shape"],
                            "target_correctness": False,
                        },
                    }
                )
            context["live_job_context"] = bound
            context["evidence_kind"] = "adapter_job_read"
        if (
            live_schedule_stable_id is not None
            and live_schedule_stable_id not in KNOWN_SCHEDULE_IDS
        ):
            # Do not invent a schedule. Do not call the engine. Record DENY.
            return self._seal(
                {
                    "pipeline": "AAX-8",
                    "stage": "EVALUATE",
                    "mode": "SHADOW",
                    "mutated": False,
                    "production_sql": False,
                    "production_mutation": False,
                    **context,
                    "authorization": {
                        "decision": "DENY",
                        "reason": "unknown_live_schedule",
                    },
                    "qalam_ok": False,
                    "zwnj_fail": False,
                    "adaeval": {
                        "validation_failures": ["unknown_live_schedule"],
                        "target_correctness": False,
                    },
                }
            )
        writes_before = int(getattr(self.engine.wp, "writes", 0) or 0)
        apply_calls_before = getattr(self.engine, "_apply_calls", 0)
        trace = self.engine.shadow_mistral(
            agent_id=agent_id,
            task_type=task_type,
            project_id=project_id,
            site_id=site_id,
            proposal=proposal,
            risk_class=risk_class,
        )
        if trace.get("mutated"):
            raise AdaError("SHADOW_MUTATED", "shadow_mistral must not mutate")
        if int(getattr(self.engine.wp, "writes", 0) or 0) != writes_before:
            raise AdaError("SHADOW_WP_WRITE", "WordPress write during shadow")
        if getattr(self.engine, "_apply_calls", 0) != apply_calls_before:
            raise AdaError("SHADOW_APPLY", "apply_authorized_mutation during shadow")
        return self._seal(
            {
                **trace,
                "pipeline": "AAX-8",
                "stage": "EVALUATE",
                **context,
                "production_sql": False,
                "production_mutation": False,
            }
        )

    def prove_postcondition(self, trace: dict[str, Any]) -> dict[str, Any]:
        """Independent validator on a sealed shadow evaluate record.

        HMAC first. Never applies the proposal. Never closes the task.
        Never executes production rollback. This is in-process evidence,
        not a live Mistral/Teznevise canary.
        """
        parent_hmac = trace.get("evidence_hmac")
        writes_before = int(getattr(self.engine.wp, "writes", 0) or 0)
        apply_calls_before = getattr(self.engine, "_apply_calls", 0)
        if not self.verify_evidence(trace):
            return self._seal(
                {
                    "pipeline": "AAX-8",
                    "stage": "POSTCONDITION",
                    "mode": "SHADOW",
                    "mutated": False,
                    "production_sql": False,
                    "production_mutation": False,
                    "parent_evidence_hmac": parent_hmac,
                    "postcondition_proven": False,
                    "task_completed": False,
                    "authorization": {
                        "decision": "DENY",
                        "reason": "unauthenticated_evidence",
                    },
                    "rollback": {
                        "required": False,
                        "executed": False,
                        "reason": "unauthenticated_evidence",
                    },
                    "adaeval": {
                        "validation_failures": ["unauthenticated_evidence"],
                        "target_correctness": False,
                    },
                }
            )
        if (
            trace.get("mutated")
            or trace.get("production_mutation")
            or trace.get("production_sql")
        ):
            raise AdaError("SHADOW_MUTATED", "sealed shadow trace claimed a mutation")

        expected = dict(trace.get("expected_postcondition") or {})
        proposal = trace.get("proposal") or {}
        payload = proposal.get("payload") or {}
        site_id = trace.get("site_id")
        resource_id = str(payload.get("resource_id") or "")
        observed = None
        failures: list[str] = []
        proven = False
        if not site_id or not resource_id or not expected:
            failures.append("missing_postcondition_target")
        else:
            observed = self.engine.verify_live(
                site_id=str(site_id),
                resource_id=resource_id,
                expected=expected,
                after_mutation_id=None,
            )
            proven = bool(observed.get("passed"))
            failures.extend(list(observed.get("failures") or []))

        task_id = trace.get("task_id")
        task_state = None
        if task_id and task_id in self.engine.tasks:
            task_state = self.engine.tasks[task_id].get("state")
            # Shadow must not promote to COMPLETED.
            if task_state == "COMPLETED":
                raise AdaError("SHADOW_COMPLETED", "shadow task closed as completed")

        if int(getattr(self.engine.wp, "writes", 0) or 0) != writes_before:
            raise AdaError("SHADOW_WP_WRITE", "WordPress write during postcondition")
        if getattr(self.engine, "_apply_calls", 0) != apply_calls_before:
            raise AdaError("SHADOW_APPLY", "apply_authorized_mutation during postcondition")

        return self._seal(
            {
                "pipeline": "AAX-8",
                "stage": "POSTCONDITION",
                "mode": "SHADOW",
                "mutated": False,
                "production_sql": False,
                "production_mutation": False,
                "parent_evidence_hmac": parent_hmac,
                "task_id": task_id,
                "task_state": task_state,
                "task_completed": False,
                "site_id": site_id,
                "live_schedule_stable_id": trace.get("live_schedule_stable_id"),
                "live_schedule_binding": trace.get("live_schedule_binding"),
                "live_job_context": trace.get("live_job_context"),
                "evidence_kind": trace.get("evidence_kind") or "repository_shadow",
                "live_mistral_job": False,
                "mistral_participated": False,
                "expected_postcondition": expected,
                "observed": observed,
                "postcondition_proven": proven,
                "authorization": {
                    "decision": "ALLOW" if not failures else "DENY",
                    "reason": (
                        "independent_postcondition"
                        if proven
                        else "postcondition_not_proven_shadow_never_applied"
                    ),
                },
                "rollback": {
                    "required": False,
                    "executed": False,
                    "reason": "shadow_never_applied",
                },
                "adaeval": {
                    "target_correctness": proven,
                    "validation_failures": failures,
                    "authorization": "VERIFIER",
                },
            }
        )

    def rollback(self, proof: dict[str, Any]) -> dict[str, Any]:
        """Record that production rollback is forbidden in shadow.

        Independent validators may *plan* rollback. Executing it would
        be a production mutation. HMAC first.
        """
        parent_hmac = proof.get("evidence_hmac")
        writes_before = int(getattr(self.engine.wp, "writes", 0) or 0)
        if not self.verify_evidence(proof):
            return self._seal(
                {
                    "pipeline": "AAX-8",
                    "stage": "ROLLBACK",
                    "mode": "SHADOW",
                    "mutated": False,
                    "production_sql": False,
                    "production_mutation": False,
                    "parent_evidence_hmac": parent_hmac,
                    "authorization": {
                        "decision": "DENY",
                        "reason": "unauthenticated_evidence",
                    },
                    "rollback": {
                        "required": False,
                        "executed": False,
                        "reason": "unauthenticated_evidence",
                    },
                }
            )
        if int(getattr(self.engine.wp, "writes", 0) or 0) != writes_before:
            raise AdaError("SHADOW_WP_WRITE", "WordPress write during rollback")
        return self._seal(
            {
                "pipeline": "AAX-8",
                "stage": "ROLLBACK",
                "mode": "SHADOW",
                "mutated": False,
                "production_sql": False,
                "production_mutation": False,
                "parent_evidence_hmac": parent_hmac,
                "task_id": proof.get("task_id"),
                "site_id": proof.get("site_id"),
                "live_job_context": proof.get("live_job_context"),
                "evidence_kind": proof.get("evidence_kind") or "repository_shadow",
                "live_mistral_job": False,
                "mistral_participated": False,
                "authorization": {
                    "decision": "DENY",
                    "reason": "shadow_forbids_production_rollback",
                },
                "rollback": {
                    "required": bool((proof.get("rollback") or {}).get("required")),
                    "executed": False,
                    "reason": "shadow_forbids_production_rollback",
                },
                "adaeval": {
                    "target_correctness": False,
                    "validation_failures": ["shadow_forbids_production_rollback"],
                },
            }
        )
