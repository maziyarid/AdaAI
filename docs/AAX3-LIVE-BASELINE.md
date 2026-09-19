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

Seeded schedules from live `seed_schedules()` (interval seconds in
source; live `enabled` flags are unconfirmed without MariaDB):

- `BLACKOUT_SENTINEL` / `blackout_sentinel.run` — 300
- `PROJECT_CONTROLLER` / `project_controller.run` — 600
- `CLICKUP_STATE_STEWARD` / `clickup_state_steward.run` — 600
  (legacy compatibility seed; AAX-6/AAX-12 still treat ClickUp as
  non-runtime)
- `SEO_SCOUT` / `seo_scout.run` — 3600
- `TEMP_TOOL_HARVESTER` / `temp_tool_harvester.run` — 900
- `ORACLE_FORECASTER` / `oracle_forecaster.run` — 86400

## Explicitly not captured

- Env file contents / secret values
- `state/` and `tools/` directories
- Live systemd ActiveState
- Live MariaDB table list, row counts, leases, `pending_external_sync`
  conflict rows
- Production apply of repo `ada_*` SQL

## Session addendum 2026-09-19 (after PR head `2dd1ffb`)

`grok-ada-readonly` was disconnected in the Grok client cache, then
reconnected. Viewer identity is unchanged:

- `pwd`: `/home/mistralops`
- `uname -a`: `Linux server.maziyarid.com 5.14.0-687.46.1.el9_8.x86_64`
- `/opt/maziyar-control-core` still exists
- `control_core.py` still 65370 bytes / 1096 lines (`wc`)

`printf` glob of `/etc/systemd/system/maziyar*` still shows
`maziyar-control-core.service`, `maziyar-mistral-worker.service`,
`maziyar-agiflow-outbox-bridge.service` + `.timer`, and the other
units listed above. MariaDB client/server config files exist under
`/etc/my.cnf.d/` (contents not read). `/var/lib/mysql/*` does not
expand for this viewer.

Viewer MCP policy this session is stricter than the 22:15Z capture:
classified-safe tools (`ls`, `cat`, `grep`, `stat`, `systemctl`,
`sha256sum`, `awk`) are refused on the readOnly profile; `python3`
is classified destructive and refused. Do not clear `readOnly`.
Do not treat this as Ada SSH being down again.

## Session addendum 2026-09-19T23:05Z (PR head `3513278`)

Classifier this session allowed `ls`, `cat`, `grep`, `head`, and `wc`
again. `systemctl` and `sha256sum` remain refused. `readOnly` stays on.
Do not treat classifier flapping as host disappearance.

Reconfirmed without secrets:

- Hostname: `server.maziyarid.com`
- `wc -c` / `wc -l` on `control_core.py`: 65370 bytes / 1096 lines
- `ls /opt/maziyar-control-core` still shows `control_core.py`,
  `clickup_state_steward.py`, `tool_harvester.py`, `venv/`, plus
  `state/` and `tools/` (viewer still cannot list those two)
- Unit text for `maziyar-control-core.service` unchanged
  (User/Group `mazcontrol`, WorkingDirectory
  `/opt/maziyar-control-core`, EnvironmentFile
  `/etc/maziyar-control-core.env` unread, ExecStart venv python
  `control_core.py serve`, `ProtectSystem=strict`,
  `ReadWritePaths=/opt/maziyar-control-core/state`)
- Source `CREATE TABLE IF NOT EXISTS` list unchanged. **No `ada_*`
  names in live `control_core.py`.**
- `grep pd_worker_runs` / `grep pd_outbox` / `grep pd_` on
  `control_core.py` are empty. Live ChatGPT canary tables
  `pd_worker_runs` / `pd_outbox` are not defined in this file;
  they remain a separate VPS artefact to reconcile at AAX-7.
- `clickup_state_steward.py` is still mode-denied for this viewer.

### AAX-4 caller (source evidence, no auth change)

Localhost `GET /health` every ~5 minutes is **not** an unknown
external monitor. Live `control_core.py` defines:

- `HEALTH_TARGETS` includes
  `("control-core", "http://127.0.0.1:8770/health", (401,))`
- Comment on that table: “An HTTP 401 is healthy for protected MCP
  resources.”
- `seed_schedules()` registers `BLACKOUT_SENTINEL` /
  `blackout_sentinel.run` at **300 seconds**
- `run_sentinel()` probes each target and sets
  `ok = probe["status"] in expected`

