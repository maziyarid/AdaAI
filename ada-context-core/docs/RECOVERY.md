# Recovery contract

“PostgreSQL is authoritative” is incomplete without recovery.

Phase 1 production requirements:
- encrypted daily logical backups
- WAL archiving / PITR appropriate to the PostgreSQL installation
- at least one off-host backup destination
- checksums
- retention policy
- backup failure alerts
- periodic restore drill
- documented RPO/RTO

`scripts/backup.sh` deliberately requires an `age` public recipient. Never put a private decryption key in the service environment. `scripts/restore-drill.sh` restores into a temporary database and verifies core tables before dropping it.

A backup is not trusted until a restore drill succeeds.
