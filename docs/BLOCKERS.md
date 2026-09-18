# Phase-1 blocker report

Status: **engine + AAX-12 steward in-repo. HMAC-issued Agiflow evidence (Greptile P1). Production import and canary not executed.**

## Blocker 1 — no SSH/SentinelX from this Grok session

**Affected:** freeze/import of `/opt/maziyar-control-core`, live MariaDB schema capture, systemd unit dump, env-name capture, production shadow wrap (AAX-3), live Agiflow board canary (AAX-12 last AC).

**Evidence:** this session has GitHub and Agiflow connectors, not SSH. A PR comment claims VPS access exists for some agents; that is not the same as this session having a live shell on the host. Do not treat the old "no VPS anywhere" sentence as current, and do not treat this session as having imported the control core.

**Safest next step:** from an authorized VPS session (AAX-3):

1. `tar` `/opt/maziyar-control-core` excluding `.env` / secrets.
2. `mysqldump --no-data` the control-core schema.
3. `systemctl cat maziyar-control-core.service maziyar-mistral-worker.service`.
4. List environment **names** only.
5. Commit under `runtime/control-core-baseline/imported/` on this branch.

## Blocker 2 — production canary not authorized

Do not run a live Teznevise mutation without explicit human approval after shadow evidence (AAX-8). Do not treat the in-process AAX-12 canary as a live board canary.

## Blocker 3 — Bible / router versions are independent

Do not collapse router 1.1.0, Bible 2.0.0, eval pack 1.3.0, or the historical 1.4.0 docs label into one number. `skills/qalam/RELEASE.json` is the pointer.

## Blocker 4 — GitHub Contents API / payload size (resolved)

Full `engine.py` + `test_phase1_contracts.py` recovered from `2c5e723` and pushed with git, not the Contents API. Placeholders must not return.

## Blocker 5 — GitHub Actions may still not start

`docs/CI.md` records that hosted runners previously failed before any step. `.github/workflows/ada-reliability.yml` is added anyway. Equivalent proof: clean venv `pip install -e ada-reliability` + pytest.

## Non-blockers (done)

- Additive MariaDB `ada_*` SQL written, dialect-reviewed, not applied. Includes `005_ada_agiflow_projection.sql` (task map, outbox, HMAC evidence, close grants, events).
- `path_hash` uniqueness and one-ACTIVE release constraint in SQL.
- Job/schedule/lease regression tests against documented PRESERVED_BEHAVIOR.
- HMAC receipts carry `signature_alg` + `key_id`.
- Fail-closed authorize / approvals / journal / ZWNJ / shadow mode.
- AAX-12 in-repo Agiflow steward: mapping, HMAC-issued Review evidence, one-time human Done grant, human-edit conflict, outbox replay of ids only, no runtime writes, no ClickUp dependency. Caller-constructed evidence is rejected (`UNKNOWN_EVIDENCE`).
- Engine + steward pytest green from the working tree.
