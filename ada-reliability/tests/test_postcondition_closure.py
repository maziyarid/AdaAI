
"""Regression tests: journal postcondition must be proven before task closure.

Covers AAX-2 P1 "Journaled Postcondition Is Ignored":
  A. exact journal postcondition -> verify -> completion succeeds
  B. strict superset verification -> completion succeeds
  C. weak HTTP-only verification for a metadata journal -> completion denied
  D. resource diverges after apply, then weak verification -> completion denied
  E. resource changes after a correct verification but before close -> denied
  F. wrong after_mutation_id cannot close
  G. prior pre-mutation verification remains unusable
  H. approved publish end-to-end (grant -> journal -> apply -> verify -> close)
     remains green
"""
import pytest

from ada_reliability.engine import AdaEngine, AdaError, IDENTITIES
from ada_reliability.seed import seed_phase1

HMAC = "phase1-test-hmac-key-must-be-32+"


def fresh():
    e = AdaEngine(hmac_key=HMAC, key_id="test-key", receipt_ttl=900)
    seed_phase1(e)
    e.register_passport(agent_id="mistral-canary", task_type="academic_content",
                        allowed_sites=["teznevise.ir"], allowed_tools=["wp_update_metadata"])
    return e


def _setup(applied=True, mutation_type="METADATA_UPDATE"):
    """task -> bootstrap -> snapshot -> authorize -> journal -> (apply)."""
    e = fresh()
    task = e.create_task(
        idempotency_key="t-pc", task_type="academic_content",
        agent_id="mistral-canary", requested_action="wp_update_metadata",
        site_id="teznevise.ir", project_id="teznevise",
    )
    pack = e.bootstrap(
        agent_id="mistral-canary", task_run_id=task["id"],
        project_id="teznevise", site_id="teznevise.ir",
        task_type="academic_content",
    )
    snap = e.snapshot("teznevise.ir", "42", "worker")
    payload = {"resource_id": "42", "meta": {"yoast_title": "خدمات نگارش"}}
    e.authorize(
        action="wp_update_metadata", payload=payload, passport=pack["passport"],
        context_receipt=pack["receipt_id"], agent_id="mistral-canary",
        task_type="academic_content", site_id="teznevise.ir",
        mutation_type=mutation_type, snapshot_hash=snap["snapshot_hash"],
        idempotency_key="idem-pc",
    )
    j = e.journal_intent(
        task_run_id=task["id"], idempotency_key="idem-pc",
        tool_name="wp_update_metadata", site_id="teznevise.ir", resource_id="42",
        payload=payload, snapshot_id=snap["id"],
        expected_postcondition={"http_status": 200, "meta": payload["meta"],
                                "zwnj_rule": "zero"},
    )
    if applied:
        e.apply_authorized_mutation(journal_id=j["id"])
    return e, task, j, payload


# A. exact postcondition -> close succeeds
def test_A_exact_postcondition_closes():
    e, task, j, payload = _setup()
    v = e.verify_live(site_id="teznevise.ir", resource_id="42",
                      expected={"http_status": 200, "meta": payload["meta"],
                                "zwnj_rule": "zero"},
                      after_mutation_id=j["id"])
    assert v["passed"]
    closed = e.close_task_if_verified(task["id"], j["id"])
    assert closed["state"] == "COMPLETED"
    assert closed["verification"]["id"] == v["id"]


# B. strict superset verification closes.
# NOTE: since the SUPPORTED_POSTCONDITION_KEYS schema landed, a strict
# superset must be expressed with supported keys only; arbitrary unsupported
# keys (e.g. "extra_probe") now fail closed in verify_live (see test_I).
def test_B_superset_verification_closes():
    e, task, j, payload = _setup()
    live = e.wp.read("teznevise.ir", "42")
    v = e.verify_live(site_id="teznevise.ir", resource_id="42",
                      expected={"http_status": 200, "meta": payload["meta"],
                                "zwnj_rule": "zero", "content": live.content},
                      after_mutation_id=j["id"])
    assert v["passed"]
    closed = e.close_task_if_verified(task["id"], j["id"])
    assert closed["state"] == "COMPLETED"


