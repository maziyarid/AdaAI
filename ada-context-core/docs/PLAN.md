# Build plan

## Milestone 0 — production protection
- VPS resource preflight
- current database/backup inventory
- MCP tool inventory and side-effect classification
- emergency kill switch
- no unrestricted production mutation

## Milestone 1 — Context Core v0.2
- PostgreSQL schema
- deterministic memory bootstrap
- scoped versions / dependency receipts
- project state
- task journal/idempotency
- agent passports + tool registry
- authorization
- durable approvals
- untrusted external-input quarantine
- audit
- backup/PITR + restore drill
- private REST + authenticated MCP adapter

## Milestone 2 — canonical migration
Import only reviewed, current P0/P1 records first. Do not bulk-import raw conversations. Establish project state for active lanes.

## Milestone 3 — Mistral shadow
Wrap one existing Mistral scheduled workflow. No production write. Generate AdaEval traces and measure target/tool/schema/canonical accuracy.

## Milestone 4 — one canary
Enable one reversible low-risk operation. Verify independently.

## Milestone 5 — bounded production
Gradually expand passports, batch size and task types based on measured failure modes.

## Milestone 6 — semantic recall
Add FTS/pgvector only after deterministic memory is proven.

## Milestone 7 — local inference
Benchmark verified open-weight candidates on the same AdaEval suite using a separate inference machine. Model registry requires official model card/license hashes plus locally measured peak memory and tool-call accuracy.
