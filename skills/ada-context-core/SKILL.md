---
name: ada-context-core
description: >
  Phase 1 reliability foundation for Ada/Qalam: PostgreSQL is authoritative
  memory and task-state. Bootstrap loads ACTIVE P0/P1 by exact scope. Receipts
  HMAC-SHA256 with scoped versions. External text is quarantined. No pgvector
  in this phase. Database ON, auth OFF in this preview.
version: 0.2.0
date: 2026-09-16
---

# Ada Context Core — Phase 1

Authoritative memory is PostgreSQL, not chat history and not embeddings.

Python source of truth for later VPS deploy: `/workspace/ada-context-core`.
This app ports schema + bootstrap + receipts + authorize + quarantine so the
database is already established.

## Guarantees

1. Every consequential task bootstraps a context pack.
2. Mandatory memory is loaded by exact global / project / site / task_type / agent.
3. Project state is a separate table from durable memory.
4. Receipts record scoped dependency versions, memory checksums, Qalam release, passport.
5. HMAC-SHA256 is preview-grade here (`signature_alg` + `key_id` so Ed25519 can replace it).
6. Scraped text is `UNTRUSTED_EXTERNAL` and cannot self-promote to canonical policy.
7. Mutating tools require a passport and, when marked, a fresh receipt. Default is DENY/ESCALATE.
8. No pgvector. No model inference. No bulk delete. No personal rows (auth is off).

## Preview endpoints (TanStack server functions)

- `adaBootstrap` — POST pack
- `adaValidateReceipt`
- `adaListMemory`
- `adaAuthorize`
- `adaQuarantine`

UI: `/ada`.

## What this is not

- Not a second writing voice. Qalam still writes.
- Not permission to publish teznevise.ir.
- Not production HMAC. Set `ADA_RECEIPT_HMAC_KEY` (≥32) off-workspace for real deploy.
