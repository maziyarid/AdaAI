# Phase-1 blocker report

Status: **engine + AAX-12 steward + AAX-15 failed-run outbox in-repo (P1s restored at `39835da`). Production SQL not applied. Live control-core import still blocked this session.**

## Blocker 1 — Ada-readonly VPS SSH profile is down (updated 2026-09-19)

**Affected:** freeze/import of `/opt/maziyar-control-core`, live MariaDB schema capture, systemd unit dump, env-name capture (AAX-3), `/health` 401 probe source (AAX-4), live `pd_*` vs `ada_*` reconciliation (AAX-7).

**This session did have VPS MCP connectors.** That is not the same as a live shell on the control-core host.

**Evidence this session (read-only, no secrets):**
- `Content` profile `grok-royadarman` is **connected**. `/opt` on that host is `cpanel`, `royadarman-admin-mcp`, `sentinelx-cloud-core`. `/opt/maziyar-control-core` **does not exist** there (`ls` exit 2). `/srv` is `community-mcp`. This is the Royadarman/content host, not Ada control-core.
- `Eqialise` profile `grok-ada-readonly` (`mistralops@127.0.0.1:22`, role=viewer) is **disconnected**. `read-command` returned nginx HTTP 502; `run-command ls /opt` timed out; no sessions. This is the intended Ada host.
- Do not treat the connected Content host as the control-core baseline. Do not rewrite history as “VPS was always unavailable”; MCP is configured, Ada SSH is not usable right now.

**Safest next step:** restore `grok-ada-readonly` SSH, then from that viewer profile only:

1. `ls` / `find` `/opt/maziyar-control-core` excluding `.env` / secrets.
2. `mysqldump --no-data` the control-core schema (table names / indexes only).
3. `systemctl cat maziyar-control-core.service` (and Mistral worker unit).
4. List environment **names** only.
5. Confirm presence/absence of `ada_*` vs live `pd_worker_runs` / `pd_outbox`.
6. Identify the localhost `/health` 401 caller (AAX-4) without weakening auth.

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
