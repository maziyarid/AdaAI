# Captured live control-core behavior (document baseline)

Source: live `/opt/maziyar-control-core/control_core.py` imported
2026-09-19T06:42Z into `runtime/control-core-baseline/live/`.
SHA-256 of captured bytes:
`aec6639acf761dfb01a72feb670b4d841c25fb1e8000abdea41bca0dcf4a94f3`
(65370 bytes / 1096 lines). Host `sha256sum` still POLICY_DENIED.

This is **not** a second scheduler.

## Service

- Unit: `maziyar-control-core.service` (User/Group `mazcontrol`)
- Bind: `127.0.0.1:8770` (`CONTROL_BIND` / `CONTROL_PORT` defaults)
- Path: `/opt/maziyar-control-core`
- DB: MariaDB 10.11 (source uses InnoDB `CREATE TABLE IF NOT EXISTS`)

## Already implemented (must be preserved)

- jobs (`INSERT IGNORE` unique `idempotency_key`)
- schedules (six seeded interval jobs)
- leases (`locked_by` / `lease_until`; expired running → queued)
- retries (exponential `available_at` backoff in `finish_job`)
- dead-letter queue (when attempts >= max_attempts)
- audit log
- content gates
- snapshots
- external synchronization state (`pending_external_sync`, SKIP LOCKED)
- health/state records (`GET /health` 200 only after Bearer auth;
  unauthenticated 401 is the configured healthy signal)
- idempotent enqueue (`create_job` INSERT IGNORE)

## Seeded schedules (source, not live enabled flags)

| stable_id | agent | interval |
| --- | --- | --- |
| schedule:blackout-sentinel | BLACKOUT_SENTINEL | 300 |
| schedule:project-controller | PROJECT_CONTROLLER | 600 |
| schedule:clickup-state-steward | CLICKUP_STATE_STEWARD | 600 |
| schedule:seo-scout | SEO_SCOUT | 3600 |
| schedule:temp-tool-harvester | TEMP_TOOL_HARVESTER | 900 |
| schedule:oracle-daily | ORACLE_FORECASTER | 86400 |

## Mistral worker

- Unit: `maziyar-mistral-worker.service`
- Bind: `127.0.0.1:9102`
- Delegates local job/schedule operations to the control core.

## Environment names (values must never be committed)

- `CONTROL_DB_HOST` `CONTROL_DB_PORT` `CONTROL_DB_USER` `CONTROL_DB_PASSWORD` `CONTROL_DB_NAME`
- `CONTROL_API_TOKEN` `CONTROL_ACTOR` `CONTROL_BIND` `CONTROL_PORT`
- `MISTRAL_API_KEY` `MISTRAL_API_BASE` `MISTRAL_DEFAULT_MODEL`
- `GROK_CLICKUP_USER_ID`

## Import status

Source + unit imported. Live MariaDB `SHOW TABLES` and systemd
ActiveState still gated on `ada-inspect` (not installed). AC3 open.
