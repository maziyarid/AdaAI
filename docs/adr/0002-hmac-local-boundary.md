# ADR 0002 — HMAC receipts inside one trust boundary

Status: accepted  
Date: 2026-09-16

v0.1 receipts use HMAC-SHA256 because issuer and verifier are the same Ada process (later the same VPS trust boundary).

Receipt envelope already includes:

- `signature_alg`
- `key_id`
- `receipt_id`, `task_run_id`, `agent_id`
- `issued_at`, `expires_at`
- scoped `dependencies`
- `allowed_mutation_classes`
- `payload_hash` / `context_hash`
- `signature`

When a semi-trusted GPU worker must verify receipts without minting them, replace HMAC with Ed25519. Workers receive only the public key. They never get the minting secret.
