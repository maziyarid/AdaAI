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

## 2026-09-17 — restore full engine + contract tests (no VPS)

**Session:** continue Phase 1 reliability (VPS still unavailable).

### Done this session
- Restored `ada-reliability/src/ada_reliability/engine.py` from last complete
  historical blob (`2c5e723` / `4f1fb06`, 1075 lines) after remote had only
  the `PLACEHOLDER_WILL_BE_REPLACED` stub.
- Restored `tests/test_phase1_contracts.py` (22 contract cases + helpers).
- Re-exported `seed_phase1` from `seed.py` so package imports stay coherent
  with the dict-based engine API used by tests.
- **28 pytest green** locally: 22 phase1 contracts + 2 adapter + 4 live
  job/schedule/lease regressions.
- Confirmed models.py remains valid dataclasses (supplementary shapes).
- Confirmed MariaDB dialect review and SQL remain document-only / not applied.
- No VPS import, no production SQL apply, no Teznevise canary.

### Still blocked
1. No VPS/SentinelX → cannot import `/opt/maziyar-control-core`.
2. Production SQL not applied (needs backup + restore drill + approval).
3. Live Teznevise canary not authorized.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.
