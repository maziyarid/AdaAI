# AAX-8 — genuine non-mutating Mistral shadow canary

Status: **live non-mutating Mistral shadow E2E executed successfully; AAX-8 is Review.**
Date: 2026-09-19. Live worker source inspected via `grok-ada-readonly`
`cat /srv/community-mcp/mistral-worker/index.mjs` (619 lines). Values of
env files were not read. `curl` to `:9102` is POLICY_DENIED on the
read-only profile. `readOnly` stayed on.

`live_mistral_job` remains **false** unless `MistralShadowCanary.run()`
**invokes** a transport `execute_internal_chat` (challenge echoed) or
verifies a worker HMAC on that result with a key distinct from the
canary engine HMAC. A caller-created `participation` dict is **never**
live proof. Do not infer participation from `job_type=mistral.chat`.

Rule: models propose. Deterministic code authorizes. Independent
validators prove the live result.

## Why not a control-core `mistral.chat` job

Live `control_core.py` `handle_job` for `mistral.chat` calls the
Mistral HTTP API **and** `finish_job` writes `jobs` / `job_results`
(and possibly `dead_letter_queue`). That is a production mutation of
the durable queue even if the prompt is harmless.

AAX-8 forbids production mutation. Do **not** enqueue a canary job.

## Live worker (secret-free)

Unit: `maziyar-mistral-worker.service`
User: `maziyarid`
ExecStart: `/usr/bin/node /srv/community-mcp/mistral-worker/index.mjs`
Listen: `PORT` default **9102**
Env file: `/etc/maziyar-mistral-worker.env` (unread)

Routes:

| Route | Auth | Effect | Canary |
| --- | --- | --- | --- |
| `GET /healthz` | none | JSON `{ok, configured, version: 1.3.1}` | liveness only; **not** participation |
| `POST /internal/chat` | **loopback only** (`127.0.0.1` / `::1`) | `chat()` → `/v1/chat/completions`; credential stays in worker | **the** shadow path |
| `POST /mcp` | Bearer `MISTRAL_MCP_BEARER_TOKEN` | MCP tools including **mutating** `mistral_local_create_job` / schedules | **forbidden** |

`/internal/chat` comment in source: “Loopback-only bridge for
first-party applications on this host. The Mistral credential remains
inside this worker and is never copied into WordPress.”

No `wordpress` string in `index.mjs`. Mutation risk is the local
control-core tools (`create_job`, `create_schedule`, `execute_workflow`,
…). The canary driver denies those names (`FORBIDDEN_WORKER_ACTIONS`).

## Required canary properties (all must hold)

1. Real Mistral worker participates (`POST /internal/chat`) via an
   invoked executor (`UrllibLoopbackChatTransport` on the VPS)
2. Deterministic prompt (`CANARY_PROMPT` / id `aax8-mistral-shadow-canary`)
3. Per-run challenge is generated inside `run()` and echoed by the executor
4. Worker returns `{choices[0].message.content, model, usage}`
5. No production mutation capability in the path (loopback chat only)
6. Ada `ShadowPipeline.evaluate` runs on a harmless metadata proposal
7. Proposal does not authorise a write
8. No WordPress write, no Teznevise write, no production SQL
9. No completion transition from the proposal
10. Independent evidence HMAC-sealed; flipping `live_mistral_job` fails verify
11. Caller-supplied `participation` never sets `live_mistral_job=true`

## Human execute (VPS loopback, after approval)

`grok-ada-readonly` cannot POST. A human or a future allowlisted
loopback helper should construct `UrllibLoopbackChatTransport` on the
VPS (not a participation dict) and call `MistralShadowCanary.run(transport=...)`.

```bash
# 1. liveness (not participation)
curl -sS -m 3 http://127.0.0.1:9102/healthz
# expect {"ok":true,...,"version":"1.3.1"}

# 2. shadow chat stays inside UrllibLoopbackChatTransport.
# Do not feed a hand-built JSON dict into run(participation=...).
```

Do not copy the API key. Do not call `/mcp`. Do not POST `/jobs`.

## Repository proof this cycle

Greptile P1 on `57e0fed` (3/5): `run()` accepted a caller-created
participation dictionary as live proof and HMAC-signed
`live_mistral_canary` without invoking a transport. Fixed:

- `participation=` never sets live flags (regression:
  `test_caller_supplied_participation_never_mints_live_canary`)
- live bind requires `transport.execute_internal_chat` actually called
  with a per-run challenge the result must echo
- optional worker HMAC must use a key distinct from the canary engine key
- `UrllibLoopbackChatTransport` POSTs only `http://127.0.0.1:9102/internal/chat`

An in-process `EchoTransport` is repository binding proof, **not** VPS
evidence. AC1 / AC3 / AC4 stay **OPEN** until the loopback POST is
actually run on the VPS.

PRODUCTION_SQL: **NONE**. PRODUCTION_MUTATION: **NONE**.

## Live VPS evidence — 2026-09-19

On exact repo head `672bcd38b921bdf9c777b4a1f0942f97a22ebbea`, the live `mistral-small-latest` worker participated through the loopback-only `/internal/chat` transport. The first transport canary was challenge-bound and HMAC-valid with WordPress writes 0→0, no SQL, no enqueue, and no schedule mutation.

A stronger E2E then used the real AAX-8 Agiflow task description as task context. The live model returned the constrained metadata proposal with a fresh challenge echo. That exact model proposal was fed into `ShadowPipeline.evaluate`, then `prove_postcondition` and `rollback`. All three evidence records verified. Authorization was DENY; `postcondition_proven=false`; `task_completed=false`; `rollback_executed=false`; journal unchanged; WordPress writes 0→0; production SQL/mutation/job enqueue/schedule mutation all false.

Secret-free hashes:
- task context: `500011d1de274892a3fcb49d718e43b953475b6d3baf75d1fe5364034b7c562b`
- Mistral response: `2b37e656662c0c9ea8e1642c178b40ccae9901fc16ba9155ebceabdbceec05bb`
- evaluated proposal: `b0ca64dab2f68a56c0cbb0f22c43535cb2dfc491f3847119998ea7821d8a6f24`

The secret-free evidence summary is `docs/AAX8-LIVE-MISTRAL-E2E-EVIDENCE.json`. All AAX-8 ACs are now evidenced; Review, not Done.
