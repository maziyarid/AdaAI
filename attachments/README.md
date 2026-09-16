# Ada Context Core v0.1.0

Authoritative, self-hosted memory and task-state service for Ada/Qalam and all Maziyar-controlled agents.

## Goal

Make critical memory deterministic and current. Every task bootstraps a context pack before execution. Mandatory memory is loaded by exact scope/priority/status, not by semantic similarity. Semantic retrieval is optional enrichment.

## Core guarantees

- PostgreSQL is the source of truth.
- Active canonical records supersede older records without deleting history.
- P0/P1 memories are loaded deterministically for matching global/project/site/task scopes.
- Project state is separate from durable memory.
- Every context pack has a version, hash, and signed receipt.
- Every scheduled run has an idempotency key, lifecycle state, events, and audit trail.
- External memories (XMemo/Engram) are mirrors only, never authoritative.
- Production mutations should require a valid, fresh context receipt.

## Phase 1 scope

This release intentionally does NOT include model inference or pgvector. It establishes the reliable memory/state foundation first. Vector search can be added after the deterministic layer is proven.

## Suggested endpoint

`https://mcp.maziyarid.com/context-mcp`

Qalam should call Context Core internally during `qalam_bootstrap`.

## Local install outline

1. Install PostgreSQL 16+ and create database/user.
2. Apply `sql/001_schema.sql`.
3. Create Python venv and install `app/requirements.txt`.
4. Configure environment variables shown in `app/.env.example`.
5. Run `uvicorn app.main:app --host 127.0.0.1 --port 8791`.
6. Install `systemd/ada-context-core.service` after adjusting paths/user.
7. Put the service behind the existing authenticated MCP/OAuth gateway; do not expose the internal port directly.

## Bootstrap flow

```text
agent/task starts
  -> POST /v1/bootstrap
  -> exact global/project/site/task mandatory memory
  -> current project state
  -> optional contextual search later
  -> signed context receipt
  -> task may execute
  -> before consequential mutation: POST /v1/receipts/validate
```

See `docs/ACCURACY-CONTRACT.md` for how routine actions become trustworthy.
