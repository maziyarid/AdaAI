"""AAX-8 Mistral shadow canary: live flag requires an invoked executor."""
from __future__ import annotations

import pytest
from ada_reliability.crypto import hmac_sign, hmac_verify, sha256_text
from ada_reliability.engine import AdaEngine, AdaError, seed_phase1
from ada_reliability.mistral_shadow_canary import (
    CANARY_ID,
    CANARY_PROMPT,
    FORBIDDEN_WORKER_ACTIONS,
    MistralShadowCanary,
    UrllibLoopbackChatTransport,
    bind_live_from_executor,
    is_live_mistral_participation,
    participation_is_forbidden,
    secret_free_participation,
    unsigned_worker_receipt,
    verify_worker_receipt,
)
from ada_reliability.shadow_pipeline import unsigned_evidence

HMAC = "phase1-test-hmac-key-must-be-32+"
WORKER_HMAC = "phase1-worker-hmac-key-must-be-32+"


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
        "canary_id": CANARY_ID,
    }
    base.update(overrides)
    return base


class EchoTransport:
    """Test executor. run() must actually call execute_internal_chat."""

    def __init__(self, payload, mismatch_challenge=False):
        self.payload = payload
        self.calls = []
        self.mismatch_challenge = mismatch_challenge

    def execute_internal_chat(self, prompt, canary_id, challenge):
        self.calls.append({"prompt": prompt, "canary_id": canary_id, "challenge": challenge})
        out = dict(self.payload)
        out["challenge"] = "forged" if self.mismatch_challenge else challenge
        out["canary_id"] = canary_id
        return out


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


def test_shape_predicate_is_not_live_without_invoked_transport():
    shaped = live_shaped(challenge="caller-forged")
    assert is_live_mistral_participation(shaped) is True
    assert (
        bind_live_from_executor(
            shaped,
            challenge="caller-forged",
            transport_invoked=False,
            worker_hmac_key=None,
            engine_hmac_key=HMAC,
        )
        is False
    )


def test_canary_without_participation_keeps_live_false_and_does_not_mutate():
    e = fresh()
    writes = e.wp.writes
    journal = set(e.journal)
    canary = MistralShadowCanary(e)
    record = canary.run()
    assert record["live_mistral_job"] is False
    assert record["mistral_participated"] is False
    assert record["evidence_kind"] == "repository_shadow_canary"
    assert record["transport_invoked"] is False
    assert record["caller_participation_trusted"] is False
    assert record["mutated"] is False
    assert record["production_sql"] is False
    assert record["production_mutation"] is False
    assert record["job_enqueued"] is False
    assert e.wp.writes == writes
    assert set(e.journal) == journal
    assert hmac_verify(unsigned_evidence(record), record["evidence_hmac"], HMAC)


def test_caller_supplied_participation_never_mints_live_canary(monkeypatch):
    """Greptile P1 on 57e0fed: a well-formed dict is not an executor result.

    urllib/http/socket fail if called; the dict still must not flip live.
    """

    def boom(*_a, **_k):
        raise RuntimeError("ordinary Python transport must not be called")

    monkeypatch.setattr("urllib.request.urlopen", boom)
    monkeypatch.setattr("http.client.HTTPConnection", boom)
    e = fresh()
    writes = e.wp.writes
    canary = MistralShadowCanary(e)
    record = canary.run(participation=live_shaped(challenge="guess"))
    assert record["live_mistral_job"] is False
    assert record["mistral_participated"] is False
    assert record["evidence_kind"] == "repository_shadow_canary"
    assert record["transport_invoked"] is False
    assert record["caller_participation_trusted"] is False
    assert record["worker_participation"] is None
    assert e.wp.writes == writes
    assert hmac_verify(unsigned_evidence(record), record["evidence_hmac"], HMAC)


