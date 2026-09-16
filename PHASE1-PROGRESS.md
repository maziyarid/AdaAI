# Phase 1 reliability progress log

## 2026-09-16 — binding hardenings (post-Greptile)

**Session:** continue AdaAI Phase 1 reliability work (no VPS).

### Done this session
- Hardened `authorize()`: passport must belong to `agent_id`; receipt must match agent, task_type, site, payload_hash (when bound), mutation class, and passport_id.
- Hardened `request_approval()`: ticket site/task must stay inside receipt scope (`SCOPE_MISMATCH` otherwise).
- Hardened `consume_approval()`: if ticket has `snapshot_hash`, caller must supply matching hash (`SNAPSHOT_REQUIRED` / `SNAPSHOT_MISMATCH`). Fail-closed on omit.
- Hardened `journal_intent()`: requires prior `authorize()` decision ALLOW or ESCALATE; ESCALATE requires CONSUMED approval ticket bound to tool/site/payload.
- Hardened `apply_authorized_mutation()`: refuses journals lacking authorization evidence.
- Added 6 regression tests for the bypasses above.
- **28 pytest cases passing** (was 24).

### Still blocked (unchanged)
1. No VPS / SentinelX access from this sandbox → cannot import `/opt/maziyar-control-core`, capture systemd units/env names, or dump live MariaDB schema.
2. Production SQL not applied (correct: needs backup + restore drill + human approval).
3. Live Teznevise canary not run (correct: needs explicit human approval after shadow evidence).

### Explicit non-actions
- Did not restore `.grok` scaffold.
- Did not install local LLM.
- Did not deploy PostgreSQL or a second scheduler.
- Did not claim production deployment.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.
