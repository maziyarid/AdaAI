# AAX-3 live control-core baseline (secret-free)

Captured 2026-09-18T22:15Z via Eqialise profile `grok-ada-readonly`
(`mistralops`, role=viewer). Commands were allowlisted `ls` / `find` /
`stat` / `cat` / `head` / `grep`. No environment **values**, tokens,
database contents, or secret-bearing files were copied.

This document replaces the earlier “Ada SSH is down” note on
`6364bced`. It is a host inventory, not a production cutover.

## Host identity

- Hostname reported by `hostname`: `server.maziyarid.com`
- Viewer home: `/home/mistralops`
- `/opt/maziyar-control-core` **exists on this host** (unlike the
  Royadarman/content host, where that path is absent).

`/opt` also contains cPanel, Imunify, SentinelX, and Teznevise QA
scripts. Those are co-located services, not the Ada scheduler.

## Tree (readable)

`/opt/maziyar-control-core/`:

- `README.md`
- `control_core.py` (live binary of record)
- `clickup_state_steward.py`
- `tool_harvester.py`
- `venv/`
- `state/` — **Permission denied** for viewer
- `tools/` — **Permission denied** for viewer
- Multiple dated `control_core.py.bak*` / `.before-*` copies

`stat` on `control_core.py` (no hash; `sha256sum` is not on the
read-only allowlist):

- Size: 65370 bytes
- Mode: 0555, owner root:root
- Modify: 2026-09-12 23:50:04 +0530
- Change: 2026-09-17 23:52:21 +0530

## systemd (unit text only)

`/etc/systemd/system/maziyar-control-core.service` is installed and
linked from `multi-user.target.wants`.

Observed unit facts (names only):

- Description: Maziyar durable control core and local scheduler
- After/Requires: `network-online.target`, `mariadb.service`
- User/Group: `mazcontrol`
- WorkingDirectory: `/opt/maziyar-control-core`
- EnvironmentFile: `/etc/maziyar-control-core.env` (file exists;
  viewer cannot read it)
- ExecStart: venv python `control_core.py serve`
- Hardening: `ProtectSystem=strict`, `ProtectHome=true`,
  `ReadWritePaths=/opt/maziyar-control-core/state`
- Restart=on-failure, RestartSec=5

`systemctl is-active` is **not** on the viewer allowlist. Process
liveness is therefore not independently proven in this capture.

Related units present on the same host (not started from this session):

- `maziyar-mistral-worker.service` — User `maziyarid`,
  WorkingDirectory `/srv/community-mcp/mistral-worker`,
  EnvironmentFile `/etc/maziyar-mistral-worker.env`,
  ExecStart `node …/index.mjs`
- `maziyar-agiflow-outbox-bridge.service` + timer — oneshot
  `/srv/maziyar-wp-mcp/deploy/agiflow_outbox_bridge.py handoff --limit 20`
- `maziyar-ai-worker.service` + timer
- `maziyar-editorial-intake.service` + timer
- `maziyar-teznevise-remediation.service` + timer
- `maziyar-wp-mcp.service`, local WP REST units, MCP OAuth gateway,
  session router, self-heal timer

Live Agiflow projection already has a VPS oneshot + timer. AAX-6/AAX-12
must treat that as existing runtime plumbing, not invent a second
scheduler.

## Environment names (from source, not from the env file)

`control_core.py` references these names. Values were not read.

- `CONTROL_DB_HOST`
- `CONTROL_DB_PORT`
- `CONTROL_DB_USER`
- `CONTROL_DB_PASSWORD`
- `CONTROL_DB_NAME`
- `CONTROL_API_TOKEN`
- `CONTROL_ACTOR`
- `CONTROL_BIND`
- `CONTROL_PORT`
- `MISTRAL_API_KEY`
- `MISTRAL_API_BASE`
- `MISTRAL_DEFAULT_MODEL`
- `GROK_CLICKUP_USER_ID`

README still describes loopback bind `127.0.0.1:8770` and MariaDB/InnoDB.
That matches `CONTROL_BIND` / `CONTROL_PORT` defaults in source.

## Schema names in source (not live `SHOW TABLES`)

`CREATE TABLE IF NOT EXISTS` strings in `control_core.py`:

`schema_migrations`, `agent_events`, `canonical_tasks`, `jobs`,
`job_results`, `schedules`, `dead_letter_queue`, `service_health`,
`operator_reachability`, `operator_state`, `cache_manifest`,
`harvest_provider_state`, `tool_harvest_queue`, `data_snapshots`,
`intelligence_findings`, `forecasts`, `content_gate_states`,
`green_buffers`, `pending_external_sync`, `audit_log`.

No `ada_*` table names appear in this live source file. Live confirmation
of `ada_*` vs `pd_*` still needs `mysqldump --no-data` or equivalent
under an approved account. Viewer cannot query MariaDB.

Seeded schedules named in README: `SEO_SCOUT`, `PROJECT_CONTROLLER`,
`ORACLE_FORECASTER`, `BLACKOUT_SENTINEL`.

## Explicitly not captured

- Env file contents / secret values
- `state/` and `tools/` directories
- Live systemd ActiveState
- Live MariaDB table list, row counts, leases, `pending_external_sync`
  conflict rows
- `/health` probe caller (AAX-4)
- Production apply of repo `ada_*` SQL

## Remaining AAX-3 work

1. Privileged or mazcontrol-scoped `systemctl status` + `mysqldump --no-data`.
2. Confirm no `ada_*` tables before any migration rehearsal (AAX-7).
3. Identify localhost `/health` 401 caller without weakening auth (AAX-4).
4. Diagnose unresolved `pending_external_sync` rows without mass-retry
   (AAX-5).
