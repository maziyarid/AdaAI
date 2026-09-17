"""Phase-1 world seed for tests and local demos."""
from __future__ import annotations

from typing import Optional

from .engine import AdaEngine
from .models import AgentPassport, Priority, Provenance, TEZNEVISE_SITE, ToolSpec


def seed_phase1(engine: Optional[AdaEngine] = None) -> AdaEngine:
    """Seed a minimal Phase-1 world for tests and local demos."""
    eng = engine or AdaEngine()

    eng.seed_memory(
        canonical_key="ada.constitution.fail_closed",
        record_type="policy",
        scope_type="global",
        scope_id="*",
        priority=Priority.P0,
        provenance=Provenance.CANONICAL.value,
        title="Fail closed",
        content="Missing/expired/stale context, unknown resource, or failed verification blocks mutation.",
        authority="human",
    )
    eng.seed_memory(
        canonical_key="ada.constitution.models_propose",
        record_type="policy",
        scope_type="global",
        scope_id="*",
        priority=Priority.P0,
        provenance=Provenance.CANONICAL.value,
        title="Models propose",
        content="Models propose. Deterministic code authorizes. Independent validators prove the live result.",
        authority="human",
    )

    eng.register_policy_release(
        "qalam",
        "2026.09.16",
        content="# Qalam router\nMandatory writing policy.\n",
        path="skills/qalam/SKILL.md",
    )
    eng.register_policy_release(
        "art-of-writing-bible",
        "2.0.0",
        content="# Art of Writing Bible\nversion: 2.0.0\n",
        path="skills/art-of-writing-bible/SKILL.md",
    )
    eng.register_policy_release(
        "fa-ir-ux",
        "1.0.0",
        content="# fa-IR UX writing\n",
        path="skills/fa-ir-ux/SKILL.md",
    )
    eng.register_policy_release(
        "teznevise-zwnj",
        "1.0.0",
        content="# Teznevise: zero U+200C (ZWNJ) in published content.\n",
        path="skills/teznevise-zwnj/SKILL.md",
    )

    eng.seed_memory(
        canonical_key="site.teznevise.zwnj",
        record_type="policy",
        scope_type="site",
        scope_id=TEZNEVISE_SITE,
        priority=Priority.P1,
        provenance=Provenance.CANONICAL.value,
        title="Teznevise ZWNJ ban",
        content="Published Teznevise content must not contain U+200C.",
        authority="human",
    )

    eng.register_passport(
        AgentPassport(
            id="passport-mistral-1",
            agent_id="mistral-worker",
            task_type="*",
            allowed_sites=[TEZNEVISE_SITE, "example.test"],
            allowed_tools=[
                "read_post",
                "update_post_metadata",
                "apply_approved_change",
                "verify_live",
            ],
            allowed_mutation_types=["update_post_metadata", "harmless_format"],
            max_batch_size=1,
            deletion_permission=False,
            policy_change_permission=False,
            approval_mandatory=False,
            approval_classes=["deletion", "bulk_publish"],
        )
    )

    eng.register_tool(ToolSpec("read_post", "read", requires_receipt=True))
    eng.register_tool(
        ToolSpec(
            "update_post_metadata",
            "mutate",
            mutation_type="update_post_metadata",
            requires_receipt=True,
            requires_snapshot=True,
            requires_live_verification=True,
        )
    )
    eng.register_tool(
        ToolSpec(
            "apply_approved_change",
            "mutate",
            mutation_type="harmless_format",
            requires_receipt=True,
            requires_snapshot=True,
            requires_live_verification=True,
        )
    )
    eng.register_tool(ToolSpec("verify_live", "read", requires_receipt=False))
    eng.register_tool(
        ToolSpec(
            "delete_post",
            "delete",
            mutation_type="deletion",
            requires_receipt=True,
            requires_snapshot=True,
        )
    )
    eng.register_tool(
        ToolSpec(
            "change_policy",
            "policy",
            mutation_type="policy_change",
            requires_receipt=True,
        )
    )

    eng.set_live(TEZNEVISE_SITE, "post-1", "سلام دنیا", meta={"title": "Hello"})
    eng.set_live("example.test", "post-2", "Hello world", meta={"title": "Example"})

    return eng
