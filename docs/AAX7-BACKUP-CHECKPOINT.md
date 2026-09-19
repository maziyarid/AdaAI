# AAX-7 AC1 — encrypted backup / schema checkpoint (STOP, not Apply)

Status: **command plan verified in-repo. Production backup not executed.**
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

## Why this is not yet a checked AC1

AC1 needs a **tested** backup/checkpoint **and** rollback procedure.
Rollback of `ada_*` is tested in isolation. Encrypted production
backup + off-host copy + restore drill into a throwaway schema still
need a human on `mazcontrol` because:

- viewer `grok-ada-readonly` cannot read
  `/etc/maziyar-control-core.env` or run `mysqldump`
- `ada-inspect` is still ENOENT
- this sandbox has no MariaDB client/server
- production dump would copy live job payloads unless schema-only

Stop here until a human runs the Execute section on the VPS, or until
an isolated skip-networking rehearsal socket is available to exercise
the same commands against non-production data.

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

1. `ada-inspect tables` captured (AAX-3 AC3) **or** an explicit
   written waiver that schema-only dump is the table inventory.
2. Disk free ≥ 3× current datadir size.
3. `age` and `mysqldump` present.
4. Age public recipient configured; private key **off-host**.
5. Off-host destination reachable.
6. Production Apply of `001`–`006` is **not** in this session.

### 1. Schema-only checkpoint (no row payloads)

```bash
mysqldump --defaults-extra-file=/etc/ada/mysql.cnf \
  --single-transaction --no-data --skip-comments --skip-dump-date \
  --routines --triggers --events \
  --databases "$CONTROL_DB_NAME" \
  > "$DEST/schema-$TS.sql"
sha256sum "$DEST/schema-$TS.sql" | tee "$DEST/schema-$TS.sql.sha256"
```

Must include `jobs`, `schedules`, `job_results`, `dead_letter_queue`,
`pending_external_sync`. Must **not** contain `INSERT INTO`.

### 2. Encrypted full logical backup

```bash
mysqldump --defaults-extra-file=/etc/ada/mysql.cnf \
  --single-transaction --routines --triggers --events --hex-blob \
  --databases "$CONTROL_DB_NAME" \
  | gzip -9 \
  | age -r "$ADA_BACKUP_AGE_RECIPIENT" \
    -o "$DEST/full-$TS.sql.gz.age"
sha256sum "$DEST/full-$TS.sql.gz.age" | tee "$DEST/full-$TS.sql.gz.age.sha256"
chmod 600 "$DEST/full-$TS.sql.gz.age" "$DEST/"*.sha256
```

`--single-transaction` is required (InnoDB). Do not use `--lock-all-tables`
on the live control-core. Do not log the dump body.

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

The skip-networking MariaDB rehearsal already:

- checkpointed 20 live-source tables + protected CREATE sha256
- applied `001`–`006` twice
- dropped only `ada_*` and restored the 20-table baseline

What it did **not** do (still open for AC1):

- `age` encryption of a dump
- off-host copy
- restore into a second throwaway schema from ciphertext
- production `mysqldump` of `$CONTROL_DB_NAME`

Re-run `isolated_mariadb_rehearsal.py` plus this plan’s encrypt/restore
steps against `/tmp/ada-rehearsal.sock` when a disposable mysqld is
available. Set `ADA_BACKUP_EXECUTE=isolated-rehearsal`. Never point
the driver at `server.maziyarid.com` or TCP 3306.

## Explicitly not done

- Production `mysqldump`
- Production `age` encrypt
- Production restore
- Apply of `001`–`006`
- Reading `/etc/maziyar-control-core.env`

PRODUCTION_SQL: **NONE**. PRODUCTION_MUTATION: **NONE**.
