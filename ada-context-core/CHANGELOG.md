# Changelog

## 0.2.0

- Replaced global-only context revision with scoped dependency versions.
- Added `receipt_dependencies` and exact freshness validation.
- Added signature algorithm/key ID fields; documented HMAC trust boundary and Ed25519 upgrade path.
- Added agent passports and tool registry.
- Added deterministic authorization endpoint.
- Added durable approval tickets/events with payload/snapshot/receipt binding.
- Added mutation journal and snapshot metadata.
- Added parent/child tasks, leases, retry budgets, and idempotency.
- Added untrusted external-input quarantine and explicit non-promotion rule.
- Added backup run/mirror run tables and recovery scripts/docs.
- Added model registry as metadata only; no model inference in Phase 1.
- Clarified MCP adapter vs private REST service.
- Added shadow-mode Mistral pilot contract and AdaEval seed cases.
- Kept pgvector and semantic retrieval deferred.
