# Captured live control-core behavior (document baseline)

Source: AdaAI architecture docs dated 2026-09-16. **Not** a live filesystem copy of `/opt/maziyar-control-core`.

## Service

- Unit: `maziyar-control-core.service`
- Bind: `127.0.0.1:8770`
- Path: `/opt/maziyar-control-core`
- DB: MariaDB 10.11

## Already implemented (must be preserved)

- jobs
- schedules
- leases
- retries
- dead-letter queue
- audit log
- content gates
- snapshots
- external synchronization state
- health/state records
- idempotent enqueue (expected)

## Mistral worker

- Unit: `maziyar-mistral-worker.service`
- Bind: `127.0.0.1:9102`
- Delegates local job/schedule operations to the control core.

## Environment names (values must never be committed)

Expected class of names only:

- database DSN / user / password
- internal API keys
- WordPress application passwords
- OAuth client secrets
- HMAC / receipt keys

## Import status

Blocked this session. See `docs/BLOCKERS.md`.