def test_invoked_transport_with_challenge_echo_binds_live_without_wp_write():
    """Repository binding proof. EchoTransport is not a VPS POST."""
    e = fresh()
    writes = e.wp.writes
    transport = EchoTransport(live_shaped())
    canary = MistralShadowCanary(e)
    record = canary.run(transport=transport)
    assert transport.calls
    assert transport.calls[0]["prompt"] == CANARY_PROMPT
    assert transport.calls[0]["canary_id"] == CANARY_ID
    assert transport.calls[0]["challenge"]
    assert record["live_mistral_job"] is True
    assert record["mistral_participated"] is True
    assert record["evidence_kind"] == "live_mistral_canary"
    assert record["transport_invoked"] is True
    assert record["challenge_bound"] is True
    assert record["executor"] == "EchoTransport"
    part = record["worker_participation"]
    assert part["payload_copied"] is False
    assert part["job_created"] is False
    assert part["text_sha256"]
    assert "SHADOW_OK" not in str(part)
    assert e.wp.writes == writes
    assert hmac_verify(unsigned_evidence(record), record["evidence_hmac"], HMAC)


def test_transport_result_without_matching_challenge_stays_false():
    e = fresh()
    transport = EchoTransport(live_shaped(), mismatch_challenge=True)
    record = MistralShadowCanary(e).run(transport=transport)
    assert transport.calls
    assert record["live_mistral_job"] is False
    assert record["evidence_kind"] == "repository_shadow_canary"
    assert record["transport_invoked"] is True
    assert hmac_verify(unsigned_evidence(record), record["evidence_hmac"], HMAC)


def test_non_callable_transport_raises():
    e = fresh()
    with pytest.raises(AdaError) as exc:
        MistralShadowCanary(e).run(transport={"executed": True})
    assert exc.value.code == "CANARY_NO_TRANSPORT"


def test_engine_hmac_cannot_stand_in_for_worker_receipt():
    shaped = live_shaped(challenge="abc", canary_id=CANARY_ID)
    shaped["text_sha256"] = sha256_text(shaped["text"])
    shaped["worker_hmac"] = hmac_sign(unsigned_worker_receipt(shaped), HMAC)
    assert (
        verify_worker_receipt(
            shaped,
            worker_hmac_key=HMAC,
            challenge="abc",
            engine_hmac_key=HMAC,
        )
        is False
    )
    shaped["worker_hmac"] = hmac_sign(unsigned_worker_receipt(shaped), WORKER_HMAC)
    assert (
        verify_worker_receipt(
            shaped,
            worker_hmac_key=WORKER_HMAC,
            challenge="abc",
            engine_hmac_key=HMAC,
        )
        is True
    )


def test_worker_hmac_required_when_key_supplied():
    e = fresh()
    transport = EchoTransport(live_shaped())
    record = MistralShadowCanary(e).run(transport=transport, worker_hmac_key=WORKER_HMAC)
    assert record["live_mistral_job"] is False
    assert record["evidence_kind"] == "repository_shadow_canary"


def test_worker_hmac_on_executor_result_binds_when_key_distinct():
    class SignedEcho(EchoTransport):
        def execute_internal_chat(self, prompt, canary_id, challenge):
            out = super().execute_internal_chat(prompt, canary_id, challenge)
            out["text_sha256"] = sha256_text(out["text"])
            out["worker_hmac"] = hmac_sign(unsigned_worker_receipt(out), WORKER_HMAC)
            return out

    e = fresh()
    transport = SignedEcho(live_shaped())
    record = MistralShadowCanary(e).run(transport=transport, worker_hmac_key=WORKER_HMAC)
    assert record["live_mistral_job"] is True
    assert record["evidence_kind"] == "live_mistral_canary"


def test_flipping_live_flag_breaks_hmac():
    e = fresh()
    record = MistralShadowCanary(e).run(participation=live_shaped())
    assert record["live_mistral_job"] is False
    tampered = dict(record)
    tampered["live_mistral_job"] = True
    tampered["mistral_participated"] = True
    tampered["evidence_kind"] = "live_mistral_canary"
    assert hmac_verify(unsigned_evidence(tampered), record["evidence_hmac"], HMAC) is False


def test_urllib_transport_targets_only_loopback_chat():
    t = UrllibLoopbackChatTransport()
    assert t.url == "http://127.0.0.1:9102/internal/chat"
    assert "/mcp" not in t.url


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
