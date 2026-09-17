# Phase 1 reliability progress log

## 2026-09-17 — continue: split engine, dialect review, job contracts

**Session:** continue AdaAI Phase 1 reliability work (no VPS).

### Done this session
- Reconfirmed local engine **33 pytest green** (27 contract + adapter + 4 job/schedule/lease regressions).
- Split engine into `models.py`, `engine.py`, `mutations.py`, `seed.py` so the package can be pushed in smaller files.
- Pushed `models.py` + `seed.py` to `phase1/reliability-layer`.
- Added `docs/MARIADB-DIALECT-REVIEW.md` (document-only; SQL not applied).
- Added `tests/test_live_job_contracts.py` for documented jobs/schedules/leases/retries/DLQ (no VPS call).
- Packaged restored sources as `ada-reliability-restored.zip` for a host that can `git add` the remaining large files.

### Still on the branch as placeholders until a git push of the zip contents
- `engine.py` (still placeholder on remote)
- `test_phase1_contracts.py` (still placeholder on remote)
- `mutations.py` (local only until pushed)

### Still blocked
1. No VPS/SentinelX → cannot import `/opt/maziyar-control-core`.
2. Production SQL not applied.
3. Live Teznevise canary not authorized.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.
