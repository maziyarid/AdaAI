# Phase-1 blocker report

Status: **local engine + 33 pytest green. Remote branch still missing full engine.py / contract tests (push size). Production import and canary not executed.**

## Blocker 1 — no live VPS / SentinelX access

**Affected:** freeze/import of `/opt/maziyar-control-core`, live MariaDB schema capture, systemd unit dump, env-name capture, production shadow wrap.

**Evidence:** this session has GitHub, not SSH/VPS MCP.

**Safest next step:** from an authorized VPS session:

1. `tar` `/opt/maziyar-control-core` excluding `.env` / secrets.
2. `mysqldump --no-data` the control-core schema.
3. `systemctl cat maziyar-control-core.service maziyar-mistral-worker.service`.
4. List environment **names** only.
5. Commit under `runtime/control-core-baseline/imported/` on this branch.

## Blocker 2 — production canary not authorized

Do not run a live Teznevise mutation without explicit human approval after shadow evidence.

## Blocker 3 — Bible v1.4 filename vs current 2.0.0

Mirrored existing 2.0.0. Did not invent a v1.4 document.

## Blocker 4 — GitHub connector payload size

Full `engine.py` + `test_phase1_contracts.py` verified locally and zipped. Apply the zip onto `phase1/reliability-layer` from a machine that can `git push`.

## Non-blockers (done)

- Additive MariaDB `ada_*` SQL written, dialect-reviewed, not applied.
- Job/schedule/lease regression tests added against documented PRESERVED_BEHAVIOR.
- HMAC receipts carry `signature_alg` + `key_id`.
