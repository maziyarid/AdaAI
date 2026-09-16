# Research synthesis applied to v0.2

The multi-agent research converged on these implementation decisions:
1. identity/memory/policy live outside model weights;
2. execution accuracy comes from deterministic authorization + independent verification, not a larger model;
3. scoped dependency versions replace a global revision;
4. HMAC is limited to a shared-secret trust domain; asymmetric signatures are the remote-worker path;
5. backups/PITR/restore drills are part of memory correctness;
6. scraped content is hostile/untrusted input until reviewed;
7. the production VPS should host control/state services, not a serious 4B+ inference worker;
8. wrap the existing Mistral worker before replacing it;
9. shadow mode and one canary precede fan-out;
10. pgvector and local model selection are deliberately deferred.

This package implements the Phase-1 subset of those conclusions.
