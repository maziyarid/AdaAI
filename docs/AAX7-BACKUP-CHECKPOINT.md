# AAX-7 AC1 — encrypted backup / schema checkpoint (STOP, not Apply)

Status: **AC1 schema checkpoint + restore drill PASS. Full encrypted row backup remains required before any future Apply.**
Date: 2026-09-19. HEAD at authoring: `e529bc4`.

This is the production-safe **pre-migration backup/schema checkpoint
and rollback trigger** contract. Isolated MariaDB rehearsal already
proved additive apply + drop-`ada_*` rollback on a disposable
skip-networking instance (`docs/AAX7-ISOLATED-MARIADB-REHEARSAL.json`).
That is **not** an encrypted production backup.

Do **not** apply `001`–`006` from this document.
Do **not** put credentials, age private keys, or row dumps in git.
`ada-context-core/scripts/backup.sh` is PostgreSQL/`pg_dump` and is
**not** the production path.

Driver: `ada-reliability/scripts/backup_checkpoint_plan.py`
(default: dry-run JSON; execute only against a `/tmp` rehearsal socket).

Rule: models propose. Deterministic code authorizes. Independent
validators prove the live result.

## AC1 live evidence — 2026-09-19

A production table-schema-only checkpoint was executed from the live MariaDB
using the runtime DB account. It contained zero row payloads and zero INSERT
statements.

Evidence:
- retained checkpoint: /var/backups/ada/control-core/schema-20260919T125013Z.sql
- sha256: bbe20ae5e6482a988562de16e5faa5634c34a75207e4cd4d846ff240f9e3a488
- size: 21,296 bytes
- CREATE TABLE count: 20
- restored into a disposable MariaDB 10.11 instance with skip-networking
- restored table inventory matched production: 20/20
- critical DDL hashes matched for jobs, schedules, job_results,
  dead_letter_queue, pending_external_sync, and audit_log
- production SQL writes: none
- production mutation: none
- rollback procedure is independently exercised in
  docs/AAX7-ISOLATED-MARIADB-REHEARSAL.json

The runtime DB account cannot SHOW EVENTS, so routines, events, and triggers
were excluded from this table-schema checkpoint. They are outside the current
control-core migration scope. The first privileged dump attempt failed closed
before producing a usable checkpoint.

This satisfies AAX-7 AC1 as written: the pre-migration schema checkpoint and
rollback procedure are tested. It does not replace the operational pre-Apply
requirement for a full encrypted row backup with an off-host private key and
checksum-verified off-host copy.

Secret-free machine-readable evidence:
docs/AAX7-LIVE-SCHEMA-CHECKPOINT-RESTORE.json.

## Artefacts (no secrets)

| Kind | On-host path (example) | Encrypted | Contains rows |
| --- | --- | --- | --- |
| Schema checkpoint | `/var/backups/ada/control-core/schema-$TS.sql` | no (DDL only) | **no** |
| Encrypted logical dump | `/var/backups/ada/control-core/full-$TS.sql.gz.age` | yes (`age`) | yes |
| Checksums | `*.sha256` next to each artefact | n/a | no |
| Off-host copy | operator-controlled; ciphertext + schema + checksums only | yes | schema: no; full: ciphertext only |
| Restore drill log | `/var/backups/ada/control-core/restore-drill-$TS.json` | no (counts/hashes) | **no** |

Directory mode `0700`, owner `mazcontrol:mazcontrol`.
Retention: 14 daily encrypted dumps, 4 weekly, schema checkpoints 30 days.
Never commit artefacts. Never `cat` the dump.

Database name and user come from env **names**
`CONTROL_DB_NAME` / `CONTROL_DB_USER` (values not in git).
Auth is `--defaults-extra-file` owned `0600 mazcontrol`, never
`--password=` on the command line.

Age **recipient** is a public key (`ADA_BACKUP_AGE_RECIPIENT`).
The private key must not live on the VPS and must not be in git.

## Exact command plan (placeholders only)

All commands run as `mazcontrol` on `server.maziyarid.com` after
human approval. `TS=$(date -u +%Y%m%dT%H%M%SZ)`.
`DEST=/var/backups/ada/control-core`. Defaults file is **not** the
control-core env file.

### 0. Preconditions (stop if any fail)

For the schema checkpoint:
1. ada-inspect tables captured.
2. mariadb-dump present.
3. Temporary defaults file is mode 0600 and deleted after use.
4. Production Apply is not in this session.

Additional requirements before the full encrypted row backup:
5. Disk free is at least 3 times the current datadir size.
6. age is installed.
7. An age public recipient is configured; the private key remains off-host.
8. Off-host destination is reachable and checksum verification is available.

### 1. Schema-only checkpoint (no row payloads)

