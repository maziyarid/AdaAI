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
become true **only** when a real loopback ``/internal/chat`` response is
supplied with ``executed=True``. Fixtures, job_type ``mistral.chat``,
and MCP tools never count.

Never enqueue production jobs. Never apply SQL. Never write WordPress
or Teznevise. Never introduce a second scheduler.
"""
from __future__ import annotations

from typing import Any, Optional

from .crypto import hmac_sign, sha256_text
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
    """True only for an executed loopback /internal/chat response.

    job_type mistral.chat, healthz, MCP, and fixtures with executed=False
    never qualify.
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
    text_sha = sha256_text(text) if isinstance(text, str) else None
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
        live = is_live_mistral_participation(participation)
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
                "worker_participation": secret_free_participation(participation),
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
