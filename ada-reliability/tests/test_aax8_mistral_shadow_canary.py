"""AAX-8 Mistral shadow canary: live flag stays false without loopback chat."""
from __future__ import annotations

import pytest
from ada_reliability.crypto import hmac_verify
from ada_reliability.engine import AdaEngine, AdaError, seed_phase1
from ada_reliability.mistral_shadow_canary import (
    CANARY_PROMPT,
    FORBIDDEN_WORKER_ACTIONS,
    MistralShadowCanary,
    is_live_mistral_participation,
    participation_is_forbidden,
    secret_free_participation,
)
from ada_reliability.shadow_pipeline import unsigned_evidence

HMAC = "phase1-test-hmac-key-must-be-32+"


def fresh():
    e = AdaEngine(hmac_key=HMAC, key_id="test-key", receipt_ttl=900)
    seed_phase1(e)
    return e


def live_shaped(**overrides):
    base = {
        "source": "loopback_internal_chat",
        "host": "127.0.0.1",
        "port": 9102,
        "path": "/internal/chat",
        "method": "POST",
        "http_status": 200,
        "executed": True,
        "model": "mistral-small-latest",
        "text": "SHADOW_OK",
        "finish_reason": "stop",
        "usage": {"total_tokens": 8},
        "job_created": False,
        "schedule_mutated": False,
    }
    base.update(overrides)
    return base


def test_prompt_forbids_production_routes():
    assert "SHADOW_OK" in CANARY_PROMPT
    assert "WordPress" in CANARY_PROMPT
    assert "create_job" in FORBIDDEN_WORKER_ACTIONS
    assert "mistral_local_create_job" in FORBIDDEN_WORKER_ACTIONS
    assert "execute_workflow" in FORBIDDEN_WORKER_ACTIONS
    assert "wp_publish" in FORBIDDEN_WORKER_ACTIONS


def test_job_type_is_not_participation():
    fake = {
        "source": "adapter.get_job",
        "job_type": "mistral.chat",
        "executed": False,
        "text": "hello",
        "model": "mistral-small-latest",
        "host": "127.0.0.1",
        "port": 9102,
        "path": "/internal/chat",
        "method": "POST",
        "http_status": 200,
    }
    assert is_live_mistral_participation(fake) is False


def test_healthz_is_not_participation():
    assert (
        is_live_mistral_participation(
            {
                "source": "healthz",
                "host": "127.0.0.1",
                "port": 9102,
                "path": "/healthz",
                "method": "GET",
                "http_status": 200,
                "executed": True,
                "text": "ok",
                "model": "mistral-small-latest",
            }
        )
        is False
    )


def test_live_bar_accepts_only_executed_loopback_chat():
    assert is_live_mistral_participation(live_shaped()) is True
    assert is_live_mistral_participation(live_shaped(executed=False)) is False
    assert is_live_mistral_participation(live_shaped(host="api.mistral.ai")) is False
    assert is_live_mistral_participation(live_shaped(path="/mcp")) is False
    assert is_live_mistral_participation(live_shaped(text="")) is False


def test_canary_without_participation_keeps_live_false_and_does_not_mutate():
    e = fresh()
    writes = e.wp.writes
    journal = set(e.journal)
    canary = MistralShadowCanary(e)
    record = canary.run()
    assert record["live_mistral_job"] is False
    assert record["mistral_participated"] is False
    assert record["evidence_kind"] == "repository_shadow_canary"
    assert record["mutated"] is False
    assert record["production_sql"] is False
    assert record["production_mutation"] is False
    assert record["job_enqueued"] is False
    assert e.wp.writes == writes
    assert set(e.journal) == journal
    assert hmac_verify(unsigned_evidence(record), record["evidence_hmac"], HMAC)


def test_fixture_with_executed_true_is_the_predicate_only_not_a_live_claim_in_docs():
    """The predicate is unit-tested; pytest is still not a VPS POST.

    A well-formed participation object is how the live host will mark
    executed=True after loopback chat. This test proves the canary
    record would flip, and that it still does not write.
    """
    e = fresh()
    writes = e.wp.writes
    canary = MistralShadowCanary(e)
    record = canary.run(participation=live_shaped())
    assert record["live_mistral_job"] is True
    assert record["mistral_participated"] is True
    assert record["evidence_kind"] == "live_mistral_canary"
    part = record["worker_participation"]
    assert part["payload_copied"] is False
    assert part["job_created"] is False
    assert part["text_sha256"]
    assert "SHADOW_OK" not in str(part)  # body not copied into sealed participation
    assert e.wp.writes == writes
    assert hmac_verify(unsigned_evidence(record), record["evidence_hmac"], HMAC)


def test_forbidden_worker_action_raises_and_does_not_mutate():
    e = fresh()
    writes = e.wp.writes
    canary = MistralShadowCanary(e)
    with pytest.raises(AdaError) as exc:
        canary.run(participation=live_shaped(action="mistral_local_create_job"))
    assert exc.value.code == "CANARY_MUTATION_ROUTE"
    assert e.wp.writes == writes
    assert participation_is_forbidden({"tool": "create_schedule"}) == "create_schedule"


def test_secret_free_participation_omits_prompt_and_keys():
    redacted = secret_free_participation(
        live_shaped(api_key="sk-live-not-for-git", prompt=CANARY_PROMPT)
    )
    blob = str(redacted)
    assert "sk-live" not in blob
    assert "API" not in blob
    assert CANARY_PROMPT not in blob
