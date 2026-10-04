# Ada operator decision gateway

This source implements AAX-36's explicit decision-note command. It does not close AAX-36 or authorise production activation.

## Contract

`/decision AAX-36 | decision text | rationale` submits only these two explicit fields. Normal chat, replies, forwarded messages and task descriptions cannot execute the command. The paired private numeric Telegram user/chat and the command kill switch are checked by the bot. The gateway independently checks Linux SO_PEERCRED against a dedicated non-root bot UID and exact configured operator user/chat IDs. All processes running as that UID are in the trust boundary; protect that account and its pairing state.

The gateway reads AAX-26, AAX-31 and the target through the supported authenticated Agiflow get_task method on every submission. Anchor IDs, project ID, slug, task ID shape and positive revisions must match. Anchor free text never grants authority. There is no cache or stale fallback. A provider outage/403 blocks queue creation; do not bypass it with another provider URL or writer.

A successful submission uses the existing control-core POST /external-sync endpoint. The queue payload is compatible with the existing Agiflow comment consumer. The gateway never claims or acknowledges work, edits task status/descriptions, writes directly to Agiflow, or creates a database/scheduler.

The idempotency key derives from configured bot ID, configured operator identity and Telegram update ID. Timestamp derives from the original Telegram message date. Mutable task revision/title are excluded from payload so a retry preserves exact content. The core's INSERT IGNORE receipt must match all target/action/key fields and exact parsed payload. Collisions fail without overwriting. Pending/in_progress/succeeded are existing queue receipt states; conflict/quarantined require review. The bot always says final Agiflow registration is unconfirmed: only the consumer's independent provider read can establish delivery.

A lost core response or Telegram reply reuses the bot's existing inbound update. No second outbox is introduced. Existing inbound retries stop after five attempts; requests older than 24 hours fail closed. To recover an uncertain/dead request, reconcile its existing core row/comment marker before sending a new command (which has a new update ID). Never blindly resubmit or remove an idempotency record. There is no exactly-once Telegram reply guarantee.

## Privacy and limits

Only explicit decision/rationale fields, a configured non-sensitive actor label, channel, original timestamp and opaque marker reach the core/Agiflow. The gateway returns no raw provider errors and logs no request bodies. Bot inbound storage remains the existing private transport database; it is not training data.

Known credential, bearer, token, private-key, credential-URL, email and Iranian mobile patterns are redacted before queuing. This is bounded pattern detection, not a universal privacy guarantee. Operators must provide text suitable for project collaborators, without patient/private information or credentials. User-authored notes remain data and do not approve deployment or change protected policy.

Each field is limited to 2,000 characters; requests to 16 KiB; JSON duplicate keys and unexpected fields fail closed. Socket input has a three-second total deadline. Upstream HTTP has eight-second socket timeouts and a 1 MiB response cap; the bot allows 40 seconds for three context reads and core receipt. A trusted upstream trickling bytes can exceed an HTTP inactivity timeout; this is not a hard wall-clock SLA. HTTP redirects and environment proxies are disabled; provider URL must be HTTPS and core URL numeric loopback HTTP.

## Installation and activation gates

1. Keep AAX-24 supported provider access and consumer canary/rollback gates in force. Confirm the source revision and independently review the gateway/consumer stack. This producer is unusable while supported task reads remain denied.
2. The existing bot account `adabot` must exist, be non-root and exclusively own the bot process. The installer creates a separate `ada-decision-gateway` system user; its group is `adabot` for socket access only. The gateway's credential environment remains root-only mode 0600.
3. Run `sudo ops/agiflow-decision-gateway/install.sh` from the accepted source checkout. It copies source/unit/docs, creates a disabled environment template if absent, reloads unit definitions, and does **not** enable or start either service.
4. An authorised operator configures `/etc/ada-decision-gateway.env` privately. Required: `ADA_BOT_UID` (numeric UID of adabot), `ADA_OPERATOR_USER_ID`, `ADA_OPERATOR_CHAT_ID` (same private pair as bot), `ADA_TELEGRAM_BOT_ID` (stable numeric getMe identity), `ADA_OPERATOR_LABEL` (non-sensitive ASCII display label), supported `AGIFLOW_MCP_URL`, protected `AGIFLOW_API_KEY`, and `CONTROL_API_TOKEN`. Core defaults to `http://127.0.0.1:8770`. No credential belongs in the bot environment.
5. Only after explicit production acceptance, set gateway `ADA_DECISIONS_ENABLED=true`, start its service, and confirm protected socket owner/group/mode. Install the accepted bot source through its existing installer and set bot `ADA_DECISIONS_ENABLED=true` before its authorised restart. The source bot unit already permits AF_UNIX; no writable exception for the socket directory is necessary to connect to a Unix socket.
6. Verify a permitted synthetic private decision, denied foreign identity/group/forward, duplicate update, unavailable upstream, unknown target, secret pattern and kill switch through the agreed canary. Independently verify the core payload and Agiflow consumer receipt. Do not claim production proof from offline tests.

The gateway unit has no [Install] section; startup is deliberate, never an added replay timer. Both gates default disabled. Use the same existing consumer; do not start a second writer.

## Rollback

Disable the bot's decision gate and command ingress first; stop the gateway. Preserve all existing core obligations for the existing consumer/operator reconciliation. Do not clear core records or bot inbound state. Restore the accepted source/service backup, reload units and verify bot health through its established runbook. Remove a stale socket only when its service is stopped and ownership is verified. The process refuses unexpected filesystem objects and never unlinks a symlink.

## Verification

Focused fixtures use temporary Unix sockets, a loopback fake MCP/core HTTP server and the real consumer parser/reconciliation code. They never use production credentials or send Telegram messages. Run as a non-root account:

```sh
python -m pytest ops/agiflow-decision-gateway/tests ops/ada-telegram-bot/tests -q
```

The queue remains the sole durable owner after the private chat is deleted. Actual external persistence still requires the gated consumer to deliver and verify the marker.
