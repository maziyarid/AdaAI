# AdaAI

AdaAI is Maziyar's provider-independent private agent control plane. Its durable identity lives outside model weights: authoritative context, Qalam policy, bounded tools, durable task state, independent verification, and audit history.

## Current milestone

**Phase 1: reliability before local inference.**

We are deliberately proving memory, authorization, recovery, and execution correctness before selecting a permanent local LLM.

Core rule:

> Models propose. Deterministic code authorizes and executes. Independent validators prove the live result.

## Canonical docs

- `docs/ARCHITECTURE.md` — target architecture reconciled with the live VPS.
- `docs/ROADMAP.md` — phased implementation roadmap and immediate build backlog.
- `docs/GROK-BUILD-HANDOFF.md` — complete implementation mission for Grok Build.
- `docs/VPS-DEPLOYMENT.md` — deployment notes for the existing VPS.
- `docs/GOOGLE-CLOUD-NO-BILLING.md` — optional Google services that may help development without becoming authoritative dependencies.
- `docs/CI.md` — test/CI status.
- `AGENTS.md` — mandatory contributor/agent operating rules.

## Live baseline

The production VPS already has a working durable control plane. Ada must evolve it rather than create a second source of truth.

Verified baseline on 2026-09-16:

```text
maziyar-control-core.service
    -> 127.0.0.1:8770
    -> MariaDB 10.11
    -> durable jobs / schedules / leases / retries / DLQ / audit / snapshots

maziyar-mistral-worker.service
    -> 127.0.0.1:9102
    -> Mistral inference/workflow bridge
    -> existing control-core durable job/schedule API
```

The current production host is about 4 vCPU / 3.6 GiB RAM with no NVIDIA GPU runtime. It remains the control/memory plane, not the heavy inference node.

## Repository layout

- `ada-context-core/` — earlier reliability prototype/reference implementation. Its contracts are useful, but its PostgreSQL assumptions must be reconciled with the live MariaDB control core before deployment.
- `docs/` — canonical architecture, roadmap, deployment and handoff documentation.
- `AGENTS.md` — mandatory contributor/agent contract.

The original Grok export is preserved on branch `archive/grok-export-2026-09-16` and is not part of the production architecture.

## Qalam and Persian writing

Qalam and the Persian writing stack are mandatory Ada infrastructure, not optional prompt attachments.

The target skill registry must preserve and version:

- Qalam router;
- Art of Writing Bible v1.4 and future releases;
- Iranian Persian (`fa-IR`) UX writing rules;
- `fa-IR` product lexicon;
- academic/methodology/service overlays;
- British-English and medical/fact-check overlays;
- site-specific rules including Teznevise zero-U+200C;
- approved examples and evaluation cases.

Writing tasks must carry Qalam/overlay release dependencies in their Context receipt.

## What is intentionally not here

No Grok App Builder scaffold, preview branding, Vercel demo shell, generated game/auth skills, screenshots, placeholder frontend, local LLM runtime, pgvector, or unrestricted production automation.

## First production proof

1. Import/freeze the live MariaDB control-core baseline into the repo.
2. Add tests that preserve its current durable queue/scheduler behavior.
3. Extend it additively with scoped memory/context/authorization/approval entities.
4. Mirror Qalam and the full writing stack into Ada's versioned skill registry.
5. Wrap one existing Mistral scheduled task in shadow mode.
6. Run one low-risk Teznevise canary with independent live verification.
7. Only after the contract is proven, benchmark local/hosted models with AdaEval.

## Tests

The earlier Context Core prototype contract suite passed locally, but the next milestone is integration against the actual live MariaDB-backed control-plane design. Do not treat prototype tests as proof of production readiness.

See `docs/ROADMAP.md` for the canonical build order.
