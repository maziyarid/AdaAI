# Phase-1 blocker report

Status: **engine + AAX-12 steward + AAX-15 failed-run outbox in-repo (lease-expire CAS + retry budget at `2dd1ffb`). Secret-free AAX-3 host inventory captured 2026-09-18T22:15Z and reconfirmed 2026-09-19. Production SQL not applied. Live MariaDB dump and systemd ActiveState still gated.**

## Blocker 1 — Ada-readonly SSH works; MariaDB / ActiveState still gated (updated 2026-09-18T22:15Z)

**Resolved this session:** viewer profile `grok-ada-readonly` can `pwd`, `ls /opt`, and `cat` the control-core unit. `/opt/maziyar-control-core` exists on `server.maziyarid.com`. Inventory is in `docs/AAX3-LIVE-BASELINE.md`.

**Still blocked:** current viewer classifier refuses `ls`/`cat`/`stat`/`systemctl`/`sha256sum` on this readOnly profile (stricter than the 22:15Z capture). `state/` and `tools/` remain mode-denied. No `mysqldump --no-data`. AAX-4 `/health` 401 caller and AAX-5/AAX-7 live table proofs therefore remain open. Do not clear `readOnly` to get those commands.

**Do not use the Content/Royadarman host as Ada.** That host still lacks `/opt/maziyar-control-core`.

**Next privileged/mazcontrol steps (no secrets in git):**

1. `mysqldump --no-data` control-core schema (table names / indexes only).
2. `systemctl status maziyar-control-core.service` (ActiveState only).
3. Confirm presence/absence of `ada_*` vs live `pd_*`.
4. Identify the localhost `/health` 401 caller (AAX-4) without weakening auth.

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
- Job/schedule/lease regression tests against documented PRESERVED_BEHAVIOR.
- HMAC receipts carry `signature_alg` + `key_id`.
- Fail-closed authorize / approvals / journal / ZWNJ / shadow mode.
- AAX-12 in-repo Agiflow steward: mapping, HMAC-issued Review evidence, one-time human Done grant, human-edit conflict, outbox replay of ids only, no runtime writes, no ClickUp dependency. Caller-constructed evidence is rejected (`UNKNOWN_EVIDENCE`).
- AAX-15 in-repo failed-run outbox (distinct from AAX-12 projection outbox): parked vs retryable vs inflight vs dead-letter, `replay=UNAVAILABLE` when persist fails, Agiflow handoff through the steward, no WordPress/packet mutation from the outbox itself. In-process restart simulation is not VPS persistence.
- Engine + steward pytest green from the working tree.
