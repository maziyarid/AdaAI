# AAX-8 — genuine non-mutating Mistral shadow canary

Status: **designed and fail-closed in-repo. Live worker chat not executed.**
Date: 2026-09-19. Live worker source inspected via `grok-ada-readonly`
`cat /srv/community-mcp/mistral-worker/index.mjs` (619 lines). Values of
env files were not read. `curl` to `:9102` is POLICY_DENIED on the
read-only profile. `readOnly` stayed on.

`live_mistral_job` remains **false** until a real loopback
`POST /internal/chat` returns HTTP 200. Do not infer it from
`job_type=mistral.chat`.

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

1. Real Mistral worker participates (`POST /internal/chat`)
2. Deterministic prompt (`CANARY_PROMPT` / id `aax8-mistral-shadow-canary`)
3. Worker returns `{choices[0].message.content, model, usage}`
4. No production mutation capability in the path (loopback chat only)
5. Ada `ShadowPipeline.evaluate` runs on a harmless metadata proposal
6. Proposal does not authorise a write
7. No WordPress write, no Teznevise write, no production SQL
8. No completion transition from the proposal
9. Independent evidence HMAC-sealed
10. Postcondition/rollback remain non-mutating
11. `live_mistral_job=true` only if `executed=True` on that POST

## Human execute (VPS loopback, after approval)

`grok-ada-readonly` cannot POST. A human or a future allowlisted
loopback helper should:

```bash
# 1. liveness (not participation)
curl -sS -m 3 http://127.0.0.1:9102/healthz
# expect {"ok":true,...,"version":"1.3.1"}

# 2. shadow chat (participation). Loopback only. No job enqueue.
curl -sS -m 90 http://127.0.0.1:9102/internal/chat \
  -H 'content-type: application/json' \
  -d '{"prompt":"Ada AAX-8 non-mutating shadow canary. Reply with exactly SHADOW_OK and nothing else. Do not propose WordPress, SQL, Teznevise, schedule, or job changes.","temperature":0,"max_tokens":32}'
```

Feed the JSON into `MistralShadowCanary.run(participation={... executed: True ...})`
on a trusted host. Capture HMAC evidence. Do not copy the API key.
Do not call `/mcp`. Do not POST `/jobs`.

## Repository proof this cycle

`ada_reliability.mistral_shadow_canary`:

- fixtures keep `live_mistral_job=false`
- forbidden worker actions raise `CANARY_MUTATION_ROUTE`
- parent `ShadowPipeline` still HMAC-seals and does not journal
- job_type `mistral.chat` is not participation

AC1 / AC3 / AC4 stay **OPEN** until the loopback POST is actually run.

PRODUCTION_SQL: **NONE**. PRODUCTION_MUTATION: **NONE**.
