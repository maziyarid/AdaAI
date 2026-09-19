# Live control-core source snapshot (AAX-3)

Secret-free capture of `/opt/maziyar-control-core` from `server.maziyarid.com`
via viewer profile `grok-ada-readonly` on 2026-09-19T06:42Z.

This directory is a **frozen import** of the production implementation so
Ada reliability can target the actual control plane. It is not a second
scheduler and must not be deployed beside MariaDB.

## What is here

- `control_core.py` — live binary of record (65370 bytes / 1096 lines)
- `maziyar-control-core.service` — unit text (no EnvironmentFile values)
- `MANIFEST.json` — capture metadata including SHA-256 of captured bytes

## What is not here

- `/etc/maziyar-control-core.env` values
- `state/` and `tools/` (viewer mode-denied)
- `clickup_state_steward.py` (mode-denied)
- `venv/`
- dated `.bak*` copies
- live `SHOW TABLES` / systemd ActiveState (still gated; see AC3)

## Hash caveat

`sha256sum` is not on the viewer allowlist. `sha256_captured_bytes` is
computed from the `cat` payload. Size matches live `wc -c`. Host inode
hash remains unchecked until `ada-inspect hashes` is installed.

## Schema / schedules

Parsed from this snapshot, not from MariaDB:

- 20 `CREATE TABLE IF NOT EXISTS` names (no `ada_*`, no `pd_worker_runs`,
  no `pd_outbox`)
- `create_job` uses `INSERT IGNORE` on unique `idempotency_key`
- `claim_job` uses `FOR UPDATE SKIP LOCKED` and lease reclaim
- `seed_schedules` registers six interval jobs (see tests)

Do not execute this copy in the Ada App Builder sandbox. Production
remains `/opt/maziyar-control-core` on the VPS.
