# AdaAI

AdaAI is Maziyar's provider-independent private agent control plane. Its durable identity lives outside model weights: authoritative context, Qalam policy, bounded tools, durable task state, independent verification, and audit history.

## Current milestone

**Phase 1: reliability before local inference.**

We are deliberately proving memory, authorization, recovery, and execution correctness before selecting a permanent local LLM.

Core rule:

> Models propose. Deterministic code authorizes and executes. Independent validators prove the live result.

## Repository layout

- `ada-context-core/` — authoritative PostgreSQL memory, task state, scoped receipts, approval tickets, mutation journal, MCP adapter, backup/recovery tooling, tests.
- `docs/GOOGLE-CLOUD-NO-BILLING.md` — Google services that can help development without requiring a billing account/payment method, plus exclusions.
- `docs/VPS-DEPLOYMENT.md` — conservative production deployment sequence for the existing VPS.
- `docs/CI.md` — current test/CI status and the GitHub-hosted-runner blocker.
- `AGENTS.md` — mandatory contributor/agent operating rules.

The original Grok export is preserved on branch `archive/grok-export-2026-09-16` and is not part of the production architecture.

## What is intentionally not here

No Grok App Builder scaffold, preview branding, Vercel demo shell, generated game/auth skills, screenshots, attachments, duplicate artifacts, frontend placeholder, local LLM runtime, pgvector, or unrestricted production automation.

## Deployment target

The first VPS deployment should run only Context Core:

```text
Qalam / workers
    -> authenticated /context-mcp
    -> Context MCP adapter
    -> 127.0.0.1:8791 private REST service
    -> PostgreSQL authoritative state
```

Recommended server path: `/srv/ada/context-core`.

Do not expose port `8791` publicly.

## First production proof

1. VPS preflight and backup/restore readiness.
2. Deploy PostgreSQL + Context Core.
3. Seed a small reviewed P0/P1 memory set.
4. Verify deterministic bootstrap and stale-context rejection.
5. Wrap the existing Mistral worker in shadow mode.
6. Run one low-risk Teznevise canary with independent live verification.
7. Only after that, benchmark local models with AdaEval.

## Tests

The Context Core contract suite currently passes locally. Until GitHub-hosted Actions can start jobs for this repository, use the commands documented in `docs/CI.md` and `ada-context-core/README.md`.

See `ada-context-core/README.md` and `ada-context-core/docs/PLAN.md` for implementation details.
