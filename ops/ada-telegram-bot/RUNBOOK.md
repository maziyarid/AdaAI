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
