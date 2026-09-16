"""Client adapter for the live maziyar-control-core.

This is NOT a second scheduler. Jobs, schedules, leases, retries and DLQ
remain in maziyar-control-core (127.0.0.1:8770). Ada reliability attaches
receipts, authorization, approvals and journals to those jobs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from urllib.request import Request, urlopen
import json


@dataclass
class ControlCoreConfig:
    base_url: str = "http://127.0.0.1:8770"
    timeout_seconds: float = 5.0


class ControlCoreAdapter:
    def __init__(self, config: Optional[ControlCoreConfig] = None):
        self.config = config or ControlCoreConfig()

    def _get(self, path: str) -> dict[str, Any]:
        req = Request(self.config.base_url + path, method="GET")
        with urlopen(req, timeout=self.config.timeout_seconds) as resp:
            return json.loads(resp.read().decode())

    def health(self) -> dict[str, Any]:
        return self._get("/health")

    def get_job(self, job_id: str) -> dict[str, Any]:
        return self._get(f"/jobs/{job_id}")


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
}