The live runtime account lacks SHOW EVENTS, and the Phase-1 migration scope is
table DDL. The tested checkpoint therefore excludes routines, events, and
triggers explicitly.

    mariadb-dump --defaults-extra-file=/run/ada-mysql.cnf       --single-transaction --no-data --skip-comments --skip-dump-date       --skip-triggers --skip-routines --skip-events       "$CONTROL_DB_NAME" > "$DEST/schema-$TS.sql"
    sha256sum "$DEST/schema-$TS.sql" > "$DEST/schema-$TS.sql.sha256"

The temporary defaults file is created mode 0600, used only for the dump/read
commands, and removed immediately afterward.
Root may read /etc/maziyar-control-core.env only to construct that temporary file; the env file itself is never passed to mariadb-dump, copied into an artefact, or committed.

Must include jobs, schedules, job_results, dead_letter_queue, and
pending_external_sync. Must contain zero INSERT INTO statements.

### 2. Encrypted full logical backup

This safeguard is still pending because age and an off-host recipient are not
configured. When they are available, use the same table-backed scope:

    mariadb-dump --defaults-extra-file=/run/ada-mysql.cnf       --single-transaction --skip-triggers --skip-routines --skip-events       --hex-blob "$CONTROL_DB_NAME"       | gzip -9       | age -r "$ADA_BACKUP_AGE_RECIPIENT"         -o "$DEST/full-$TS.sql.gz.age"
    sha256sum "$DEST/full-$TS.sql.gz.age" > "$DEST/full-$TS.sql.gz.age.sha256"

single-transaction is required for InnoDB. Do not use lock-all-tables on the
live control core. Never log or print the dump body.

### 3. Checksum / verification

- sha256 of schema file and of ciphertext
- `age -d` of ciphertext **off-host** (private key never copied in)
- `gzip -t` on the decrypted stream
- confirm dump header names `$CONTROL_DB_NAME`
- confirm schema dump has zero `INSERT INTO`

### 4. Off-host copy

Copy **only** `schema-*.sql`, `full-*.sql.gz.age`, and `*.sha256`.
Re-hash after copy; mismatch is a failed backup, not a warning.

### 5. Restore validation (throwaway, never production)

```bash
# throwaway schema name is literal; do not restore onto $CONTROL_DB_NAME
mysql --defaults-extra-file=/etc/ada/mysql.cnf \
  -e "CREATE DATABASE ada_restore_drill_$TS"
age -d -i /path/to/offhost-age-identity \
  "$DEST/full-$TS.sql.gz.age" | gzip -dc \
  | sed "s/\`$CONTROL_DB_NAME\`/\`ada_restore_drill_$TS\`/g" \
  | mysql --defaults-extra-file=/etc/ada/mysql.cnf ada_restore_drill_$TS
```

Checks (counts only, no payload dump):

```sql
SELECT COUNT(*) FROM jobs;
SELECT COUNT(*) FROM schedules;
SELECT COUNT(*) FROM pending_external_sync;
SHOW TABLES LIKE 'ada_%';
SHOW TABLES LIKE 'pd_%';
```

Then `DROP DATABASE ada_restore_drill_$TS`.
Record counts + sha256 in `restore-drill-$TS.json`.
Do **not** restart WordPress MCP, OAuth, GSC, or control-core for a
successful drill.

### 6. Rollback trigger criteria (when to restore vs drop-ada)

| Trigger | Action |
| --- | --- |
| Apply never started | do nothing; keep backups |
| Only `ada_*` created; `jobs`/`schedules` hashes unchanged | drop `ada_*` only (ROLLBACK-RUNBOOK “If only Ada tables were added”) |
| Any `ALTER`/`DROP` of live names, or job/schedule row drift | **stop Apply**, restore encrypted dump into a new instance, cut over only with human approval |
| Restore drill checksum mismatch | **do not Apply**; treat backup as missing |
| `pd_worker_runs` / `pd_outbox` discovered live after backup | **stop**; remap 006 before any Apply |
| Control-core unhealthy after a future Apply | restore last checksum-passing dump; do not “fix forward” with unreviewed SQL |

Production rollback of the live instance is a **human** action.
Shadow/Ada must not execute it.

## Isolated rehearsal mapping

The skip-networking MariaDB rehearsal:
- checkpoints the 20 control-core tables and protected CREATE hashes
- exercises job/schedule/lease/retry/DLQ semantics before and after migrations
- applies migrations 001-006 twice
- drops only ada_* and restores the 20-table baseline

The live schema checkpoint restore drill now additionally proves that a
production DDL checkpoint can be restored into a throwaway MariaDB and recover
the same table inventory and critical DDL.

AC1 is therefore checked. The full encrypted row backup/off-host-copy path is
still a pre-Apply safeguard and remains intentionally incomplete because no
off-host age recipient is configured.

## Explicitly not done

- Production full-row dump
- Production age encryption
- Production row-data restore
- Apply of migrations 001-006
- Persisting production DB credentials outside the temporary 0600 defaults file

PRODUCTION_SQL_WRITE: **NONE**. PRODUCTION_MUTATION: **NONE**.
Production schema read/checkpoint: **DONE**.
