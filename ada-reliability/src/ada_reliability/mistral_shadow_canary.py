"""AAX-8 genuine Mistral shadow canary — fail closed.

The live Mistral worker (`maziyar-mistral-worker.service`, loopback
`:9102`, source `/srv/community-mcp/mistral-worker/index.mjs` v1.3.1)
exposes:

- ``GET /healthz`` — liveness; no jobs
- ``POST /internal/chat`` — loopback-only chat; Mistral credential stays
  in the worker; **does not** create control-core jobs or write WordPress
- ``POST /mcp`` — bearer MCP, includes mutating ``mistral_local_create_job``
  / schedule tools that this canary must never call

This module evaluates a proposal through ``ShadowPipeline`` and records
HMAC-sealed evidence. ``live_mistral_job`` / ``mistral_participated``
become true **only** when ``run()`` itself invokes a transport's
``execute_internal_chat`` (or verifies a worker HMAC on that result)
with a per-run challenge the transport must echo. A caller-created
``participation`` dictionary is never live proof. Fixtures, job_type
``mistral.chat``, healthz, and MCP tools never count.

Never enqueue production jobs. Never apply SQL. Never write WordPress
or Teznevise. Never introduce a second scheduler.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Optional

from .crypto import hmac_sign, hmac_verify, sha256_text, token
from .engine import AdaEngine, AdaError
from .shadow_pipeline import ShadowPipeline, unsigned_evidence

CANARY_ID = "aax8-mistral-shadow-canary"
CANARY_PROMPT = (
    "Ada AAX-8 non-mutating shadow canary. "
    "Reply with exactly SHADOW_OK and nothing else. "
    "Do not propose WordPress, SQL, Teznevise, schedule, or job changes."
)
WORKER_LOOPBACK_URL = "http://127.0.0.1:9102/internal/chat"
WORKER_HEALTHZ_URL = "http://127.0.0.1:9102/healthz"
ALLOWED_CHAT_PATH = "/internal/chat"
ALLOWED_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})
WORKER_RECEIPT_FIELDS = (
    "challenge",
    "canary_id",
    "source",
    "host",
    "port",
    "path",
    "method",
    "http_status",
    "model",
    "text_sha256",
)

# Live worker actions that mutate control-core or Mistral workflow state.
FORBIDDEN_WORKER_ACTIONS = frozenset(
    {
        "create_job",
        "cancel_job",
        "retry_job",
        "create_schedule",
        "update_schedule",
        "pause_schedule",
        "resume_schedule",
        "run_schedule",
        "run-now",
        "delete_schedule",
        "execute_workflow",
        "trigger_schedule",
        "mistral_local_create_job",
        "mistral_local_cancel_job",
        "mistral_local_retry_job",
        "mistral_local_create_schedule",
        "mistral_local_update_schedule",
        "mistral_local_pause_schedule",
        "mistral_local_resume_schedule",
        "mistral_local_run_schedule",
        "mistral_local_delete_schedule",
        "wp_publish",
        "wp_delete",
        "wp_update",
        "apply_sql",
    }
)

SHADOW_OBSERVE_PROPOSAL = {
    "tool": "wp_update_metadata",
    "mutation_type": "METADATA_UPDATE",
    "payload": {"resource_id": "42", "meta": {"yoast_title": "خدمات"}},
    "confidence": 0.99,
}


def participation_is_forbidden(participation: Optional[dict[str, Any]]) -> Optional[str]:
    if not participation:
        return None
    for key in ("action", "tool", "mcp_tool", "control_action"):
        value = participation.get(key)
        if isinstance(value, str) and value in FORBIDDEN_WORKER_ACTIONS:
            return value
    for flag in ("job_created", "schedule_mutated", "wp_written", "sql_applied"):
        if participation.get(flag):
            return flag
    return None


def is_live_mistral_participation(participation: Optional[dict[str, Any]]) -> bool:
    """Shape predicate for an executed loopback /internal/chat response.

    Not live evidence by itself. ``run()`` must still bind a transport
    result (or worker HMAC) to a per-run challenge. job_type
    mistral.chat, healthz, MCP, and fixtures with executed=False never
    qualify.
    """
    if not isinstance(participation, dict):
        return False
    if participation_is_forbidden(participation):
        return False
    if participation.get("executed") is not True:
        return False
    if participation.get("http_status") != 200:
        return False
    if participation.get("source") != "loopback_internal_chat":
        return False
    if participation.get("path") != ALLOWED_CHAT_PATH:
        return False
    if participation.get("method") != "POST":
        return False
    host = str(participation.get("host") or "")
    if host not in ALLOWED_HOSTS:
        return False
    if int(participation.get("port") or 0) != 9102:
        return False
    if participation.get("job_type") and not participation.get("text"):
        return False
    text = participation.get("text")
    model = participation.get("model")
    if not isinstance(text, str) or not text.strip():
        return False
    if not isinstance(model, str) or not model.strip():
        return False
    return True


def secret_free_participation(participation: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    if not isinstance(participation, dict):
        return None
    text = participation.get("text")
    text_sha = sha256_text(text) if isinstance(text, str) else participation.get("text_sha256")
    return {
        "source": participation.get("source"),
        "host": participation.get("host"),
        "port": participation.get("port"),
        "path": participation.get("path"),
        "method": participation.get("method"),
        "http_status": participation.get("http_status"),
        "executed": bool(participation.get("executed") is True),
        "model": participation.get("model"),
        "finish_reason": participation.get("finish_reason"),
        "usage": participation.get("usage"),
        "text_sha256": text_sha,
        "text_len": len(text) if isinstance(text, str) else 0,
        "prompt_id": CANARY_ID,
        "job_created": False,
        "schedule_mutated": False,
        "payload_copied": False,
        "challenge_bound": bool(participation.get("challenge")),
    }


def unsigned_worker_receipt(result: dict[str, Any]) -> dict[str, Any]:
    text = result.get("text")
    text_sha = sha256_text(text) if isinstance(text, str) else result.get("text_sha256")
    body = {k: result.get(k) for k in WORKER_RECEIPT_FIELDS}
    body["text_sha256"] = text_sha
    return body


def verify_worker_receipt(
    result: Optional[dict[str, Any]],
    *,
    worker_hmac_key: str,
    challenge: str,
    engine_hmac_key: str,
) -> bool:
    """True only for a worker HMAC distinct from the canary engine key."""
    if not isinstance(result, dict):
        return False
    if not challenge or result.get("challenge") != challenge:
        return False
    if result.get("canary_id") != CANARY_ID:
        return False
    if not worker_hmac_key or worker_hmac_key == engine_hmac_key:
        return False
    sig = result.get("worker_hmac")
    if not isinstance(sig, str) or not sig:
        return False
    try:
        if not hmac_verify(unsigned_worker_receipt(result), sig, worker_hmac_key):
            return False
    except Exception:
        return False
    return is_live_mistral_participation(result)


def bind_live_from_executor(
    result: Optional[dict[str, Any]],
    *,
    challenge: str,
    transport_invoked: bool,
    worker_hmac_key: Optional[str],
    engine_hmac_key: str,
) -> bool:
    """Live only if this run invoked a transport and the result echoes challenge.

    Caller-supplied participation dicts never reach this helper.
    """
    if not transport_invoked:
        return False
    if not challenge or not isinstance(result, dict):
        return False
    if result.get("challenge") != challenge:
        return False
    if not is_live_mistral_participation(result):
        return False
    if worker_hmac_key:
        return verify_worker_receipt(
            result,
            worker_hmac_key=worker_hmac_key,
            challenge=challenge,
            engine_hmac_key=engine_hmac_key,
        )
    return True


class UrllibLoopbackChatTransport:
    """Authenticated executor: POST loopback /internal/chat. Never /mcp."""

    url = WORKER_LOOPBACK_URL

    def execute_internal_chat(self, prompt: str, canary_id: str, challenge: str) -> dict[str, Any]:
        if not challenge or not isinstance(challenge, str):
            raise AdaError("CANARY_CHALLENGE", "missing challenge")
        if not prompt or canary_id != CANARY_ID:
            raise AdaError("CANARY_PROMPT", canary_id)
        body = json.dumps(
            {
                "prompt": prompt,
                "temperature": 0,
                "max_tokens": 32,
                "canary_id": canary_id,
                "challenge": challenge,
            }
        ).encode()
        req = urllib.request.Request(
            self.url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        if req.full_url != WORKER_LOOPBACK_URL or req.get_method() != "POST":
            raise AdaError("CANARY_TRANSPORT_URL", req.full_url)
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                raw = resp.read()
                status = int(getattr(resp, "status", 200))
        except urllib.error.URLError as exc:
            raise AdaError("CANARY_TRANSPORT", str(exc.reason)[:200]) from exc
        try:
            parsed = json.loads(raw.decode())
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AdaError("CANARY_TRANSPORT", "invalid json") from exc
        choices = parsed.get("choices") if isinstance(parsed, dict) else None
        text = ""
        if isinstance(choices, list) and choices:
            message = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(message, dict):
                text = str(message.get("content") or "")
        if not text and isinstance(parsed, dict):
            text = str(parsed.get("text") or parsed.get("content") or "")
        model = ""
        if isinstance(parsed, dict):
            model = str(parsed.get("model") or "")
        return {
            "source": "loopback_internal_chat",
            "host": "127.0.0.1",
            "port": 9102,
            "path": ALLOWED_CHAT_PATH,
            "method": "POST",
            "http_status": status,
            "executed": True,
            "model": model,
            "text": text,
            "finish_reason": (parsed.get("finish_reason") if isinstance(parsed, dict) else None),
            "usage": (parsed.get("usage") if isinstance(parsed, dict) else None),
            "challenge": challenge,
            "canary_id": canary_id,
            "job_created": False,
            "schedule_mutated": False,
        }


class MistralShadowCanary:
    """Propose via live worker chat (optional) → Ada evaluates → STOP."""

    def __init__(self, engine: AdaEngine):
        self.engine = engine
        self.pipeline = ShadowPipeline(engine)
        self.evidence: list[dict[str, Any]] = []

    def _seal(self, record: dict[str, Any]) -> dict[str, Any]:
        record["evidence_alg"] = "hmac-sha256"
        record["evidence_key_id"] = self.engine.key_id
        record["evidence_hmac"] = hmac_sign(unsigned_evidence(record), self.engine.hmac_key)
        self.evidence.append(record)
        self.pipeline.evidence.append(record)
        return record

    def run(
        self,
        *,
        agent_id: str = "mistral-canary",
        task_type: str = "academic_content",
        project_id: str = "teznevise",
        site_id: str = "teznevise.ir",
        proposal: Optional[dict[str, Any]] = None,
        participation: Optional[dict[str, Any]] = None,
        transport: Any = None,
        worker_hmac_key: Optional[str] = None,
    ) -> dict[str, Any]:
        forbidden = participation_is_forbidden(participation)
        if forbidden:
            raise AdaError("CANARY_MUTATION_ROUTE", forbidden)
        writes_before = int(getattr(self.engine.wp, "writes", 0) or 0)
        journal_before = set(self.engine.journal)
        trace = self.pipeline.evaluate(
            agent_id=agent_id,
            task_type=task_type,
            project_id=project_id,
            site_id=site_id,
            proposal=proposal or SHADOW_OBSERVE_PROPOSAL,
        )
        challenge = token()
        transport_invoked = False
        executor_result: Optional[dict[str, Any]] = None
        if transport is not None:
            execute = getattr(transport, "execute_internal_chat", None)
            if not callable(execute):
                raise AdaError("CANARY_NO_TRANSPORT", type(transport).__name__)
            raw = execute(CANARY_PROMPT, CANARY_ID, challenge)
            transport_invoked = True
            if not isinstance(raw, dict):
                raise AdaError("CANARY_TRANSPORT", "executor result must be a dict")
            forbidden_exec = participation_is_forbidden(raw)
            if forbidden_exec:
                raise AdaError("CANARY_MUTATION_ROUTE", forbidden_exec)
            executor_result = raw
        live = bind_live_from_executor(
            executor_result,
            challenge=challenge,
            transport_invoked=transport_invoked,
            worker_hmac_key=worker_hmac_key,
            engine_hmac_key=self.engine.hmac_key,
        )
        bound = secret_free_participation(executor_result if live else None)
        parent = trace.get("evidence_hmac")
        record = {k: v for k, v in trace.items() if k != "evidence_hmac"}
        record.update(
            {
                "pipeline": "AAX-8",
                "stage": "MISTRAL_SHADOW_CANARY",
                "canary_id": CANARY_ID,
                "canary_prompt_id": CANARY_ID,
                "parent_evidence_hmac": parent,
                "live_mistral_job": live,
                "mistral_participated": live,
                "evidence_kind": (
                    "live_mistral_canary" if live else "repository_shadow_canary"
                ),
                "worker_participation": bound,
                "transport_invoked": transport_invoked,
                "challenge_bound": bool(live),
                "executor": type(transport).__name__ if transport is not None else None,
                "caller_participation_trusted": False,
                "production_sql": False,
                "production_mutation": False,
                "mutated": False,
                "job_enqueued": False,
                "schedule_mutated": False,
            }
        )
        if int(getattr(self.engine.wp, "writes", 0) or 0) != writes_before:
            raise AdaError("SHADOW_WP_WRITE", "WordPress write during Mistral canary")
        if set(self.engine.journal) != journal_before:
            raise AdaError("SHADOW_JOURNAL", "canary must not journal a write intent")
        if trace.get("mutated") or trace.get("production_mutation") or trace.get("production_sql"):
            raise AdaError("SHADOW_MUTATED", "canary parent claimed a mutation")
        return self._seal(record)
