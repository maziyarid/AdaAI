# Phase 1 reliability progress log

## 2026-09-16 — restore engine + binding hardenings (session continue)

**Session:** continue AdaAI Phase 1 reliability work (no VPS).

### Done this session
- **Restored** `ada-reliability/src/ada_reliability/engine.py` from placeholder (was syntactically invalid / unimportable).
- **Restored** `ada-reliability/tests/test_phase1_contracts.py` from placeholder.
- Full deterministic engine: bootstrap, scoped receipts (HMAC + alg/key_id), passports, `authorize()` fail-closed, approvals (no self-grant, one-time consume, snapshot-bound), mutation journal (ALLOW-only, idempotent), independent verify, ZWNJ, external quarantine, shadow mode.
- Binding hardenings: passport\u2194agent, receipt\u2194agent/task/site/payload, journal requires ALLOW, apply refuses unbound, approval cannot escape receipt site, snapshot omit fails closed.
- **27 pytest cases passing** locally (16 handoff contracts + binding extras + shadow/HMAC/AI-P0).
- VPS still unavailable — no import of `/opt/maziyar-control-core`, no production SQL, no live canary.

### Still blocked
1. No VPS/SentinelX → cannot import `/opt/maziyar-control-core`.
2. Production SQL not applied (backup + restore drill + approval required).
3. Live Teznevise canary not authorized.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.

## 2026-09-16 — binding hardenings (post-Greptile) [prior]

**Session:** continue AdaAI Phase 1 reliability work (no VPS).

### Done this session
- Hardened authorize/approval/journal bindings (fail-closed).
- Added regression tests for Greptile findings.
- Updated BLOCKERS.md.

### Known issue (resolved this session)
A tool-argument size mishap temporarily replaced `engine.py` / `test_phase1_contracts.py` on the branch with placeholders. **Restored and verified 27/27 green.**