# C. weak HTTP-only verification cannot close a metadata journal
def test_C_weak_http_only_verification_denied():
    e, task, j, payload = _setup()
    v = e.verify_live(site_id="teznevise.ir", resource_id="42",
                      expected={"http_status": 200},
                      after_mutation_id=j["id"])
    assert v["passed"]
    with pytest.raises(AdaError) as ei:
        e.close_task_if_verified(task["id"], j["id"])
    assert ei.value.code == "POSTCONDITION_NOT_PROVEN"
    assert e.tasks[task["id"]]["state"] != "COMPLETED"


# D. resource diverges after apply, then weak verification -> denied
def test_D_divergence_then_weak_verification_denied():
    e, task, j, payload = _setup()
    # divergence: mutate resource again outside the journal
    e.wp.write_metadata("teznevise.ir", "42", {"yoast_title": "تغییر ناخواسته"})
    v = e.verify_live(site_id="teznevise.ir", resource_id="42",
                      expected={"http_status": 200},
                      after_mutation_id=j["id"])
    assert v["passed"]
    with pytest.raises(AdaError) as ei:
        e.close_task_if_verified(task["id"], j["id"])
    assert ei.value.code in ("POSTCONDITION_NOT_PROVEN", "STALE_VERIFICATION")
    assert e.tasks[task["id"]]["state"] != "COMPLETED"


# E. resource changes after a correct verification but before close -> denied
def test_E_resource_changes_after_verification_denied():
    e, task, j, payload = _setup()
    v = e.verify_live(site_id="teznevise.ir", resource_id="42",
                      expected={"http_status": 200, "meta": payload["meta"],
                                "zwnj_rule": "zero"},
                      after_mutation_id=j["id"])
    assert v["passed"]
    # resource changes AFTER the qualifying verification, BEFORE close
    e.wp.write_metadata("teznevise.ir", "42", {"yoast_title": "بعد از تأیید"})
    with pytest.raises(AdaError) as ei:
        e.close_task_if_verified(task["id"], j["id"])
    assert ei.value.code == "STALE_VERIFICATION"
    assert e.tasks[task["id"]]["state"] != "COMPLETED"


# F. wrong after_mutation_id cannot close
def test_F_wrong_after_mutation_id_denied():
    e, task, j, payload = _setup()
    v = e.verify_live(site_id="teznevise.ir", resource_id="42",
                      expected={"http_status": 200, "meta": payload["meta"],
                                "zwnj_rule": "zero"},
                      after_mutation_id="other-journal")
    assert v["passed"]
    with pytest.raises(AdaError) as ei:
        e.close_task_if_verified(task["id"], j["id"])
    assert ei.value.code == "FRESH_VERIFICATION_REQUIRED"


# G. prior pre-mutation verification remains unusable
def test_G_pre_mutation_verification_unusable():
    e, task, j, payload = _setup(applied=False)
    pre = e.verify_live(site_id="teznevise.ir", resource_id="42",
                        expected={"http_status": 200, "meta": payload["meta"],
                                  "zwnj_rule": "zero"})
    assert pre["passed"] and not pre["stale"]
    e.apply_authorized_mutation(journal_id=j["id"])
    assert pre["stale"] is True
    with pytest.raises(AdaError) as ei:
        e.close_task_if_verified(task["id"], j["id"])
    assert ei.value.code == "STALE_VERIFICATION"


