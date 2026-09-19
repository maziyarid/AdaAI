"""AAX-8 non-mutating shadow pipeline.

Binds live control-core snapshot identities + Qalam to
AdaEngine.shadow_mistral. Never writes WordPress, never applies SQL,
never creates a second scheduler or lease authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

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

# Adapter may only read. A write method appearing here is a contract break.
FORBIDDEN_ADAPTER_ATTRS = (
    "create_schedule",
    "acquire_lease",
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


class ShadowPipeline:
    """bootstrap → inspect → propose → validate → authorize → record → STOP."""

    def __init__(self, engine: AdaEngine, adapter: Optional[Any] = None):
        self.engine = engine
        self.adapter = adapter
        self.evidence: list[dict[str, Any]] = []
        if adapter is not None:
            assert_adapter_is_read_only(adapter)

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
        record = {
            **trace,
            "pipeline": "AAX-8",
            "live_schedule_stable_id": live_schedule_stable_id,
            "production_sql": False,
            "production_mutation": False,
        }
        self.evidence.append(record)
        return record
