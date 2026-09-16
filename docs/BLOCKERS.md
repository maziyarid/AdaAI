# Phase-1 blocker report

Status: **code + tests restored and green in repo (27 pytest). Production import and canary not executed.**

## Blocker 1 — no live VPS / SentinelX access

**Affected:** freeze/import of `/opt/maziyar-control-core`, live MariaDB schema capture, systemd unit dump, env-name capture, production shadow wrap.

**Evidence:** this Grok Build sandbox has GitHub, not SSH/VPS MCP. `maziyar-control-core` is not a GitHub repository.

**Safest next step:** from an authorized VPS session:

1. `tar` `/opt/maziyar-control-core` excluding `.env` / secrets.
2. `mysqldump --no-data` the control-core schema (table names only is enough for a second pass).
3. `systemctl cat maziyar-control-core.service maziyar-mistral-worker.service`.
4. List environment **names** only.
5. Commit the source under `runtime/control-core-baseline/imported/` on this branch.

Until then the adapter in `runtime/control-core-baseline/adapter.py` is a client stub, not an import.

## Blocker 2 — production canary not authorized

**Affected:** first live Teznevise mutation.

**Safest next step:** run shadow mode against a real scheduled Mistral job after the control-core import. Only then request a one-resource metadata canary.

## Blocker 3 — Bible v1.4 filename vs current 2.0.0

Mission text says “Art of Writing Bible v1.4”. Canonical file in archive/agents is `skills/art-of-writing-bible/SKILL.md` **version 2.0.0** dated 2026-09-16, with history 1.0.0–1.3.0 preserved. We mirrored what exists. We did not invent a v1.4 document.

## Resolved this session (2026-09-16 continue)

- Restored `engine.py` and `test_phase1_contracts.py` from placeholders (package was unimportable).
- Authorization binds passport → agent, receipt → agent/task/site/payload/mutation/passport.
- Mutation journal requires authorize() ALLOW; apply refuses unbound journals.
- Approval tickets cannot escape receipt site/task scope.
- Snapshot-bound approvals fail closed when snapshot_hash is omitted at consume time.
- **27 pytest cases passing**.

## Non-blockers (done)

- 16 required contract tests + binding extras: passing locally.
- MariaDB additive SQL written, not applied.
- Qalam router, Bible, fa-IR UX, lexicon, medical overlay, Teznevise ZWNJ overlay mirrored with sha256 (prior session).
- Deterministic authorize / approval / journal / ZWNJ validator / shadow adapter implemented.
- HMAC receipts carry `signature_alg` + `key_id` for later Ed25519.
