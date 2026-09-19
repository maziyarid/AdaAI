"""Client adapter for the live maziyar-control-core.

This is NOT a second scheduler. Jobs, schedules, leases, retries and DLQ
remain in maziyar-control-core (127.0.0.1:8770). Ada reliability attaches
receipts, authorization, approvals and journals to those jobs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import json


@dataclass
class ControlCoreConfig:
    base_url: str = "http://127.0.0.1:8770"
    timeout_seconds: float = 5.0
    # Optional CONTROL_API_TOKEN. Never commit values. Unauthenticated
    # GET /health is expected to 401; that is the live healthy signal.
    api_token: Optional[str] = None


class ControlCoreAdapter:
    def __init__(self, config: Optional[ControlCoreConfig] = None):
        self.config = config or ControlCoreConfig()

    def _get(self, path: str, token: Optional[str] = None) -> dict[str, Any]:
        req = Request(self.config.base_url + path, method="GET")
        if token:
            req.add_header("Authorization", "Bearer " + token)
        with urlopen(req, timeout=self.config.timeout_seconds) as resp:
            return json.loads(resp.read().decode())

    def health(self) -> dict[str, Any]:
        """Probe live `/health` without making the endpoint public.

        Live `HEALTH_TARGETS` treats unauthenticated HTTP 401 as healthy
        for `http://127.0.0.1:8770/health` (BLACKOUT_SENTINEL). The 200
        JSON branch exists only after `auth()` with `CONTROL_API_TOKEN`.
        Do not strip that token. Do not add a public `/health`.
        """
        token = self.config.api_token
        url = self.config.base_url + "/health"
        req = Request(url, method="GET")
        if token:
            req.add_header("Authorization", "Bearer " + token)
        try:
            with urlopen(req, timeout=self.config.timeout_seconds) as resp:
                payload = json.loads(resp.read().decode())
                status = getattr(resp, "status", 200)
        except HTTPError as exc:
            if exc.code == 401 and not token:
                return {
                    "ok": True,
                    "http_status": 401,
                    "contract": "protected-health",
                    "authenticated": False,
                }
            raise
        if not token:
            raise RuntimeError(
                "HEALTH_ENDPOINT_PUBLIC: unauthenticated /health returned "
                f"{status}; live contract expects 401. Do not make /health public."
            )
        return {
            "ok": True,
            "http_status": status,
            "contract": "authenticated-health",
            "authenticated": True,
            "body": payload,
        }

    def get_job(self, job_id: str) -> dict[str, Any]:
        return self._get(f"/jobs/{job_id}", token=self.config.api_token)


# Documented live behavior we must preserve. Tests assert this map exists so
# a later import of /opt/maziyar-control-core cannot silently drop it.
PRESERVED_BEHAVIOR = {
    "durable_jobs": True,
    "schedules": True,
    "leases": True,
    "retries": True,
    "dead_letter_queue": True,
    "audit_log": True,
    "content_gates": True,
    "snapshots": True,
    "external_sync_state": True,
    "idempotent_enqueue": True,
    "database": "MariaDB 10.11",
    "listen": "127.0.0.1:8770",
    "service": "maziyar-control-core.service",
    "implementation": "/opt/maziyar-control-core",
    "mistral_worker": "127.0.0.1:9102",
    "health_unauthenticated_status": 401,
    "health_endpoint_public": False,
    "source_snapshot": "runtime/control-core-baseline/live/control_core.py",
    "source_bytes": 65370,
    "source_sha256_captured_bytes": "aec6639acf761dfb01a72feb670b4d841c25fb1e8000abdea41bca0dcf4a94f3",
}
