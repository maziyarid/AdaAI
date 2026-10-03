#!/usr/bin/env python3
"""AAX-24: single-owner Agiflow external-sync replay consumer.

Control-core pending_external_sync remains the durable queue/lease/backoff
authority. This process owns only connector execution for target_service=agiflow.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
import urllib.error
import urllib.request
import urllib.parse
from dataclasses import dataclass
from typing import Any, Callable, Protocol

WORKER_ID = "ada-agiflow-external-sync-consumer"
REQUIRED_TOOLS = {"list_task_comments", "create_task_comment"}
IDEMPOTENCY_RE = re.compile(r"^[A-Za-z0-9._:/-]{1,191}$")
MAX_COMMENT_SCAN = 5000
COMMENT_PAGE_SIZE = 100
COMMENT_PAGE_LEASE_RESERVE = 45  # 20s page + 20s ACK + processing margin
DEFAULT_CONTROL_URL = "http://127.0.0.1:8770"


class ConsumerError(RuntimeError):
    retryable = False


class ConnectorError(ConsumerError):
    """Safe typed connector failure. Response bodies never enter logs/state."""
    def __init__(self, code: str, *, retryable: bool = True):
        self.code = re.sub(r"[^A-Z0-9_]", "_", code.split(":")[0].upper())[:80]
        self.retryable = retryable
        super().__init__(self.code)


class QueueError(ConsumerError):
    failure_scope = "queue"

    def __init__(self, code: str, *, retryable: bool = True):
        self.code = re.sub(r"[^A-Z0-9_]", "_", code.split(":")[0].upper())[:80]
        self.retryable = retryable
        super().__init__(self.code)


class LeaseBudgetError(QueueError):
    retryable = True


class CoreClient(Protocol):
    def claim(self) -> dict[str, Any] | None: ...
    def ack(
        self,
        target: str,
        outcome: str,
        *,
        observed_external_version: str | None = None,
        error: str | None = None,
    ) -> dict[str, Any]: ...


class AgiflowClient(Protocol):
    def probe(self) -> dict[str, Any]: ...
    def list_comments(self, task_id: str, *,
                      ensure_page_budget: Callable[[float], None] | None = None) -> list[dict[str, Any]]: ...
    def create_comment(self, task_id: str, content: str) -> dict[str, Any]: ...


class CommentScan(list):
    """A bounded scan can reconcile a seen marker but cannot prove absence."""
    def __init__(self, rows, *, complete: bool, reason: str = "COMMENT_SCAN_LIMIT_EXCEEDED"):
        super().__init__(rows)
        self.complete = complete
        self.reason = reason


class RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward API keys or bearer tokens to a redirected origin.
        raise ConnectorError("HTTP_REDIRECT_REFUSED", retryable=False)


HTTP_OPENER = urllib.request.build_opener(RejectRedirects())


def _json_request(
    url: str,
    payload: dict[str, Any],
    *,
    headers: dict[str, str],
    timeout: float = 20.0,
    allow_null: bool = False,
) -> tuple[int, dict[str, Any] | None]:
    data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    for key, value in headers.items():
        req.add_header(key, value)
    try:
        with HTTP_OPENER.open(req, timeout=timeout) as resp:
            body = resp.read(1048577)
            if len(body) > 1048576:
                raise ConnectorError("RESPONSE_TOO_LARGE", retryable=False)
            raw = body.decode("utf-8", "replace")
            status = int(resp.status)
            ctype = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        raise ConnectorError(
            f"HTTP_{exc.code}",
            retryable=exc.code in {408, 425, 429} or exc.code >= 500,
        ) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ConnectorError(f"HTTP_TRANSPORT:{type(exc).__name__}:{str(exc)[:300]}") from exc

    if "text/event-stream" in ctype:
        messages: list[dict[str, Any]] = []
        for line in raw.splitlines():
            if not line.startswith("data:"):
                continue
            try:
                obj = json.loads(line[5:].strip())
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                messages.append(obj)
        return status, messages[-1] if messages else {}

    try:
        obj = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        raise ConnectorError("INVALID_JSON_RESPONSE") from exc
    if allow_null and obj is None:
        return status, None
    if not isinstance(obj, dict):
        raise ConnectorError("INVALID_OBJECT_RESPONSE")
    return status, obj


@dataclass
class HttpControlCoreClient:
    base_url: str
    token: str
    lease_seconds: int = 180
    claim_target: str | None = None
    claim_attempt: int | None = None
    claim_deadline: float | None = None

    def ensure_write_budget(self, seconds: float = 80):
        if self.claim_deadline is None or time.monotonic() + seconds >= self.claim_deadline:
            raise LeaseBudgetError("CLAIM_LEASE_BUDGET_EXHAUSTED")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        try:
            _, obj = _json_request(
                self.base_url.rstrip("/") + path,
                payload,
                headers={"Authorization": "Bearer " + self.token},
                allow_null=path == "/external-sync/claim",
            )
        except ConnectorError as exc:
            # Core authorization/lease errors are not Agiflow availability.
            raise QueueError(exc.code, retryable=exc.retryable) from exc
        return obj

    def claim(self) -> dict[str, Any] | None:
        obj = self._post(
            "/external-sync/claim",
            {
                "worker_id": WORKER_ID,
                "target_service": "agiflow",
                "lease_seconds": self.lease_seconds,
            },
        )
        self.claim_target = None
        self.claim_attempt = None
        self.claim_deadline = None
        if obj is None:
            return None
        if not isinstance(obj, dict):
            raise QueueError("CLAIM_RESPONSE_INVALID")
        target = str(obj.get("stable_id") or obj.get("id") or "")
        attempt = obj.get("attempts")
        if obj.get("locked_by") != WORKER_ID or type(attempt) is not int or attempt < 1 or not target:
            raise QueueError("CLAIM_BINDING_INVALID")
        try:
            expiry = datetime.fromisoformat(str(obj["lease_until"]).replace("Z", "+00:00"))
            if expiry.tzinfo is None:
                raise ValueError()
            remaining = expiry.timestamp() - datetime.now(timezone.utc).timestamp()
            if remaining <= 0:
                raise ValueError()
        except (KeyError, TypeError, ValueError):
            raise QueueError("CLAIM_LEASE_INVALID")
        self.claim_target = target
        self.claim_attempt = attempt
        self.claim_deadline = time.monotonic() + min(self.lease_seconds, remaining)
        return obj

    def ack(
        self,
        target: str,
        outcome: str,
        *,
        observed_external_version: str | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        if target != self.claim_target or self.claim_attempt is None:
            raise QueueError("ACK_CLAIM_BINDING_MISSING")
        self.ensure_write_budget(20)
        payload: dict[str, Any] = {"outcome": outcome, "worker_id": WORKER_ID,
                                   "claim_attempt": self.claim_attempt}
        if observed_external_version:
            payload["observed_external_version"] = observed_external_version
        if error:
            payload["error"] = error[:1000]
        return self._post("/external-sync/" + target + "/ack", payload)


@dataclass
class StatelessAgiflowMcpClient:
    url: str
    api_key: str

    def _rpc(self, request_id: int, method: str, params: dict[str, Any]) -> dict[str, Any]:
        _, obj = _json_request(
            self.url,
            {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params},
            headers={"x-api-key": self.api_key},
        )
        if obj.get("error"):
            raise ConnectorError("MCP_ERROR")
        result = obj.get("result")
        if not isinstance(result, dict):
            raise ConnectorError("MCP_RESULT_MISSING")
        return result

    @staticmethod
    def _tool_payload(result: dict[str, Any]) -> Any:
        if result.get("isError"):
            text = " ".join(
                str(x.get("text") or "")
                for x in result.get("content") or []
                if isinstance(x, dict)
            )
            raise ConnectorError("MCP_TOOL_ERROR")
        texts = [
            x.get("text")
            for x in result.get("content") or []
            if isinstance(x, dict)
            and x.get("type") == "text"
            and isinstance(x.get("text"), str)
        ]
        if not texts:
            return {}
        try:
            return json.loads(texts[0])
        except json.JSONDecodeError as exc:
            raise ConnectorError("MCP_TOOL_INVALID_JSON") from exc

    def _call_tool(self, request_id: int, name: str, arguments: dict[str, Any]) -> Any:
        result = self._rpc(
            request_id,
            "tools/call",
            {"name": name, "arguments": arguments},
        )
        return self._tool_payload(result)

    def probe(self) -> dict[str, Any]:
        result = self._rpc(1, "tools/list", {})
        tools = result.get("tools") or []
        names = {str(t.get("name") or "") for t in tools if isinstance(t, dict)}
        missing = sorted(REQUIRED_TOOLS - names)
        if missing:
            raise ConnectorError("AGIFLOW_REQUIRED_TOOLS_MISSING:" + ",".join(missing), retryable=False)
        return {"tool_count": len(names), "required_tools": sorted(REQUIRED_TOOLS)}

    def list_comments(self, task_id: str, *,
                      ensure_page_budget: Callable[[float], None] | None = None) -> list[dict[str, Any]]:
        comments: list[dict[str, Any]] = []
        offset = 0
        complete = False
        reason = "COMMENT_SCAN_LIMIT_EXCEEDED"
        while offset < MAX_COMMENT_SCAN:
            if ensure_page_budget is not None:
                try:
                    ensure_page_budget(COMMENT_PAGE_LEASE_RESERVE)
                except LeaseBudgetError:
                    # Return observed markers, but never treat a time-bound
                    # partial history as absence. Reserve the fenced ACK.
                    reason = "COMMENT_SCAN_LEASE_BUDGET_EXHAUSTED"
                    break
            page = self._call_tool(
                1000 + offset,
                "list_task_comments",
                {
                    "taskId": task_id,
                    "limit": COMMENT_PAGE_SIZE,
                    "offset": offset,
                    "sort": "createdAt",
                    "order": "desc",
                },
            )
            if not isinstance(page, dict):
                raise ConnectorError("COMMENTS_RESPONSE_INVALID")
            batch = page.get("comments") or []
            if not isinstance(batch, list):
                raise ConnectorError("COMMENTS_LIST_INVALID")
            if len(batch) > COMMENT_PAGE_SIZE:
                raise ConnectorError("COMMENTS_PAGE_LIMIT_INVALID")
            comments.extend(x for x in batch if isinstance(x, dict))
            total = page.get("total")
            offset += len(batch)
            if type(total) is int:
                if offset >= total:
                    complete = True
                    break
            if len(batch) < COMMENT_PAGE_SIZE:
                complete = type(total) is not int
                break
        return CommentScan(comments, complete=complete, reason=reason)

    def create_comment(self, task_id: str, content: str) -> dict[str, Any]:
        obj = self._call_tool(
            9001,
            "create_task_comment",
            {"taskId": task_id, "content": content},
        )
        return obj if isinstance(obj, dict) else {}


def _parse_item(item: dict[str, Any]) -> dict[str, str]:
    if str(item.get("target_service") or "") != "agiflow":
        raise QueueError("UNEXPECTED_TARGET_SERVICE")
    if str(item.get("entity_type") or "") != "task_comment":
        raise QueueError("UNSUPPORTED_ENTITY_TYPE")
    if str(item.get("operation") or "") != "create_task_comment":
        raise QueueError("UNSUPPORTED_OPERATION")

    try:
        payload = json.loads(str(item.get("payload_json") or "{}"))
    except json.JSONDecodeError as exc:
        raise QueueError("INVALID_PAYLOAD_JSON") from exc
    if not isinstance(payload, dict):
        raise QueueError("INVALID_PAYLOAD_OBJECT")

    task_id = str(payload.get("task_ref") or item.get("entity_id") or "").strip()
    content = str(payload.get("content") or "")
    idem = str(item.get("idempotency_key") or payload.get("idempotency_key") or "").strip()
    source_stable = str(payload.get("stable_id") or "").strip()
    if not task_id or not content or not idem:
        raise QueueError("TARGET_CONTENT_OR_IDEMPOTENCY_MISSING")
    if str(item.get("entity_id") or "").strip() not in ("", task_id):
        raise QueueError("ENTITY_ID_PAYLOAD_MISMATCH")
    if str(payload.get("idempotency_key") or idem).strip() != idem:
        raise QueueError("IDEMPOTENCY_PAYLOAD_MISMATCH")
    if not IDEMPOTENCY_RE.fullmatch(idem):
        raise QueueError("IDEMPOTENCY_FORMAT_INVALID")
    marker = f"[sync:{idem}]"
    if marker not in content:
        raise QueueError("DURABLE_MARKER_MISSING")
    return {
        "task_id": task_id,
        "content": content,
        "idempotency_key": idem,
        "marker": marker,
        "source_stable_id": source_stable,
    }


def _comment_marker_matches(
    comments: list[dict[str, Any]], marker: str
) -> list[dict[str, Any]]:
    return [row for row in comments if marker in str(row.get("content") or "")]


def _comment_id(row: dict[str, Any]) -> str:
    return str(row.get("id") or row.get("commentId") or "").strip()


def mirror_local_external_state(source_stable_id: str, external_state: str) -> dict[str, Any]:
    if not source_stable_id:
        return {"status": "SKIPPED", "reason": "source_stable_id_missing"}
    py = "/srv/maziyar-wp-mcp/.venv/bin/python"
    ledger = "/srv/maziyar-wp-mcp/deploy/run_ledger_outbox.py"
    try:
        p = subprocess.run(
            [
                py,
                ledger,
                "set-external-sync",
                "--target",
                source_stable_id,
                "--external-sync-state",
                external_state,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception as exc:
        return {"status": "FAILED", "error": type(exc).__name__}
    if p.returncode != 0:
        return {"status": "FAILED", "error": "LOCAL_MIRROR_FAILED"}
    return {"status": "OK"}


def _ack_and_mirror(
    core: CoreClient,
    item: dict[str, Any],
    parsed: dict[str, str] | None,
    outcome: str,
    *,
    observed: str | None = None,
    error: str | None = None,
    mirror: bool = True,
) -> dict[str, Any]:
    target = str(item.get("stable_id") or item.get("id") or "").strip()
    if not target:
        raise QueueError("QUEUE_TARGET_MISSING")
    updated = core.ack(
        target,
        outcome,
        observed_external_version=observed,
        error=error,
    )
    mirror_result = {"status": "SKIPPED"}
    if mirror and parsed:
        if outcome == "succeeded":
            state = "AGIFLOW_SYNCED:" + str(observed or "")
        elif outcome == "retry":
            state = "CONTROL_CORE_RETRY"
        elif outcome == "conflict":
            state = "AGIFLOW_CONFLICT"
        else:
            state = "AGIFLOW_QUARANTINED"
        mirror_result = mirror_local_external_state(
            parsed.get("source_stable_id", ""), state
        )
    return {"queue": updated, "local_mirror": mirror_result}


def safe_error(exc: Exception) -> str:
    return exc.code if isinstance(exc, (ConnectorError, QueueError)) else type(exc).__name__


def _retry_after_error(core, item, parsed, exc, phase, *, mirror):
    try:
        ack = _ack_and_mirror(core, item, parsed, "retry",
                              error="AGIFLOW_" + phase.upper() + "_FAILED:" + safe_error(exc),
                              mirror=mirror)
    except Exception as ack_exc:
        if isinstance(exc, ConnectorError):
            # Preserve provider denial even when queue bookkeeping is unavailable.
            # The authoritative lease can expire; never mask the connector latch.
            raise exc from ack_exc
        raise
    return {"status": "RETRYABLE", "claimed": True, "phase": phase, "ack": ack,
            "retryable": getattr(exc, "retryable", True), "reason": safe_error(exc),
            "failure_scope": getattr(exc, "failure_scope", "connector")}


def _quarantine_incomplete_scan(core, item, parsed, phase, *, mirror,
                                reason="COMMENT_SCAN_LIMIT_EXCEEDED"):
    # The same bounded scan cannot prove absence on a larger history. Keep this
    # obligation in the existing queue for operator reconciliation, not retries
    # or a second replay owner. An observed marker is handled before this guard.
    ack = _ack_and_mirror(core, item, parsed, "quarantined", error=reason, mirror=mirror)
    return {"status": "QUARANTINED", "claimed": True, "phase": phase,
            "reason": reason, "owner_action_required": True,
            "failure_scope": "queue", "ack": ack}


def consume_one(
    core: CoreClient,
    agiflow: AgiflowClient,
    *,
    enabled: bool,
    mirror: bool = True,
) -> dict[str, Any]:
    if not enabled:
        return {"status": "DISABLED", "claimed": False}

    probe = agiflow.probe()
    item = core.claim()
    if not item:
        return {"status": "NO_ELIGIBLE_UNIT", "claimed": False, "probe": probe}

    parsed: dict[str, str] | None = None
    try:
        parsed = _parse_item(item)
    except QueueError as exc:
        ack = _ack_and_mirror(
            core,
            item,
            parsed,
            "quarantined",
            error=str(exc),
            mirror=mirror,
        )
        return {
            "status": "QUARANTINED",
            "claimed": True,
            "reason": str(exc),
            "ack": ack,
        }

    marker = parsed["marker"]
    task_id = parsed["task_id"]
    try:
        before = agiflow.list_comments(task_id, ensure_page_budget=getattr(core, "ensure_write_budget", None))
    except Exception as exc:
        return _retry_after_error(core, item, parsed, exc, "precheck", mirror=mirror)

    matches = _comment_marker_matches(before, marker)
    if len(matches) > 1:
        ack = _ack_and_mirror(
            core,
            item,
            parsed,
            "conflict",
            error="DUPLICATE_DURABLE_MARKER",
            mirror=mirror,
        )
        return {
            "status": "CONFLICT",
            "claimed": True,
            "matches": len(matches),
            "ack": ack,
        }
    if len(matches) == 1:
        observed = _comment_id(matches[0])
        if not observed:
            ack = _ack_and_mirror(
                core,
                item,
                parsed,
                "conflict",
                error="EXISTING_MARKER_COMMENT_ID_MISSING",
                mirror=mirror,
            )
            return {
                "status": "CONFLICT",
                "claimed": True,
                "matches": 1,
                "ack": ack,
            }
        ack = _ack_and_mirror(
            core,
            item,
            parsed,
            "succeeded",
            observed=observed,
            mirror=mirror,
        )
        return {
            "status": "DEDUPED_EXISTING",
            "claimed": True,
            "observed_external_version": observed,
            "ack": ack,
        }

    if not getattr(before, "complete", True):
        return _quarantine_incomplete_scan(core, item, parsed, "precheck", mirror=mirror,
                                          reason=getattr(before, "reason", "COMMENT_SCAN_LIMIT_EXCEEDED"))

    try:
        if hasattr(core, "ensure_write_budget"):
            core.ensure_write_budget()
        agiflow.create_comment(task_id, parsed["content"])
    except Exception as exc:
        return _retry_after_error(core, item, parsed, exc, "create", mirror=mirror)

    try:
        after = agiflow.list_comments(task_id, ensure_page_budget=getattr(core, "ensure_write_budget", None))
    except Exception as exc:
        return _retry_after_error(core, item, parsed, exc, "verify", mirror=mirror)

    matches = _comment_marker_matches(after, marker)
    if len(matches) == 0:
        if not getattr(after, "complete", True):
            return _quarantine_incomplete_scan(core, item, parsed, "verify", mirror=mirror,
                                              reason=getattr(after, "reason", "COMMENT_SCAN_LIMIT_EXCEEDED"))
        ack = _ack_and_mirror(
            core,
            item,
            parsed,
            "retry",
            error="AGIFLOW_MARKER_NOT_OBSERVED_AFTER_CREATE",
            mirror=mirror,
        )
        return {
            "status": "RETRYABLE",
            "claimed": True,
            "phase": "verify_missing",
            "ack": ack,
        }
    if len(matches) > 1:
        ack = _ack_and_mirror(
            core,
            item,
            parsed,
            "conflict",
            error="DUPLICATE_DURABLE_MARKER_AFTER_CREATE",
            mirror=mirror,
        )
        return {
            "status": "CONFLICT",
            "claimed": True,
            "matches": len(matches),
            "ack": ack,
        }

    observed = _comment_id(matches[0])
    if not observed:
        ack = _ack_and_mirror(
            core,
            item,
            parsed,
            "retry",
            error="CREATED_MARKER_COMMENT_ID_MISSING",
            mirror=mirror,
        )
        return {
            "status": "RETRYABLE",
            "claimed": True,
            "phase": "verify_id",
            "ack": ack,
        }

    ack = _ack_and_mirror(
        core,
        item,
        parsed,
        "succeeded",
        observed=observed,
        mirror=mirror,
    )
    return {
        "status": "SUCCEEDED",
        "claimed": True,
        "observed_external_version": observed,
        "ack": ack,
    }


def _enabled_from_env() -> bool:
    return os.environ.get("AGIFLOW_CONSUMER_ENABLED", "false").strip().lower() == "true"


def build_agiflow_client() -> StatelessAgiflowMcpClient:
    agiflow_url = os.environ.get("AGIFLOW_MCP_URL", "").strip()
    agiflow_key = os.environ.get("AGIFLOW_API_KEY", "").strip()
    missing = [
        name
        for name, value in (
            ("AGIFLOW_MCP_URL", agiflow_url),
            ("AGIFLOW_API_KEY", agiflow_key),
        )
        if not value
    ]
    if missing:
        raise ConsumerError("MISSING_ENV:" + ",".join(missing))
    return StatelessAgiflowMcpClient(agiflow_url, agiflow_key)


def build_live_clients() -> tuple[HttpControlCoreClient, StatelessAgiflowMcpClient]:
    core_token = os.environ.get("CONTROL_API_TOKEN", "").strip()
    if not core_token:
        raise QueueError("CONTROL_API_TOKEN_MISSING", retryable=False)
    return (
        HttpControlCoreClient(
            os.environ.get("CONTROL_CORE_URL", DEFAULT_CONTROL_URL).strip()
            or DEFAULT_CONTROL_URL,
            core_token,
        ),
        build_agiflow_client(),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--reset-circuit", action="store_true")
    ap.add_argument("--circuit-state", default="/srv/maziyar-wp-mcp/state/agiflow-consumer-circuit.json")
    args = ap.parse_args()
    if sum((args.probe, args.once, args.reset_circuit)) != 1:
        ap.error("choose exactly one of --probe, --once or --reset-circuit")

    try:
        if args.probe:
            agiflow = build_agiflow_client()
            print(json.dumps({"status": "OK", "probe": agiflow.probe()}, sort_keys=True))
            return 0
        if not args.reset_circuit and not _enabled_from_env():
            print(json.dumps({"status": "DISABLED", "claimed": False}, sort_keys=True))
            return 0
        from circuit_gate import CircuitGate
        with CircuitGate(args.circuit_state) as gate:
            result = gate.run(
                lambda: consume_one(*build_live_clients(), enabled=True),
                reset_probe=(lambda: build_agiflow_client().probe()) if args.reset_circuit else None,
            )
        # Queue payloads, comments and provider errors are never logged.
        public = {key: value for key, value in result.items() if key in {
            "status", "claimed", "phase", "reason", "retryable", "retry_at",
            "failure_count", "owner_action_required",
        }}
        print(json.dumps(public, sort_keys=True, default=str))
        return 1 if result.get("status") == "QUEUE_ERROR" else 0
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "error": safe_error(exc),
                },
                sort_keys=True,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
