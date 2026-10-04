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

Conversation routing and display:
- Only a slash-prefixed message is interpreted as a command. Ordinary English/Persian text reaches the bounded chat backend after private numeric identity, forwarding/group, rate-limit and kill-switch checks.
- Unknown slash commands show help and never reach the model. Status, health and alert headings use real display line breaks.
- Backend/read failures emit fixed event names and error types, not provider exception text or private chat snippets.

Feedback dataset release v2:
- Export is explicit and approved-only; raw inbound chat, actor identifiers, pairing and credentials are excluded. Approval still requires human privacy/consent review; automated capture-time redaction is not a guarantee that arbitrary patient/private prose is safe for training.
- The manifest schema is ada.feedback.dataset/v2. Each row retains its original feedback fingerprint and adds split_group. Split grouping hashes the NFKC/casefold/whitespace-normalised original text, independent of preferred answer, reason, category and Qalam release. Revisions of the same normalised original remain together across new dataset versions.
- This prevents exact normalised-input overlap between v2 splits. It does not detect semantic near-duplicates, partial excerpts or paraphrases; review those before tuning or held-out evaluation.
- Do not combine v1 fingerprint-split training data with v2 evaluation. Existing immutable v1 releases stay unchanged; rebuild/review a complete v2 corpus and verify overlap before any new training/evaluation use. No model or dataset is automatically promoted.
- Exports serialize through a private lock, stage private files, verify hashes, flush files/directories and publish only the completed version directory. Ordinary pre-publication failures remove the temporary staging directory and permit retry. A process/power loss can leave an unreferenced .export-* staging directory; never treat it as a released dataset. A crash after rename can leave a complete version whose success response was lost; inspect its manifest rather than overwrite it.
- Version names cannot begin with a dot or exceed 128 characters. An existing directory or symlink is never replaced by a cooperating exporter.
- Rejection/removal affects future exports. Published manifests and files remain immutable; withdrawal of already-distributed data requires a separately tracked recall.

- If parent-directory sync fails after publication, the exporter reports a fixed 'publication durability is unconfirmed' diagnostic. The complete immutable release is preserved. Verify its manifest and storage durability before using it; do not overwrite the version or infer durable success from its presence alone.

Operator decision notes:
- /decision AAX-36 | decision | rationale uses the separately gated Unix-socket gateway. Both bot and gateway default ADA_DECISIONS_ENABLED=false. See ../agiflow-decision-gateway/README.md in source (installed gateway docs: /opt/ada-decision-gateway/README.md).
- A queue receipt does not mean Agiflow delivery. Preserve the original inbound update on uncertain transport errors; reconcile before creating a new command. Never add provider/core credentials to the bot environment.

### Feedback email privacy

New explicit feedback redacts email addresses regardless of case in the original,
preferred wording and rationale. Exports refuse approved historical rows that
still contain a matching email address, before any release is created. Review
and reject affected entries through the protected feedback administration path;
capture a corrected example and approve it separately. Existing rows and immutable
dataset releases are not automatically rewritten. The email guard is a bounded
pattern check and does not replace human privacy review for other sensitive data.
