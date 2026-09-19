"""Regression contracts for live control-core jobs/schedules/leases.

These assert documented live behavior that an import of
/opt/maziyar-control-core must not drop. They do not call the VPS.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "runtime" / "control-core-baseline"))

from adapter import PRESERVED_BEHAVIOR, ControlCoreAdapter, ControlCoreConfig


def test_jobs_schedules_leases_are_live_authority():
    assert PRESERVED_BEHAVIOR["durable_jobs"] is True
    assert PRESERVED_BEHAVIOR["schedules"] is True
    assert PRESERVED_BEHAVIOR["leases"] is True
    assert PRESERVED_BEHAVIOR["retries"] is True
    assert PRESERVED_BEHAVIOR["dead_letter_queue"] is True
    assert PRESERVED_BEHAVIOR["idempotent_enqueue"] is True


def test_no_second_listen_port():
    assert PRESERVED_BEHAVIOR["listen"] == "127.0.0.1:8770"
    a = ControlCoreAdapter(ControlCoreConfig())
    assert a.config.base_url == "http://127.0.0.1:8770"


def test_implementation_path_is_control_core_not_prototype():
    assert PRESERVED_BEHAVIOR["implementation"] == "/opt/maziyar-control-core"
    assert PRESERVED_BEHAVIOR["service"] == "maziyar-control-core.service"
    assert "9102" in PRESERVED_BEHAVIOR["mistral_worker"]


def test_adapter_has_job_read_not_local_enqueue():
    a = ControlCoreAdapter()
    assert hasattr(a, "get_job")
    assert hasattr(a, "health")
    assert not hasattr(a, "create_schedule")
    assert not hasattr(a, "acquire_lease")