# H. approved publish end-to-end remains green (incl. closure)
def _publisher():
    e = AdaEngine(hmac_key=HMAC, key_id="test-key", receipt_ttl=900)
    seed_phase1(e)
    e.register_passport(
        agent_id="mistral-publisher", task_type="academic_content",
        allowed_sites=["teznevise.ir"],
        allowed_tools=["wp_read", "wp_update_metadata", "wp_publish", "wp_delete"],
        allowed_mutation_types=["METADATA_UPDATE", "PUBLISH", "DELETE"],
        approval_mandatory=False,
        approval_classes=["DELETE", "BULK_WRITE", "EXTERNAL_MESSAGE", "POLICY_CHANGE"],
    )
    task = e.create_task(
        idempotency_key="t-pub-h", task_type="academic_content",
        agent_id="mistral-publisher", requested_action="wp_publish",
        site_id="teznevise.ir", project_id="teznevise",
    )
    pack = e.bootstrap(
        agent_id="mistral-publisher", task_run_id=task["id"],
        project_id="teznevise", site_id="teznevise.ir",
        task_type="academic_content",
    )
    snap = e.snapshot("teznevise.ir", "42", "worker")
    payload = {"resource_id": "42", "meta": {"yoast_title": "انتشار"}}
    return e, task, pack, snap, payload


def test_H_approved_publish_end_to_end_with_close():
    e, task, pack, snap, payload = _publisher()
    ticket = e.request_approval(
        task_run_id=task["id"], tool_name="wp_publish",
        site_id="teznevise.ir", resource_id="42", payload=payload,
        snapshot_hash=snap["snapshot_hash"], context_receipt_id=pack["receipt_id"],
        requested_by="mistral-publisher", identity=IDENTITIES["MODEL_PROPOSER"],
        idempotency_key="pub-h", mutation_type="PUBLISH",
    )
    granted = e.decide_approval(ticket["id"], approver="maziyar", decision="GRANT",
                                identity=IDENTITIES["HUMAN_APPROVER"])
    e.consume_approval(ticket["id"], granted["one_time_token"], payload,
                       snap["snapshot_hash"])
    second = e.authorize(
        action="wp_publish", payload=payload, passport=pack["passport"],
        context_receipt=pack["receipt_id"], agent_id="mistral-publisher",
        task_type="academic_content", site_id="teznevise.ir",
        mutation_type="PUBLISH", snapshot_hash=snap["snapshot_hash"],
        idempotency_key="pub-h", approval_ticket_id=ticket["id"],
    )
    assert second["decision"] == "ALLOW"
    j = e.journal_intent(
        task_run_id=task["id"], idempotency_key="pub-h",
        tool_name="wp_publish", site_id="teznevise.ir", resource_id="42",
        payload=payload, snapshot_id=snap["id"],
        expected_postcondition={"http_status": 200, "meta": payload["meta"],
                                "zwnj_rule": "zero"},
    )
    applied = e.apply_authorized_mutation(journal_id=j["id"])
    assert applied["mutated"] is True
    verified = e.verify_live(site_id="teznevise.ir", resource_id="42",
                             expected={"http_status": 200, "meta": payload["meta"],
                                       "zwnj_rule": "zero"},
                             after_mutation_id=j["id"])
    assert verified["passed"]
    closed = e.close_task_if_verified(task["id"], j["id"])
    assert closed["state"] == "COMPLETED"


# -- AAX-2 P1 "Unsupported Requirements Verify" ---------------------------
# Unsupported top-level requirement keys must fail closed and must never be
# copied into verified_requirements as unexamined proof.

def _setup_unverified(mutation_type="METADATA_UPDATE"):
    """task -> bootstrap -> snapshot -> authorize (no journal/apply yet)."""
    e = fresh()
    task = e.create_task(
        idempotency_key="t-uns", task_type="academic_content",
        agent_id="mistral-canary", requested_action="wp_update_metadata",
        site_id="teznevise.ir", project_id="teznevise",
    )
    pack = e.bootstrap(
        agent_id="mistral-canary", task_run_id=task["id"],
        project_id="teznevise", site_id="teznevise.ir",
        task_type="academic_content",
    )
    snap = e.snapshot("teznevise.ir", "42", "worker")
    payload = {"resource_id": "42", "meta": {"yoast_title": "خدمات نگارش"}}
    e.authorize(
        action="wp_update_metadata", payload=payload, passport=pack["passport"],
        context_receipt=pack["receipt_id"], agent_id="mistral-canary",
        task_type="academic_content", site_id="teznevise.ir",
        mutation_type=mutation_type, snapshot_hash=snap["snapshot_hash"],
        idempotency_key="idem-uns",
    )
    return e, task, snap, payload


