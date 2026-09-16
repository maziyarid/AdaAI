from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "runtime" / "control-core-baseline"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from adapter import PRESERVED_BEHAVIOR, ControlCoreAdapter, ControlCoreConfig


def test_preserved_behavior_map_is_complete():
    required = {
        "durable_jobs", "schedules", "leases", "retries", "dead_letter_queue",
        "audit_log", "content_gates", "snapshots", "idempotent_enqueue",
        "database", "listen", "service",
    }
    assert required <= set(PRESERVED_BEHAVIOR)
    assert PRESERVED_BEHAVIOR["database"].startswith("MariaDB")
    assert "8770" in PRESERVED_BEHAVIOR["listen"]
    assert PRESERVED_BEHAVIOR["service"] == "maziyar-control-core.service"


def test_adapter_does_not_bind_a_second_scheduler():
    a = ControlCoreAdapter(ControlCoreConfig(base_url="http://127.0.0.1:8770"))
    assert a.config.base_url.endswith(":8770")
    # Adapter is a client. It must not start its own queue loop.
    assert not hasattr(a, "run_forever")
    assert not hasattr(a, "enqueue_local")
