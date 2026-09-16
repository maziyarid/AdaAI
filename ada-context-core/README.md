# Ada Context Core v0.2.0 — Phase 1 Reliability Foundation

Authoritative, self-hosted memory, task-state, and execution-authorization service for Ada/Qalam and all Maziyar-controlled agents.

## Why this release exists

v0.1 established the right direction but had four design weaknesses: one global context revision, HMAC described too broadly as a signature, no first-class recovery/PITR contract, and no explicit quarantine boundary for scraped/external text. v0.2 corrects those before production deployment.

## Phase 1 objective

Prove this statement before choosing or hosting a local LLM:

> Every consequential task receives the current, scope-correct authoritative memory; every mutation is independently authorized and journaled; stale context fails closed; results are verified independently; memory is recoverable after failure.

This release intentionally has **no pgvector and no model inference**. Semantic recall and local inference are later milestones.

## Architecture

```text
External clients / Qalam / workers
          |
          v
https://mcp.maziyarid.com/context-mcp   (authenticated MCP adapter)
          |
          v
127.0.0.1:8791                          (private Context Core REST API)
          |
          v
PostgreSQL                               (authoritative state)
```

The REST service is not an MCP server. The `mcp/` adapter is the MCP surface and must be placed behind the existing OAuth gateway. Port 8791 stays loopback-only.

## Core guarantees

- PostgreSQL is authoritative; XMemo/Engram are optional asynchronous mirrors only.
- P0/P1 memory is loaded deterministically by exact global/project/site/task/agent scopes.
- Context freshness uses **scoped dependency versions**, not one global counter.
- Receipts record the exact scope versions and project-state version loaded.
- HMAC-SHA256 is used only for the initial same-trust-boundary deployment. The receipt format carries `signature_alg` and `key_id` so Ed25519 can replace HMAC for semi-trusted remote workers.
- Project state is separate from durable memory.
- External/scraped material is stored as `UNTRUSTED_EXTERNAL` and cannot become canonical policy automatically.
- Mutating tool calls require deterministic authorization at the gateway/executor boundary.
- Approval tickets bind an exact payload hash, snapshot hash, receipt, and dependency hash; a bare `approved=true` is never enough.
- Every mutation has an idempotency key and journal record.
- Backups, WAL/PITR configuration, off-host copies, and restore drills are Phase 1 requirements.
- A model may propose; code decides; a separate verifier proves live postconditions.

## Recommended first deployment sequence

1. Run `scripts/preflight.sh` on the VPS. Do not modify existing MCP control-plane services.
2. Install PostgreSQL 16+ conservatively and apply `sql/001_schema.sql`.
3. Configure `app/.env.example` as `/etc/ada/context_core.env` (0600).
4. Install/start `ada-context-core.service` on `127.0.0.1:8791`.
5. Configure encrypted backup + WAL archive and run a restore drill.
6. Seed only a small set of known P0/P1 policies and one project working state.
7. Verify `/v1/bootstrap` returns exact deterministic memory and scoped dependencies.
8. Start the MCP adapter on loopback and route `/context-mcp` through the existing authenticated gateway.
9. Wrap the existing Mistral worker in **shadow mode**. It proposes; nothing is mutated.
10. After AdaEval/shadow results pass, perform one low-risk Teznevise canary; independently verify it; only then widen scope.

## What is deliberately deferred

- pgvector / semantic memory
- autonomous memory promotion
- unrestricted memory writes by agents
- local model serving
- model routing/fine-tuning
- bulk publishing
- destructive automation

## Tests

```bash
python -m compileall app mcp
pytest -q
```

Database integration tests require `ADA_TEST_DATABASE_URL` and are separate from the pure contract tests.

See:
- `docs/PLAN.md`
- `docs/MEMORY-CONTRACT.md`
- `docs/EXECUTION-CONTRACT.md`
- `docs/SECURITY.md`
- `docs/PILOT.md`
- `docs/RECOVERY.md`
