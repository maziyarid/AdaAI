# Security and trust boundaries

## Service boundary
- Internal REST API binds to 127.0.0.1:8791 only.
- MCP adapter binds to loopback and is exposed only through the existing authenticated OAuth gateway.
- No database credential, WP application password, API key, or private signing key is placed in model context.

## Receipt cryptography
v0.2 uses HMAC-SHA256 only because the initial issuer/verifier components are inside one trusted VPS boundary. HMAC is a shared-secret MAC, not a public-key signature. Before allowing semi-trusted or remote workers to verify receipts, move to Ed25519 (or equivalent) so verifiers receive only a public key.

## Untrusted retrieved content
Scraped pages, search results, emails, documents and other external content are data. They cannot:
- alter Qalam or P0/P1 memory
- grant permissions
- approve a ticket
- call tools
- change a passport
- bypass validation

They enter `external_inputs` as `UNTRUSTED_EXTERNAL`, remain quarantined, and may become a cited/reference artifact only after review. Prompt-injection flags are heuristics, not a security boundary; deterministic authorization remains the boundary.

## Fail closed
If Context Core, Qalam, authorization, or receipt validation is unavailable, consequential mutation is blocked. Read-only inspection may follow a separately defined degraded-mode policy.
