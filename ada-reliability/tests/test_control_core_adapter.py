from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "runtime" / "control-core-baseline"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from adapter import PRESERVED_BEHAVIOR, ControlCoreAdapter, ControlCoreConfig


class _FakeResp:
    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_preserved_behavior_map_is_complete():
    required = {
        "durable_jobs", "schedules", "leases", "retries", "dead_letter_queue",
        "audit_log", "content_gates", "snapshots", "idempotent_enqueue",
        "database", "listen", "service",
        "health_unauthenticated_status", "health_endpoint_public",
    }
    assert required <= set(PRESERVED_BEHAVIOR)
    assert PRESERVED_BEHAVIOR["database"].startswith("MariaDB")
    assert "8770" in PRESERVED_BEHAVIOR["listen"]
    assert PRESERVED_BEHAVIOR["service"] == "maziyar-control-core.service"
    assert PRESERVED_BEHAVIOR["health_unauthenticated_status"] == 401
    assert PRESERVED_BEHAVIOR["health_endpoint_public"] is False
    assert PRESERVED_BEHAVIOR["source_bytes"] == 65370
    assert PRESERVED_BEHAVIOR["source_sha256_captured_bytes"] == (
        "aec6639acf761dfb01a72feb670b4d841c25fb1e8000abdea41bca0dcf4a94f3"
    )


def test_adapter_does_not_bind_a_second_scheduler():
    a = ControlCoreAdapter(ControlCoreConfig(base_url="http://127.0.0.1:8770"))
    assert a.config.base_url.endswith(":8770")
    # Adapter is a client. It must not start its own queue loop.
    assert not hasattr(a, "run_forever")
    assert not hasattr(a, "enqueue_local")


def test_unauthenticated_health_treats_401_as_protected_healthy():
    """Live BLACKOUT_SENTINEL HEALTH_TARGETS expects 401. Do not make /health public."""
    err = HTTPError(
        "http://127.0.0.1:8770/health",
        401,
        "unauthorized",
        hdrs=None,
        fp=BytesIO(b'{"error":"unauthorized"}'),
    )
    a = ControlCoreAdapter()
    with patch("adapter.urlopen", side_effect=err):
        got = a.health()
    assert got["ok"] is True
    assert got["http_status"] == 401
    assert got["contract"] == "protected-health"
    assert got["authenticated"] is False


def test_authenticated_health_sends_bearer_token():
    a = ControlCoreAdapter(ControlCoreConfig(api_token="test-token"))
    resp = _FakeResp(200, b'{"status":"ok","backend":"mariadb"}')
    with patch("adapter.urlopen", return_value=resp) as mocked:
        got = a.health()
    req = mocked.call_args[0][0]
    assert req.get_header("Authorization") == "Bearer test-token"
    assert got["ok"] is True
    assert got["http_status"] == 200
    assert got["contract"] == "authenticated-health"
    assert got["authenticated"] is True
    assert got["body"]["status"] == "ok"


def test_unauthenticated_200_fails_closed_health_must_stay_protected():
    a = ControlCoreAdapter()
    resp = _FakeResp(200, b'{"status":"ok"}')
    with patch("adapter.urlopen", return_value=resp):
        try:
            a.health()
        except RuntimeError as exc:
            assert "HEALTH_ENDPOINT_PUBLIC" in str(exc)
        else:
            raise AssertionError("unauthenticated 200 must fail closed")
