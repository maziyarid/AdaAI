# AdaLLMbot Runtime Runbook

Telegram is transport only. Agiflow is durable project/incident memory. VPS/runtime state is authoritative for service health. Git is authoritative for code.

Secrets: TELEGRAM_BOT_TOKEN belongs only in /etc/ada-telegram-bot.env (root:adabot 0640). Never store it in Git, Agiflow, logs, alert bodies, ordinary prompts, or shell history. Rotate the bootstrap token before production acceptance.

Activation:
1. Rotate any token exposed during bootstrap.
2. From an operator-controlled terminal run /usr/local/sbin/ada-bot-set-token.
3. Start ada-telegram-bot.service.
4. Pair in a private Telegram chat with the one-time pairing code.
5. Verify /ping, /health, /status and /alerttest.
6. Verify ada-bot-health exits 0.

If no token is configured, ExecCondition skips startup rather than creating a restart loop.

Kill switch:
- ada-botctl disable-commands
- ada-botctl enable-commands
Outbound alerts remain independent of inbound-command availability.

Durable alerts:
ada-send-alert --severity warning --source worker --key STABLE_KEY "message"
For state-change-only alerts add --fingerprint INCIDENT --state STATE. Repeated unchanged states are suppressed.
Repeated delivery failures back off and eventually enter dead-letter state.

Recovery:
Inspect journalctl -u ada-telegram-bot.service, ada-botctl status and ada-botctl queue.
Durable cursor, pending inbound updates, identity, outbox and alert state live under /var/lib/ada-telegram-bot.
Never blindly replay consequential commands after a crash.

Backup:
Back up non-secret state with permissions preserved. Do not include /etc/ada-telegram-bot.env in ordinary state backups. Stop the service or use SQLite backup semantics before copying the DB.

Rollback:
Pre-change files are stored under /opt/ada-telegram-bot/backups/<UTC timestamp>/. Restore files, daemon-reload, restart and verify health.

Production acceptance requires rotated token, numeric private user+chat pairing, durable cursor, duplicate-update safety, restart resilience, provider-outage retry/dead-letter test, unknown-user/group denial, kill-switch test, secret-redaction test, and end-to-end inbound/outbound proof.

Health inspection:
- ada-bot-health performs bounded read-only SQLite inspection; a missing DB is not created.
- Exit 0 means valid readiness plus a matching live PID, a heartbeat aged 0–90 seconds, private 0600 database permissions, successful integrity/queue reads and a running/degraded process state. Exit 2 means unavailable health.
- A degraded process is visible as state=degraded; exit 0 is not proof that Telegram or Agiflow end-to-end delivery works.
- database_ok and process_alive are explicit. Unavailable queue counts are null rather than a misleading zero. errors contains fixed categories only, never raw exception text or state contents.
- Future/invalid heartbeat epochs, mismatched PIDs, malformed/oversized status files and missing/corrupt/schema-incomplete databases fail closed.
- Read-only connections include committed WAL transactions. SQLite may maintain its normal WAL shared-memory bookkeeping; the checker does not execute state writes. Database lock waits and query work each have a two-second budget.

Offline state recovery proof:
- tests/test_state_restore.py exercises the existing backup-state command on synthetic bot state and restores its SQLite snapshot into a clean fixture. Cursor 55→56, inbound identity, alert idempotency and pending feedback survive; duplicate alert/feedback creation is suppressed.
- Database-only backups exclude protected pairing/identity files, credentials, readiness and heartbeat. A database-only restore does not pair or activate the bot. The operator must separately recover protected configuration/identity through the established secure procedure before any delivery.
- This offline proof does not accept a production backup destination, prove receive/send delivery, or authorise activation. Verify those in AAX-39/AAX-40 after private token rotation and pairing.
