"""Phase-1 world seed.

Canonical implementation lives in engine.seed_phase1 (dict-based contract
used by the 27+ pytest cases). This module re-exports it for callers that
prefer `from ada_reliability.seed import seed_phase1`.
"""
from __future__ import annotations

from .engine import seed_phase1

__all__ = ["seed_phase1"]