So 401 on unauthenticated `/health` is the **configured healthy
signal** for this protected endpoint. The HTTP handler also has a
`GET /health` → 200 JSON branch; credential-free probes never reach
it. Do **not** make `/health` public. Do **not** weaken
`CONTROL_API_TOKEN` auth.

A later code change, if wanted, should add a separate
no-secrets `/livez` and point `HEALTH_TARGETS` at that path — not
strip auth from `/health`. Not implemented here. No production
mutation.

`maziyar-mcp-self-heal.timer` is every 1 minute and targets MCP
OAuth/gateway (`ExecStart=/usr/local/sbin/maziyar-mcp-self-heal`).
That is not the control-core `/health` 401 loop.

### Smallest extra read-only scope still needed

Keep `grok-ada-readonly` as-is. Preferred extra profile is a
`mazcontrol` **read-only** command allowlist, not root:

1. `systemctl show -p ActiveState,SubState,MainPID,FragmentPath,ExecStart`
   for `maziyar-control-core.service`,
   `maziyar-mistral-worker.service`,
   `maziyar-agiflow-outbox-bridge.timer` only
2. `sha256sum /opt/maziyar-control-core/control_core.py`
3. Schema-only MariaDB: `mysqldump --no-data --skip-comments`
   or `SHOW TABLES` / `SHOW CREATE TABLE` as the `mazcontrol`
   DB user (names/indexes/constraints only)
4. Optional: `journalctl -u maziyar-control-core.service -n 50 --no-pager`
   with secret redaction

Still deny: arbitrary sudo, service restart, package install,
file writes, SQL DML/DDL apply, reading
`/etc/maziyar-control-core.env` or other secret files.

## Session addendum 2026-09-19 (fresh Grok account, Greptile 5/5)

Independent reconfirm of live Ada-readonly SSH after Greptile
reviewed `3513278` at **5/5** with no outstanding P0/P1.

- `pwd` = `/home/mistralops`
- `uname -n` = `server.maziyarid.com`
- `ls /opt/maziyar-control-core` still lists `control_core.py`,
  `clickup_state_steward.py`, `tool_harvester.py`, `venv/`, `state/`,
  `tools/`, README, and dated `.bak*` copies
- `wc -c` / `wc -l` = **65370 bytes / 1096 lines**
- `grep ada_`, `grep pd_worker_runs`, `grep pd_outbox` on
  `control_core.py` all exit 1 (no matches)
- `pending_external_sync` **is** a live control-core table (CREATE +
  lease columns `locked_by` / `lease_until`)
- systemd unit text re-read: User/Group `mazcontrol`, Requires
  `mariadb.service`, EnvironmentFile unread, ExecStart venv python
  `control_core.py serve`, `ProtectSystem=strict`
- Mistral worker unit: User `maziyarid`, ExecStart
  `/usr/bin/node /srv/community-mcp/mistral-worker/index.mjs`
- Agiflow outbox bridge timer: `OnUnitActiveSec=5min`
- Env **names** reconfirmed (values not read): `CONTROL_DB_HOST`,
  `CONTROL_DB_PORT`, `CONTROL_DB_USER`, `CONTROL_DB_PASSWORD`,
  `CONTROL_DB_NAME`, `CONTROL_API_TOKEN`, `CONTROL_ACTOR`,
  `CONTROL_BIND`, `CONTROL_PORT`, `MISTRAL_API_KEY`,
  `MISTRAL_API_BASE`, `MISTRAL_DEFAULT_MODEL`, `GROK_CLICKUP_USER_ID`
- `systemctl show` still POLICY_DENIED. `sha256sum` still gated.
- No production SQL. No live canary. `readOnly` stays on.

AAX-4 source proof reconfirmed: `HEALTH_TARGETS` control-core row is
`("control-core", "http://127.0.0.1:8770/health", (401,))` with
comment “An HTTP 401 is healthy for protected MCP resources.”
`GET /health` 200 JSON exists only after `auth()`. Credential-free
probes never reach it. `BLACKOUT_SENTINEL` interval is 300 seconds.

## Remaining AAX-3 work

1. mazcontrol-scoped `systemctl show` + `mysqldump --no-data`.
2. Confirm no live `ada_*` tables before any migration rehearsal (AAX-7).
3. AAX-4 caller is identified from source; production code change is
   optional and must not weaken auth.
4. Diagnose unresolved `pending_external_sync` rows without mass-retry
   (AAX-5).
5. Do not clear viewer `readOnly` to bypass the current MCP classifier.

## Session addendum 2026-09-19T06:42Z — live source imported (AC2)

