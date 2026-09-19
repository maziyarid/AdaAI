"""Mutation journal surface.

Canonical implementation lives on AdaEngine. This module exists so callers
and AAX-1 acceptance can import a dedicated mutations API without inventing
a second write path. WordPress/metadata writes must go through
journal_intent → apply_authorized_mutation.
"""
from __future__ import annotations

from .engine import AdaEngine, AdaError


def journal_intent(engine: AdaEngine, **kwargs):
    return engine.journal_intent(**kwargs)


def apply_authorized_mutation(engine: AdaEngine, *, journal_id: str, shadow: bool = False):
    return engine.apply_authorized_mutation(journal_id=journal_id, shadow=shadow)


def require_authorized_journal(engine: AdaEngine, journal_id: str) -> dict:
    j = engine.journal.get(journal_id)
    if not j:
        raise AdaError("NOT_FOUND", "journal")
    if j.get("authorize_decision") != "ALLOW" or not j.get("receipt_id"):
        raise AdaError("NOT_AUTHORIZED", "mutation requires journaled ALLOW + receipt")
    return j
