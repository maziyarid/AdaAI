# Phase 1 reliability progress log

## 2026-09-17 — AAX-1 restore + AAX-2 fail-closed bindings (Grok)

**Session:** Grok with GitHub + Agiflow. PR head before this commit: `66c850df9eacbd9c55e496d1d7bbd5fb104c52c2`.

### Evidence (do not treat older "33 pytest green locally" claims as completion)
- Remote `engine.py` and `test_phase1_contracts.py` were still placeholders at that SHA.
- Recovered the complete engine/tests from git history `2c5e723` (1075-line engine, 588-line contracts). Later "restore" commits did not actually land the blobs (GitHub Contents API size).
- Restored via `git checkout 2c5e723 -- …` then applied fail-closed hardenings. Push is a real git commit, not the Contents API.

### Done this session
- Restored `ada-reliability/src/ada_reliability/engine.py` and `tests/test_phase1_contracts.py`.
- Added `mutations.py` and `qalam_release.py`.
- Fail-closed: passport bound to agent + stored version; empty `allowed_sites` denies; receipt agent/task/site/payload/passport/mutation binding; approval stays inside receipt scope; snapshot required when ticket bound one; journal/apply require matching ALLOW + live receipt; policy receipts hash the ACTIVE asset bundle (real files when present), not a placeholder string.
- Authoritative Qalam pointer: `skills/qalam/RELEASE.json`. Router 1.1.0 and Bible 2.0.0 stay independent; eval pack 1.3.0 validates Bible 2.0.0.
- Overlay paths reconciled to `skills/qalam/fa-ir-overlays/*`. Loading plan is deterministic (router + Bible + every listed profile overlay + Bible companions).
- MariaDB: `path_hash` PK (no `path(191)` unique); one-ACTIVE unique generated column.
- Migration runbook precondition 5 now admits the bootstrap `INSERT IGNORE`.
- GitHub Actions workflow `.github/workflows/ada-reliability.yml` (may still be blocked by repo Actions policy; this session also ran a clean venv `pip install -e` + pytest).
- **43 pytest passed** from the working tree, including an isolated venv install/import.

### Production
- SQL not applied.
- No live Teznevise canary.
- This session has GitHub + Agiflow, not SSH to `/opt/maziyar-control-core`. AAX-3 remains blocked here even if another agent has VPS.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.

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