Add A profile `grok-ada-readonly` allowed a single `cat` of
`/opt/maziyar-control-core/control_core.py`. Combined `&&` commands
are still classified as non-readonly. `readOnly` stayed on. Royadarman
was not used.

Imported into the repo (no secrets, no env file, no `state/`):

- `runtime/control-core-baseline/live/control_core.py`
- `runtime/control-core-baseline/live/maziyar-control-core.service`
- `runtime/control-core-baseline/live/MANIFEST.json`

Capture facts:

- 65370 bytes / 1096 lines (matches prior `wc`)
- SHA-256 of captured bytes
  `aec6639acf761dfb01a72feb670b4d841c25fb1e8000abdea41bca0dcf4a94f3`
- Host `sha256sum` still POLICY_DENIED — this is **not** the inode hash
- `clickup_state_steward.py`: Permission denied
- `ada-inspect`: still absent

Source contracts now in-repo (tests parse the snapshot):

- 20 `CREATE TABLE` names; **no `ada_*` / `pd_worker_runs` / `pd_outbox`**
- `create_job` `INSERT IGNORE` on unique `idempotency_key`
- `claim_job` `FOR UPDATE SKIP LOCKED` + expired-lease reclaim
- `pending_external_sync` leased SKIP LOCKED outbox
- `seed_schedules` six rows (BLACKOUT_SENTINEL 300 … ORACLE 86400)
- `API.auth()` Bearer `CONTROL_API_TOKEN` **before** `/health` 200 JSON
- `HEALTH_TARGETS` control-core expected 401 unchanged
- credentials only via `os.environ` / `os.getenv`

**AC2:** satisfied as a secret-free baseline of service/runtime, schema
*shape*, seeded schedules, and captured-byte source hash.

**AC3:** still unchecked. Source has no `ada_*` names. That is not
live `SHOW TABLES`. Do not apply SQL.

No production mutation. PR not merged.


## Session addendum 2026-09-19T23:20Z (fresh Grok account, HEAD `7953eab`)

Independent fetch confirmed remote HEAD is still
`7953eaba43bd0fe5230ae9f0b3f0370cf8a1d1ed`. No concurrent implementation
commit. Greptile score on implementation `3513278` remains **5/5**,
0 unresolved P0/P1. Docs-only HEAD has a Greptile check still
`in_progress`.

Ada MCP is the **Add A** connector profile `grok-ada-readonly`
(`mistralops`, role=viewer). Roya default is Royadarman and must not
be used as Ada.

This session independently reconfirmed (no secrets):

- `uname`: `Linux server.maziyarid.com 5.14.0-687.46.1.el9_8.x86_64`
- `id`: `uid=1003(mistralops) gid=1005(mistralops)`
- `control_core.py`: **65370 bytes / 1096 lines**, mode `0555` root:root,
  Modify 2026-09-12 23:50:04 +0530
- `grep ada_` / `pd_worker_runs` / `pd_outbox` on live source: no matches
- `CREATE TABLE` list unchanged (20 tables including
  `pending_external_sync` with `locked_by` / `lease_until`)
- Seeded schedules re-read from source lines 428–433:
  BLACKOUT_SENTINEL 300, PROJECT_CONTROLLER 600,
  CLICKUP_STATE_STEWARD 600, SEO_SCOUT 3600,
  TEMP_TOOL_HARVESTER 900, ORACLE_FORECASTER 86400
- Unit text re-read: User/Group `mazcontrol`, Requires `mariadb.service`,
  EnvironmentFile unread (`0640 root:mazcontrol`, 480 bytes),
  ExecStart venv python `control_core.py serve`, `ProtectSystem=strict`,
  `ReadWritePaths=/opt/maziyar-control-core/state`
- Mistral worker: User `maziyarid`, ExecStart
  `/usr/bin/node /srv/community-mcp/mistral-worker/index.mjs`,
  drop-in ReadWritePaths for `/srv/maziyar-wp-mcp/*` plus
  ReadOnlyPaths `/opt/maziyar-control-core`
- Agiflow outbox bridge: oneshot root, `OnUnitActiveSec=5min`,
  `/srv/maziyar-wp-mcp/deploy/agiflow_outbox_bridge.py handoff --limit 20`
- `multi-user.target.wants` includes `maziyar-control-core.service`,
  `maziyar-mistral-worker.service`, `mariadb.service`,
  `ssh-mcp-grok-temp.service`
- ssh-mcp Grok Ada unit is temporary (`RuntimeMaxSec=604800`) with
  existing audit-write drop-in
  `ReadWritePaths=/var/lib/mcpvps/.local/share/ssh-mcp`
