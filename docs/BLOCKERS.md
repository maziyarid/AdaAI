# Phase-1 blocker report

Status: **engine + AAX-12 steward + AAX-15 failed-run outbox + AAX-8 in-repo shadow pipeline. Live `control_core.py` imported 2026-09-19T06:42Z (65370 bytes, sha256 of captured bytes `aec6639acf761dfb01a72feb670b4d841c25fb1e8000abdea41bca0dcf4a94f3`). Greptile independently reviewed `d7e41a6` at 5/5 (no outstanding P0/P1). AAX-4 `/health` 401 caller identified from live source. mazcontrol read-only helper is in-repo, not installed (`ada-inspect` ENOENT 2026-09-19T07:10Z). Production SQL not applied. Live MariaDB `SHOW TABLES` and systemd ActiveState still gated.**

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

- Additive MariaDB `ada_*` SQL written, dialect-reviewed, not applied. Includes `005_ada_agiflow_projection.sql` and `006_ada_failed_run_outbox.sql`.
- `path_hash` uniqueness and one-ACTIVE release constraint in SQL.
- Job/schedule/lease regression tests against documented PRESERVED_BEHAVIOR **and** the imported live source snapshot.
- HMAC receipts carry `signature_alg` + `key_id`.
- Fail-closed authorize / approvals / journal / ZWNJ / shadow mode.
- AAX-12 in-repo Agiflow steward: mapping, HMAC-issued Review evidence, one-time human Done grant, human-edit conflict, outbox replay of ids only, no runtime writes, no ClickUp dependency. Caller-constructed evidence is rejected (`UNKNOWN_EVIDENCE`).
- AAX-15 in-repo failed-run outbox (distinct from AAX-12 projection outbox): parked vs retryable vs inflight vs dead-letter, `replay=UNAVAILABLE` when persist fails, Agiflow handoff through the steward, no WordPress/packet mutation from the outbox itself. In-process restart simulation is not VPS persistence.
- Engine + steward pytest green from the working tree.
