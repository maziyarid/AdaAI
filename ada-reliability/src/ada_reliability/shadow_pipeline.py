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


class ShadowPipeline:
    """bootstrap → inspect → propose → validate → authorize → record → STOP."""

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
    ) -> dict[str, Any]:
        if (
            live_schedule_stable_id is not None
            and live_schedule_stable_id not in KNOWN_SCHEDULE_IDS
        ):
            # Do not invent a schedule. Do not call the engine. Record DENY.
            return self._seal(
                {
                    "pipeline": "AAX-8",
                    "mode": "SHADOW",
                    "mutated": False,
                    "production_sql": False,
                    "production_mutation": False,
                    "live_schedule_stable_id": live_schedule_stable_id,
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
                "live_schedule_stable_id": live_schedule_stable_id,
                "production_sql": False,
                "production_mutation": False,
            }
        )