# I. verify_live fails closed on an unsupported top-level requirement
def test_I_verify_live_rejects_unsupported_requirement():
    e, task, j, payload = _setup()
    v = e.verify_live(site_id="teznevise.ir", resource_id="42",
                      expected={"http_status": 200, "canonical": False},
                      after_mutation_id=j["id"])
    assert not v["passed"]
    assert any(f.startswith("UNSUPPORTED_POSTCONDITION") for f in v["failures"])


# J. unsupported requirements are not copied into verified_requirements
def test_J_unsupported_requirements_not_copied_into_proof():
    e, task, j, payload = _setup()
    v = e.verify_live(site_id="teznevise.ir", resource_id="42",
                      expected={"http_status": 200, "canonical": False,
                                "language": "xx"},
                      after_mutation_id=j["id"])
    assert v["verified_requirements"] == {"http_status": 200}


# K. journal creation rejects an unsupported postcondition key (canonical)
def test_K_journal_intent_rejects_unsupported_postcondition():
    e, task, snap, payload = _setup_unverified()
    with pytest.raises(AdaError) as ei:
        e.journal_intent(
            task_run_id=task["id"], idempotency_key="idem-uns",
            tool_name="wp_update_metadata", site_id="teznevise.ir",
            resource_id="42", payload=payload, snapshot_id=snap["id"],
            expected_postcondition={"http_status": 200, "canonical": False},
        )
    assert ei.value.code == "UNSUPPORTED_POSTCONDITION"


# K2. journal creation rejects an unsupported postcondition key (language)
def test_K2_journal_intent_rejects_language_postcondition():
    e, task, snap, payload = _setup_unverified()
    with pytest.raises(AdaError) as ei:
        e.journal_intent(
            task_run_id=task["id"], idempotency_key="idem-uns",
            tool_name="wp_update_metadata", site_id="teznevise.ir",
            resource_id="42", payload=payload, snapshot_id=snap["id"],
            expected_postcondition={"http_status": 200, "language": "xx"},
        )
    assert ei.value.code == "UNSUPPORTED_POSTCONDITION"


# L. a legacy journal requiring `canonical` cannot be closed by supplying the
#    same value to verify_live (the verifier refuses to treat it as proof)
def test_L_canonical_journal_cannot_close_via_matching_caller_value():
    e, task, j, payload = _setup()
    j["expected_postcondition"]["canonical"] = False  # legacy unverifiable journal
    v = e.verify_live(
        site_id="teznevise.ir", resource_id="42",
        expected={"http_status": 200, "meta": payload["meta"],
                  "zwnj_rule": "zero", "canonical": False},
        after_mutation_id=j["id"],
    )
    assert not v["passed"]
    assert "canonical" not in v["verified_requirements"]
    with pytest.raises(AdaError):
        e.close_task_if_verified(task["id"], j["id"])


# M. a legacy journal requiring `language` cannot close without a live validator
def test_M_language_journal_cannot_close_without_validator():
    e, task, j, payload = _setup()
    j["expected_postcondition"]["language"] = "xx"
    v = e.verify_live(
        site_id="teznevise.ir", resource_id="42",
        expected={"http_status": 200, "meta": payload["meta"],
                  "zwnj_rule": "zero", "language": "xx"},
        after_mutation_id=j["id"],
    )
    assert not v["passed"]
    assert "language" not in v["verified_requirements"]
    with pytest.raises(AdaError):
        e.close_task_if_verified(task["id"], j["id"])
