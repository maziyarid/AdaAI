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

- `ada-reliability/` — Phase-1 executable contract (bootstrap, receipts, authorize, approvals, journal, ZWNJ validator, Mistral shadow). Tests do not require MariaDB.
- `ada-reliability/sql/mariadb/` — additive `ada_*` tables for the live MariaDB instance.
- `runtime/control-core-baseline/` — client adapter + captured behavior. Live `/opt/maziyar-control-core` import is blocked until VPS access.
- `skills/qalam/` — versioned writing registry (router, fa-IR overlays, Teznevise ZWNJ).
- `skills/art-of-writing-bible/` — Bible 2.0.0 + history 1.0.0–1.3.0.
- `skills/persian-medical-human-writing/` — medical overlay.
- `ada-context-core/` — earlier PostgreSQL prototype. Reference only. Do not deploy.
- `docs/` — architecture, roadmap, runbooks, blockers, ADRs.

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

```bash
cd ada-reliability && python3 -m pytest tests -v
```

22 contract tests covering the 18 required Phase-1 cases passed on 2026-09-16. Prototype `ada-context-core` tests are not production proof.

See `docs/ROADMAP.md`, `docs/BLOCKERS.md`, `docs/MIGRATION-RUNBOOK.md`.