- `clickup_state_steward.py` / `tool_harvester.py` remain mode-denied
- `sha256sum` / `systemctl show` / `cksum` / `openssl dgst` remain
  POLICY_DENIED. `readOnly` stays on. `sudoers.d` is unreadable.

Env **names** only (values not read). Source required names this
session: `CONTROL_DB_HOST/PORT/USER/PASSWORD/NAME`, `CONTROL_ACTOR`,
`CONTROL_BIND`, `CONTROL_PORT`, `CONTROL_API_TOKEN`, `MISTRAL_API_KEY`,
`MISTRAL_API_BASE`, `MISTRAL_DEFAULT_MODEL`, `GROK_CLICKUP_USER_ID`.

AAX-4 source proof reconfirmed: `HEALTH_TARGETS` control-core row
expects 401; `CONTROL_API_TOKEN` is required at line 918.

### Helper prepared, not installed

Repo now contains `ops/mazcontrol-readonly/ada-inspect` plus
`docs/MAZCONTROL-READONLY.md`. VPS install + MCP allowlist of that
single binary is the remaining AAX-3 infrastructure step. No
production SQL. No helper copied onto the host from this session.

## Repository adapter vs live `/health` (Greptile P1, no auth weaken)

Live dispatch authenticates **before** the `GET /health` 200 JSON
branch (`control_core.py` `auth()` at line 917, Bearer
`CONTROL_API_TOKEN`). Unauthenticated probes therefore receive 401.
`HEALTH_TARGETS` documents that 401 as the healthy signal.

`runtime/control-core-baseline/adapter.py` previously called
`/health` with no token and would raise on 401, diverging from the
documented deployment. The adapter now:

- treats unauthenticated HTTP 401 as `contract=protected-health`
  (`ok=True`) — matching BLACKOUT_SENTINEL
- sends `Authorization: Bearer <token>` only when
  `ControlCoreConfig.api_token` is set, and then expects 200 JSON
- fails closed with `HEALTH_ENDPOINT_PUBLIC` if unauthenticated
  `/health` returns success

Do **not** make `/health` public. Do **not** strip
`CONTROL_API_TOKEN`. A no-secrets `/livez` is still optional and
does not exist.

## Session addendum 2026-09-18T23:30Z (HEAD was `872ad1d`)

Independent fetch on a new Grok account:

- Remote HEAD at session start: `872ad1d416d06fe0da9faa5001ad3f1e9afd7a51`
  (docs helper only; implementation parent `3513278`)
- Greptile implementation 5/5 on `3513278` stands; docs HEAD later
  scored 3/5 with two P1s (runbook apply-before-reconcile, adapter
  health 401). Those are addressed in this follow-up.
- Ada MCP: Add A profile `grok-ada-readonly`, `pwd=/home/mistralops`
- `ada-inspect` still **not** installed (`stat` → ENOENT)
- `systemctl show` / `sha256sum` still POLICY_DENIED; `readOnly` stays on
- `ls` / `stat` / `cat` / `grep` reconfirmed: `control_core.py`
  65370 bytes, mode 0555 root:root, Modify 2026-09-12 23:50:04 +0530
- `grep ada_` / `pd_worker_runs` / `pd_outbox` still empty
- `CREATE TABLE` list unchanged (20 tables). `jobs` has
  `locked_by`/`lease_until`; `pending_external_sync` has the same
  plus unique idempotency
- GitHub Actions on `872ad1d`: run `35405493093` job
  `105794291766`, `runner_id=0`, logs 404, ~3s. Pytest never ran.

AC2/AC3 remain unchecked until `ada-inspect units/hashes/tables`.
No production SQL. PR not merged. PR not deployed.



## Live MariaDB table proof — 2026-09-19

The reviewed least-privilege `ada-inspect` helper is now installed at `/usr/local/bin/ada-inspect` and executed as `mazcontrol` without clearing the Grok profile's `readOnly` flag. `ada-inspect tables` returned exactly the 20 expected control-core MariaDB tables and **no `ada_*` / no `pd_*` tables**. Schema-only CREATE/column/index metadata was captured for `jobs`, `schedules`, `dead_letter_queue`, `pending_external_sync`, `job_results`, and `schema_migrations`; no rows or secrets were dumped. The separate AAX-15 `pd_*` recovery store was subsequently confirmed to be SQLite, not this MariaDB.

All AAX-3 acceptance criteria are now evidenced; AAX-3 is Review.
