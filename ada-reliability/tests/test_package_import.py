"""Prove the installed package imports without a hand-edited sys.path (beyond pytest pythonpath)."""
from ada_reliability import (
    AdaEngine,
    AgiflowStateSteward,
    CloseGrant,
    IssuedEvidence,
    apply_authorized_mutation,
    journal_intent,
    seed_phase1,
)
from ada_reliability.mutations import require_authorized_journal


def test_public_api_imports():
    assert callable(AdaEngine)
    assert callable(seed_phase1)
    assert callable(journal_intent)
    assert callable(apply_authorized_mutation)
    assert callable(require_authorized_journal)
    assert callable(AgiflowStateSteward)
    assert IssuedEvidence is not None
    assert CloseGrant is not None
