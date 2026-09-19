# Phase-1 blocker report

Status: **engine + AAX-12 steward + AAX-15 failed-run outbox + AAX-8 in-repo shadow pipeline (HMAC covers the full evidence record except `evidence_hmac`; bound `live_job_id` never grants production mutation families; unauthorised networked adapter reads fail closed without HTTP, including hostname aliases, ControlCoreAdapter subclasses, and wrappers; path/URL job ids never reach GET /jobs/{id}; independent postcondition/rollback stages do not apply, complete, or journal a write intent; optional read-only `adapter.get_job` binds secret-free job shape and never claims live Mistral). Live `control_core.py` imported 2026-09-19T06:42Z (65370 bytes, sha256 of captured bytes `aec6639acf761dfb01a72feb670b4d841c25fb1e8000abdea41bca0dcf4a94f3`). AAX-7 isolated **MariaDB** rehearsal of `001`–`006` ran on disposable skip-networking 10.11.11 (protected jobs/schedules unchanged; rollback restored baseline; not VPS SHOW TABLES). mazcontrol read-only helper is in-repo, not installed (`ada-inspect` ENOENT 2026-09-19T09:14Z). Production SQL not applied. Live MariaDB `SHOW TABLES` and systemd ActiveState still gated.**

## Blocker 1 — Ada-readonly SSH works; MariaDB / ActiveState still gated (updated 2026-09-18T22:15Z)

**Resolved this session:** viewer profile `grok-ada-readonly` can `pwd`, `ls /opt`, and `cat` the control-core unit. `/opt/maziyar-control-core` exists on `server.maziyarid.com`. Inventory is in `docs/AAX3-LIVE-BASELINE.md`.

**Still blocked:** `systemctl` ActiveState/SubState and host `sha256sum` remain refused on this readOnly profile. `state/` and `tools/` remain mode-denied. `clickup_state_steward.py` is mode-denied. No `mysqldump --no-data`. Live `ada_*` vs `pd_*` **table list** therefore remains open (source has zero `ada_*` / `pd_worker_runs` / `pd_outbox` names; that is not `SHOW TABLES`). Do not clear `readOnly` to get those commands. AAX-4 `/health` 401 caller is identified from live `control_core.py` (`BLACKOUT_SENTINEL` / `HEALTH_TARGETS` expects 401 as healthy); do not weaken auth.

**Do not use the Content/Royadarman host as Ada.** That host still lacks `/opt/maziyar-control-core`.

**Next privileged/mazcontrol steps (no secrets in git):**

1. Human-install `ops/mazcontrol-readonly/ada-inspect` as
   `/usr/local/bin/ada-inspect` and the matching sudoers snippet.
   Allowlist that single binary on `grok-ada-readonly`. Keep `readOnly`.
2. `ada-inspect units` (ActiveState only) and `ada-inspect hashes`.
3. `ada-inspect tables` to confirm live `ada_*` vs `pd_*` (source has
   no `ada_*` / `pd_worker_runs` / `pd_outbox` names).
4. Optional later AAX-4 code change: add no-secrets `/livez` and point
   `HEALTH_TARGETS` at it. Do **not** strip `CONTROL_API_TOKEN` from
   `/health`.

## Blocker 2 — production canary not authorized

Do not run a live Teznevise mutation without explicit human approval after shadow evidence (AAX-8). Do not treat the in-process AAX-12 canary as a live board canary.

## Blocker 3 — Bible / router versions are independent

Do not collapse router 1.1.0, Bible 2.0.0, eval pack 1.3.0, or the historical 1.4.0 docs label into one number. `skills/qalam/RELEASE.json` is the pointer.

## Blocker 4 — GitHub Contents API / payload size (resolved)

Full `engine.py` + `test_phase1_contracts.py` recovered from `2c5e723` and pushed with git, not the Contents API. Placeholders must not return.

## Blocker 5 — GitHub Actions may still not start

`docs/CI.md` records that hosted runners previously failed before any step. `.github/workflows/ada-reliability.yml` is added anyway. Equivalent proof: clean venv `pip install -e ada-reliability` + pytest.

## Non-blockers (done)

- Additive MariaDB `ada_*` SQL written, dialect-reviewed, **isolated skip-networking rehearsal passed** (10.11.11; not applied to production). Includes `005_ada_agiflow_projection.sql` and `006_ada_failed_run_outbox.sql`. `release` is quoted as a reserved word.
- `path_hash` uniqueness and one-ACTIVE release constraint in SQL.
- Job/schedule/lease regression tests against documented PRESERVED_BEHAVIOR **and** the imported live source snapshot.
- HMAC receipts carry `signature_alg` + `key_id`.
- Fail-closed authorize / approvals / journal / ZWNJ / shadow mode.
- AAX-12 in-repo Agiflow steward: mapping, HMAC-issued Review evidence, one-time human Done grant, human-edit conflict, outbox replay of ids only, no runtime writes, no ClickUp dependency. Caller-constructed evidence is rejected (`UNKNOWN_EVIDENCE`).
- AAX-15 in-repo failed-run outbox (distinct from AAX-12 projection outbox): parked vs retryable vs inflight vs dead-letter, `replay=UNAVAILABLE` when persist fails, Agiflow handoff through the steward, no WordPress/packet mutation from the outbox itself. In-process restart simulation is not VPS persistence.
- Engine + steward pytest green from the working tree.
