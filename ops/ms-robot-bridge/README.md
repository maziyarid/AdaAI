# Ada to Ms Robot Bridge

Canonical product name: Ms Robot. The maziyarid/Canopy repository name remains a historical identifier until source recovery and reconciliation are complete.

Ms Robot is the operations, data and UI hub. Ada is the governed intelligence and orchestration layer.

Ms Robot may send versioned authenticated events, present Ada outcomes and evidence, and supply analytics or inquiry context by reference. Ms Robot may not become a second scheduler or lease authority, write Ada runtime databases directly, invoke arbitrary shell or SQL, mint Ada approvals or receipts, or treat an LLM response as proof of a live action.

Ada validates and deduplicates events, routes them through deterministic policy, requests approval when needed, and returns an evidence-backed ada.outcome.v1 envelope.

Transport should be private or loopback where possible. Secrets remain in service-owned environment or secret files and never enter Git, Agiflow, ordinary logs or event payloads. HMAC-SHA256 uses canonical JSON, a minimum 32-byte key, a maximum 300-second event skew and stable event plus idempotency identifiers.

Linking sequence:
1. Reconcile Ms Robot source under AAX-42.
2. Implement this exact event envelope in the Ms Robot Event Router under AAX-44.
3. Put the bridge behind private service authentication.
4. Run shadow mode first with no consequential writes.
5. Verify replay, stale signature, permission isolation, audit, outage and recovery.
6. Enable selected action families only through existing Ada policy and approval gates.

No direct database coupling is required.
