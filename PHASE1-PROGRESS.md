# Phase 1 reliability progress log

## 2026-09-19T10:05Z — Greptile P1 on 57e0fed: live Mistral evidence cannot be a dict

**Fetched HEAD:** `57e0fedc9583f0c8c24221875f5b535961b47c29` (matches origin).
Greptile independently reviewed that SHA at **3/5** (PR body last-reviewed
commit is this SHA) with **P1 Security**: `MistralShadowCanary.run()`
accepted a caller-created `participation` dictionary as proof that
`/internal/chat` ran, then HMAC-signed `live_mistral_canary` without a
transport result or worker receipt. Valid. Did not dismiss.
Reproduction matched: urllib/http patched to fail, well-formed dict
still minted live evidence on 57e0fed.

### Fix
- `participation=` never sets `live_mistral_job` / `mistral_participated`.
- Live bind requires `transport.execute_internal_chat` actually invoked
  with a per-run challenge the result must echo.
- Optional worker HMAC must use a key distinct from the canary engine key.
- `UrllibLoopbackChatTransport` POSTs only loopback `/internal/chat`.
- HMAC still covers the full record; flipping live flags fails verify.

### Live evidence this session
- Ada-readonly: `ls /usr/local/bin/ada-inspect` → ENOENT.
  `ls /opt/maziyar-control-core` present. `readOnly` stayed on.
  Royadarman not used. AAX-3 AC3 still open.
- No VPS `POST /internal/chat`. No WP write. No production SQL.
- CI on `57e0fed`: pytest jobs failed in ~2s (`runner_id` unassigned
  historically). Do not rewrite app code.
- Local suite **231 passed**. Critical files unchanged
  (engine 71704, outbox 40345).

### Not claimed
- Live `SHOW TABLES`. Production SQL. Merge of PR #2. Live Mistral POST.
- Greptile 5/5 on this fix (not yet pushed/reviewed).
- AAX-8 AC1/AC3/AC4 stay OPEN.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.



## 2026-09-19T09:40Z — backup/checkpoint contract + Mistral loopback canary (not executed)

**Fetched HEAD:** `e529bc4c3cca9171675dafba8645724af4777a3a` (matches origin).
Greptile independently reviewed that SHA at **4/5** (check
`105874371957`, completed 09:25:04Z) with **P1**: isolated rehearsal
could DROP `ada_isolated_rehearsal` on a long-lived MariaDB whose
socket happened to be under `/tmp` with `skip_networking=ON`. Valid.
Did not dismiss. Fix in this commit: require disposable marker token
plus `datadir`/`pid_file` under `/tmp/` before any DROP/CREATE.

### Live evidence this session
- Ada-readonly reconfirm: `ls /usr/local/bin/ada-inspect` → ENOENT.
  `readOnly` stayed on. Royadarman not used. `curl` `:9102` POLICY_DENIED.
- Live Mistral worker source inspected (`cat` of
  `/srv/community-mcp/mistral-worker/index.mjs`, 619 lines):
  `GET /healthz` (v1.3.1), loopback-only `POST /internal/chat` (no job
  enqueue, credential stays in worker), MCP tools include mutating
  `mistral_local_create_job`. No WordPress route in that file.
- AAX-7 AC1: production-safe encrypted backup / schema checkpoint /
  checksum / restore-drill / retention / rollback-trigger command plan
  (`docs/AAX7-BACKUP-CHECKPOINT.md` + dry-run
  `scripts/backup_checkpoint_plan.py`). Production `mysqldump` not run.
  Isolated apply/rollback already existed; encrypt+off-host still needs
  mazcontrol.
- AAX-8: fail-closed `MistralShadowCanary`. `live_mistral_job` stays
  false without an executed loopback `/internal/chat`. No WP write.
  No job enqueue. AC1/AC3/AC4 stay OPEN.
- CI on `e529bc4`: pytest jobs `105874365831` / `105874359368`,
  `runner_id=0`, ~2s, logs 404. Do not rewrite app code.
- Local suite **222 passed**. Critical files unchanged
  (engine 71704, outbox 40345).

### Not claimed
- Live `SHOW TABLES`. Production SQL. Merge of PR #2. Live Mistral POST.
- Greptile 5/5 on `e529bc4` (it is 4/5 P1; fix is in this commit, not yet re-reviewed).

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.


## 2026-09-19T09:20Z — Greptile 5/5 on 797bc3f; isolated MariaDB rehearsal

**Fetched HEAD:** `797bc3ff10417a7c7f696fdb0f42b9e144754719` (matches origin).
Greptile independently reviewed that SHA at **5/5** (check
`105872277622`, completed 09:05:49Z, conclusion success). PR body
last-reviewed commit is this SHA. 0 P0/P1. Do not add more
repository-only AAX-8 unit tests.

### Live evidence this session
- Ada-readonly reconfirm: hostname `server.maziyarid.com`,
  `/opt/maziyar-control-core` present, `control_core.py` 65370 bytes.
  `ls /usr/local/bin/ada-inspect` → ENOENT. `sudo -n -u mazcontrol
  /usr/local/bin/ada-inspect tables` → POLICY_DENIED (`readOnly`
  stayed on). Royadarman not used. AAX-3 AC3 still open.
- AAX-7: **real isolated MariaDB 10.11.11** rehearsal, skip-networking
  unix socket, not production. Live source SCHEMA + seed, `001`–`006`
  apply twice, unique/idempotency 1062, CAS claim_generation, 28
  `ada_*`, protected jobs/schedules unchanged, rollback restored the
  20-table baseline. Quoted reserved `` `release` `` in 002/004.
  Report: `docs/AAX7-ISOLATED-MARIADB-REHEARSAL.json`.
- AAX-8: no genuine Mistral participation this cycle. No WP write.
  `live_mistral_job` remains false. AC1/AC3/AC4 stay OPEN.
- Local suite **209 passed**. Critical files unchanged
  (engine 71704, outbox 40345).
- CI on `797bc3f`: pytest jobs `105872274489` / `105872266095`,
  `runner_id=0`, ~2s. Do not rewrite app code.

### Not claimed
- Live `SHOW TABLES`. Production SQL. Merge of PR #2. Live Mistral.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.



## 2026-09-19T09:10Z — Greptile 5/5 on 5d331d7; AAX-8 wrapper/escalation proofs

**Fetched HEAD:** `5d331d736c44849c1dd2a0ad11bfed46dc911307`.
Greptile independently reviewed that SHA at **5/5** (check completed
08:56:11Z, check `105871068043`). No P0/P1. Parent `e3bd2c7` was 3/5
P1 (live-read alias); that fix is what Greptile just scored.

### Done this session
- Ada-readonly reconfirm: hostname `server.maziyarid.com`,
  `/opt/maziyar-control-core` present, `ls /usr/local/bin/ada-inspect`
  → ENOENT. `readOnly` stayed on. Royadarman not used. AAX-3 AC3 still
  open. Close AC3 only from live `SHOW TABLES`.
- AAX-8 repository fail-closed: live-read gate walks
  `ControlCoreAdapter` subclasses and wrappers (`inner` / bound
  `get_job.__self__`), not just class-name equality. Path/URL/padded
  `live_job_id` values never reach `get_job`. Stale job statuses,
  forged approvals, matching postconditions, and
  `allow_live_job_read=True` on a fake adapter still cannot journal or
  apply a write. Sealed `mutated=True` cannot prove postcondition.
  Rollback remains evidence-only. Local suite **209 passed**.
- CI on `5d331d7`: jobs `105871061433` / `105871054069`, `runner_id=0`,
  ~2s, logs 404, Actions banner still "You can't perform that action
  at this time." Not a pytest failure. Do not rewrite app code.
- SQL not applied. AAX-8 AC1/AC3/AC4 unchecked. AAX-12/AAX-15 Review.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.


## 2026-09-19T08:55Z — Greptile P1 live-read alias + AAX-8 identity mismatch

**Fetched HEAD:** `e3bd2c7c90ba86c2ad8b171e8f3f806c9749fc49`.
Greptile independently reviewed that SHA at **3/5** (check completed
08:46:11Z, check `105869568594`). P1 Security: live-read gate could be
bypassed by a hostname alias that is not the literal
`127.0.0.1:8770` / `localhost:8770`. Valid. Did not dismiss.

### Done this session
- Ada-readonly reconfirm: `ls /usr/local/bin/ada-inspect` → ENOENT.
  `readOnly` stayed on. Royadarman not used. AAX-3 AC3 still open.
- P1 fix: `adapter_targets_live_control_core` treats **any** configured
  `base_url` (and the `ControlCoreAdapter` class) as a live/network
  target. Hostname aliases, IPv6 loopback, and bearer tokens never
  reach HTTP when `allow_live_job_read` is false.
- AAX-8: requested `live_job_id` must match returned `id` or
  `stable_id` (`live_job_id_mismatch`). Empty ids deny. Mutation
  families (`wp_publish`, `wp_delete`, `apply_sql`, `POLICY_CHANGE`,
  `CANONICAL_OWNERSHIP`) stay non-ALLOW with a bound job; rollback is
  not executed. HMAC fails if `live_job_context` / `live_job_id` is
  swapped across jobs. Local suite **201 passed**.
- CI: `e3bd2c7` job `105869561606` still `runner_id=0`, logs 404.
  Actions page banner: "You can't perform that action at this time."
  Account/policy restriction, not a pytest failure. Do not rewrite app
  code.
- SQL not applied. AAX-8 AC1/AC3/AC4 unchecked. AAX-12/AAX-15 Review.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.


## 2026-09-19T09:05Z — AAX-7 isolated inventory rehearsal + AAX-8 live-adapter deny

**Fetched HEAD:** `27ffc513ef7e9bb68fa7dd988210049646f930d0`.
Greptile independently reviewed that SHA at **5/5** (check completed
08:33:25Z, check `105868399364`). No new P0/P1. Parent `d7537ca` was
also 5/5. PR #2 open, not merged, `mergeable_state=unstable`.

### Done this session
- Ada-readonly reconfirm: hostname `server.maziyarid.com`,
  `/opt/maziyar-control-core` present, `/usr/local/bin/ada-inspect`
  still ENOENT. `readOnly` stayed on. Royadarman not used. AAX-3 AC3
  still open. Close AC3 only from live `SHOW TABLES`.
- AAX-7: in-memory inventory rehearsal of `001`–`006` against the live
  source table set. 20 protected control-core tables unchanged; only
  `ada_*` names added; rollback restores the starting set. No MariaDB
  connection. No production SQL. Responsibility map now covers
  persistence, failure records, leases, claim generation, retry,
  idempotency, dead-letter, quarantine, external sync, Agiflow handoff.
  `006` comments no longer claim live `pd_*` tables exist.
- AAX-8: unauthorised `ControlCoreAdapter` `live_job_id` reads fail
  closed (`live_adapter_read_not_authorised`) without HTTP. Write-capable
  adapters with `get_job` still rejected. Fake-adapter `wp_publish`
  denial from `27ffc51` unchanged.
- Do **not** check AAX-8 AC1/AC3/AC4. Do **not** check AAX-7 ACs.
- Hosted Actions on `27ffc51`: `runner_id=0`, ~2s, pytest never
  started (jobs `105868392628` / `105868388833`). Do not rewrite app
  code for this.
- SQL not applied. AAX-12/AAX-15 remain Review.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.



## 2026-09-19T08:40Z — AAX-8 bound job id does not grant wp_publish

**Fetched HEAD:** `d7537cada013e278552354411ac09707562ec30d`.
Greptile independently reviewed that SHA at **5/5** (check completed
08:25:18Z). No new P0/P1. PR #2 open, not merged,
`mergeable_state=unstable`.

### Done this session
- Ada-readonly reconfirm: `/usr/local/bin/ada-inspect` still ENOENT.
  `readOnly` stayed on. Royadarman not used. AAX-3 AC3 still open.
- AAX-8: bound `live_job_id` (fake adapter, `mistral.chat` identity)
  plus a `wp_publish` proposal is still DENY. No WordPress write, no
  apply, task stays SHADOW, postcondition not proven, rollback not
  executed, job payload not copied, HMAC covers the evidence. Local
  suite **188 passed**.
- This remains repository/adapter-read proof. Do **not** check AAX-8
  AC1/AC3/AC4.
- Hosted Actions on `d7537ca` still fail in ~2s (`runner_id=0`, job
  `105867421213`). Do not rewrite app code for this.
- SQL not applied. AAX-12/AAX-15 remain Review.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.


## 2026-09-19T08:25Z — AAX-8 read-only live job shape (not AC1)

**Fetched HEAD:** `ae4fd13af8b137e3f39bdc0cb19cac583960762a`.
Greptile independently reviewed that SHA at **5/5** (check completed
08:15:09Z). Prior HMAC P1 remains closed. No new P0/P1. PR #2 open,
not merged, `mergeable_state=unstable`.

### Done this session
- Ada-readonly reconfirm: hostname `server.maziyarid.com`,
  `/usr/local/bin/ada-inspect` still ENOENT. `readOnly` stayed on.
  Royadarman not used. AAX-3 AC3 still open. Close AC3 only from live
  `SHOW TABLES`.
- AAX-8: optional `live_job_id` binds secret-free job identity via
  read-only `adapter.get_job`. Missing adapter / read failure /
  unknown `job_type` fail closed. `payload_json` is never copied.
  Evidence is labelled `evidence_kind=adapter_job_read` and
  `live_mistral_job=false` / `mistral_participated=false` even when
  the bound type is `mistral.chat`. HMAC covers the new fields.
  Local suite **187 passed**.
- This is still repository/adapter-read proof. Do **not** check AAX-8
  AC1/AC3/AC4.
- Hosted Actions on `ae4fd13` still fail in ~2s (`runner_id=0`, job
  `105866075903`). Do not rewrite app code for this.
- SQL not applied. AAX-12/AAX-15 remain Review.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.


## 2026-09-19T08:15Z — AAX-8 independent postcondition/rollback evidence (in-repo)

**Fetched HEAD:** `58e64c788bbea747251a82c4d5a8c68bd15a7cda`.
Greptile independently reviewed that SHA at **5/5** (PR body last
reviewed commit matches HEAD). Prior HMAC P1 closed. No new P0/P1.
PR #2 open, not merged, `mergeable_state=unstable`.

### Done this session
- Ada-readonly reconfirm: hostname `server.maziyarid.com`,
  `/opt/maziyar-control-core` present, `/usr/local/bin/ada-inspect`
  still ENOENT. `readOnly` stayed on. Royadarman not used. AAX-3 AC3
  still open. Close AC3 only from live `SHOW TABLES`.
- AAX-8: `prove_postcondition` HMAC-verifies the evaluate record first,
  independently checks expected vs FakeWordPress live, and never
  completes the task. `rollback` records a DENY plan and never
  executes a production rollback. Snapshot schedule binding is
  labelled `live_mistral_job=false`. Local suite **180 passed**.
- Hosted Actions on `58e64c7` still fail in ~2s (`runner_id=0`).
  Do not rewrite app code for this.
- SQL not applied. AAX-8 AC1/AC3/AC4 remain unchecked (no live
  Mistral / live postcondition canary). AAX-12/AAX-15 remain Review.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.


## 2026-09-19T08:00Z — AAX-8 HMAC covers the full evaluation record

**Fetched HEAD:** `1a1c995f87978f0c1d00dea6954a4792debea0d2`.
Greptile independently reviewed that SHA at **3/5** with **P1 Security**
on `unsigned_evidence()` (discussion_r4052536047). PR #2 open, not merged.

### Done this session
- Ada-readonly reconfirm: hostname `server.maziyarid.com`,
  `/opt/maziyar-control-core` present, `/usr/local/bin/ada-inspect`
  still ENOENT. `readOnly` stayed on. Royadarman not used. AAX-3 AC3
  still open.
- Greptile P1: HMAC body is now the full record minus `evidence_hmac`.
  `adaeval`, `proposal`, `expected_postcondition`, `qalam_release`,
  `evidence_alg`, and `evidence_key_id` are bound. Tampering any of
  them fails `verify_evidence()`.
- Hosted Actions on `1a1c995` still fail in ~2s (runner never assigned).
  Do not rewrite app code for this.
- Local suite **174 passed**. SQL not applied. AAX-8 AC1/AC3/AC4 remain
  unchecked. AAX-12/AAX-15 remain Review.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.


## 2026-09-19T07:35Z — AAX-8 signed evidence; schema still blocked

**Fetched HEAD:** `ca08ec64ba5e0344158e8a5ff4021ba6772de25c`.
Greptile Review check **in_progress** on that SHA (no P0/P1 published). Last completed Greptile 5/5 remains `d7e41a6`. PR #2 open, not merged.

### Done this session
- Ada-readonly reconfirm: `ada-inspect` still ENOENT on `server.maziyarid.com`.
  `readOnly` stayed on. Royadarman not used. AAX-3 AC3 still open.
- AAX-8: HMAC-seal shadow evidence (`hmac-sha256` + `key_id`). Unknown
  `live_schedule_stable_id` DENY without creating an engine task (no
  invented second scheduler). `wp_publish` DENY, no FakeWordPress writes.
  Adapter may `get_job`/`health`; `claim_job` / `release_due_schedules`
  forbidden. Tampered evidence fails verify.
- Local suite **173 passed**. SQL not applied.

### Not done
- AAX-3 AC3 live `SHOW TABLES`.
- Hosted Actions still `runner_id=0`.
- Production SQL. Merge. Deploy. Live Mistral/Teznevise canary.
- AAX-12 / AAX-15 remain Review.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.



## 2026-09-19T07:15Z — AAX-8 in-repo shadow pipeline; AAX-7 source map

**Fetched HEAD:** `d7e41a6c2d8fbf64e0e8de740f74bd77976ebb19` (unchanged until this push).
Greptile **5/5** on that exact SHA. PR #2 open, not merged, `mergeable_state=unstable`.

### Done this session
- Ada-readonly reconfirm: hostname `server.maziyarid.com`,
  `/opt/maziyar-control-core` present, `/usr/local/bin/ada-inspect`
  still ENOENT. `readOnly` stayed on. Royadarman not used.
- AAX-8 `ShadowPipeline`: binds live snapshot schedule identities,
  asserts adapter has no write/lease/SQL surface, wraps
  `shadow_mistral`, records evidence, STOP. No WordPress write,
  no SQL, no second scheduler.
- AAX-7 `docs/AAX7-SOURCE-VS-MIGRATION.md`: source-vs-migration
  classification (already provided / complementary / overlapping /
  still missing). **STOP before Apply.** 006 retained as complementary
  only if live has no `pd_outbox`.
- Local suite **170 passed** (161 baseline + 9 new). Imports
  `AdaEngine` / `seed_phase1` / `FailedRunOutbox` / `ShadowPipeline`
  OK. Zero placeholders. engine 71704 / outbox 40345 unchanged.

### Not done
- AAX-3 AC3 live `SHOW TABLES`.
- Production SQL. Merge. Deploy. Live Mistral/Teznevise canary.
- Hosted Actions still `runner_id=0` (public repo; not private minutes).

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.


## 2026-09-19T06:42Z — AAX-3 live source snapshot imported (AC2)

**Fetched HEAD:** `cd7c63c0fb25ecdb7e1e9eebb4499797441bb6ff`.
Implementation parent still Greptile **5/5**. PR #2 open, not merged.

### Done this session
- Ada-readonly `cat` of `/opt/maziyar-control-core/control_core.py`
  (65370 bytes / 1096 lines). No env values. No `ada_*` / `pd_*`
  names in source.
- Imported snapshot to `runtime/control-core-baseline/live/` plus
  unit file. SHA-256 of **captured bytes**:
  `aec6639acf761dfb01a72feb670b4d841c25fb1e8000abdea41bca0dcf4a94f3`.
  Host `sha256sum` still POLICY_DENIED.
- Contract tests parse the snapshot: 20 tables, `INSERT IGNORE`
  idempotency, `FOR UPDATE SKIP LOCKED` claim, six seeded schedules,
  `/health` behind Bearer, env-only credentials.
- `clickup_state_steward.py` remains mode-denied. `ada-inspect`
  still not installed.

### Not done
- AC3 live `SHOW TABLES` (source absence of `ada_*` is not MariaDB
  proof).
- Production SQL. Merge. Deploy. Live Teznevise canary.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.



## 2026-09-19T23:20Z — mazcontrol helper prepared; AAX-3 AC2/AC3 still gated

**Fetched HEAD:** `7953eaba43bd0fe5230ae9f0b3f0370cf8a1d1ed` (unchanged).
Implementation parent `3513278` still Greptile **5/5**, 0 P0/P1.
PR #2 open, `mergeable_state=unstable` because Actions `runner_id=0`.

### Done this session
- Independent Ada-readonly reconfirm (Add A profile `grok-ada-readonly`).
- In-repo least-privilege helper `ops/mazcontrol-readonly/ada-inspect`
  (units/hashes/schema-only). **Not installed on VPS.**
- Local clean venv: **149 passed**. Import OK. Critical files non-empty
  (outbox 40345 / tests 27521 / engine 71704). Zero source placeholders.

### Not done
- Helper/sudoers/MCP allowlist install (needs Maziyar).
- Live `SHOW TABLES` / ActiveState / sha256.
- Production SQL. Merge. Deploy.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.


## 2026-09-19 — AAX-15 restore + Greptile P1s (atomic claim / no silent succeed)

**Fetched HEAD:** `4caefb5970b3d6245ce11801f59b07d0df2b4584` (placeholders).
**Baseline restored from:** `903da122dcb26e63bd3ab707e8f0a96321fcfc40` via real git checkout, not Contents API.

### What was broken on fetched HEAD
Contents-API commits `574b670` / `4caefb5` replaced
`failed_run_outbox.py` with `PLACEHOLDER_WILL_BE_REPLACED` and
`test_failed_run_outbox.py` with `TEMP_SEE_NEXT`. Greptile 1/5:
broken package import plus the three original outbox P1s.

### Done this session (in-repo)
- Restored both files from `903da12` (26 outbox tests kept; uniqueness HMAC + AAX-15 distinctness kept).
- P1 #1: `FailedRunStore.claim_if_eligible` compare-and-set. `claim_batch` owns a row only if still queued/retryable/due. In-memory lock is atomicity; MariaDB must `UPDATE ... WHERE lifecycle IN ('queued','retryable')`.
- P1 #2: `engine_retry` FAILED / EXECUTING / unknown statuses requeue or park. Only `APPLIED` / `DUPLICATE_SKIPPED` become terminal succeeded.
- P1 #3: unknown `mutation_kind` parked on persist against `SUPPORTED_MUTATION_KINDS`; legacy/corrupt rows parked on replay.
- 6 new regressions. Full suite **141 passed**. Clean venv import of `AdaEngine` / `FailedRunOutbox` works.
- SQL 006 documents the CAS claim. **Not applied.**

### Not claimed
- Live VPS re-canary. ChatGPT AAX-12/AAX-15 live ACs stay checked; this is repository proof only.
- Production SQL. Merge of PR #2 as deployed.

### Phase B (same session, read-only)
VPS MCP is configured. Ada control-core was **not** imported:
- Content `grok-royadarman` connected, but `/opt/maziyar-control-core` is absent (Royadarman host).
- Eqialise `grok-ada-readonly` disconnected (HTTP 502 / timeout). AAX-3 stays Blocked.
See `docs/BLOCKERS.md`.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.

## 2026-09-18 — AAX-15 in-repo failed-run outbox (distinct from AAX-12)

**Session:** continue Phase 1 from fetched HEAD `1eabaad`. Greptile on that SHA: 5/5, 0 blocking issues. PR #2: 32 review threads, 0 unresolved.

### Done this session
- Added `ada_reliability.failed_run_outbox` as **execution recovery**, not Agiflow projection.
  Distinct from `ada_agiflow_outbox` (AAX-12).
- Lifecycle: queued / retryable / inflight / parked / succeeded / dead_letter / quarantined.
- `FACTORY_PACKET_MISSING`, packet-pipeline and exit 137/SIGKILL park with reset conditions and do not hot-loop.
- Workers report `replay=queued|parked|retryable` only after persist; otherwise `replay=UNAVAILABLE`.
- Replay is bounded, ordered by `first_failed_at`, lease-aware, idempotent. WordPress/packet mutations are not applied by this module; duplicates skip via a mutation ledger. Agiflow catch-up goes through AAX-12 `project(evidence_id=...)`.
- Additive SQL `006_ada_failed_run_outbox.sql` (`ada_failed_runs`, `ada_failed_run_events`). Not applied.
- In-process dump/load simulates process restart. This is **not** VPS MariaDB persistence.

### Not claimed
- Live schema on control-core MariaDB.
- Live worker restart survival.
- Live scheduled-failure accumulation / replay canary.
- ChatGPT's VPS `pd_worker_runs` / `pd_outbox` work is recorded on AAX-15; this session did not re-verify the host.

### Still blocked
1. No SSH/SentinelX this session → AAX-3 live control-core import.
2. Production SQL not applied (AAX-7). Reconcile `ada_failed_runs` with live `pd_*` before apply.
3. Live Teznevise canary not authorized (AAX-8).
4. AAX-12 AC5 live board canary still needs VPS.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.

## 2026-09-18 — AAX-12 Greptile P1: HMAC-issued evidence (not caller-constructed)


**Session:** continue Phase 1. Greptile on `cb0b1b7` scored 3/5: Review/Done could be projected from a caller-built `ProjectionEvidence(verified=True, ...)`. Valid. Did not dismiss.

### Done this session
- Removed `ProjectionEvidence`. Review requires `issue_evidence` from a trusted verifier (`verifier`, `ada_service`) and trusted source (`runtime`/`live`). HMAC-SHA256 over `{durable_job_id, live_hash, verifier_identity, source}`.
- Done additionally requires a one-time `issue_close_grant` from `human_approver`, HMAC-bound to job+evidence, consumed after successful Done.
- `project()` takes `evidence_id` / `close_grant_id` only. Unknown, job-mismatched, or tampered HMAC records fail closed (`UNKNOWN_EVIDENCE`, `FORGED_EVIDENCE`, `CLOSE_GRANT_CONSUMED`, …).
- Caller-constructed `IssuedEvidence` / `CloseGrant` dataclasses are handles, not proofs: store lookup fails.
- Outbox payload is `{evidence_id, close_grant_id}` — no forgeable `verified` / identity fields.
- Additive SQL: `ada_agiflow_evidence`, `ada_agiflow_close_grants`. Not applied.
- ADR-0003 item 7 updated. Package no longer exports `ProjectionEvidence`.

### Still blocked
1. No SSH/SentinelX this session → AAX-3 live control-core import.
2. Production SQL not applied (AAX-7).
3. Live Teznevise canary not authorized (AAX-8).
4. Live durable-job → Agiflow board canary (AAX-12 last AC) needs VPS.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.

## 2026-09-18 — AAX-12 Agiflow state steward (in-repo, no VPS)

**Session:** continue Phase 1 after AAX-2 Review at `16b78c9`. Greptile on that SHA: merge-safe, 5/5, 0 blocking issues.

### Done this session
- Implemented `ada_reliability.agiflow_steward` against ADR-0003:
  stable durable-job ↔ Agiflow-task mapping, runtime-state projection,
  evidence-backed Review/Done, human-edit conflict preservation,
  durable outbox + idempotent replay, projection rollback that does not
  mutate runtime jobs.
- Steward cannot enqueue/lease/schedule and cannot call Agiflow execute.
- ClickUp is accepted only as an ignored spy; tests prove it is never called.
- Additive SQL `005_ada_agiflow_projection.sql` (`ada_agiflow_task_map`,
  `ada_agiflow_outbox`, `ada_agiflow_projection_events`). Not applied.
- In-process canary covers queued → In Progress → outage → verified Review
  → projection rollback. This is **not** a live VPS canary.

### Still blocked
1. No SSH/SentinelX this session → AAX-3 live control-core import.
2. Production SQL not applied (AAX-7).
3. Live Teznevise canary not authorized (AAX-8).
4. Live durable-job → Agiflow board canary (AAX-12 last AC) needs VPS + mapping to a real Agiflow project.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.

## 2026-09-17 — AAX-1 restore + AAX-2 fail-closed bindings (Grok)

**Session:** Grok with GitHub + Agiflow. PR head before this commit: `66c850df9eacbd9c55e496d1d7bbd5fb104c52c2`.

### Evidence (do not treat older "33 pytest green locally" claims as completion)
- Remote `engine.py` and `test_phase1_contracts.py` were still placeholders at that SHA.
- Recovered the complete engine/tests from git history `2c5e723` (1075-line engine, 588-line contracts). Later "restore" commits did not actually land the blobs (GitHub Contents API size).
- Restored via `git checkout 2c5e723 -- …` then applied fail-closed hardenings. Push is a real git commit, not the Contents API.

### Done this session
- Restored `ada-reliability/src/ada_reliability/engine.py` and `tests/test_phase1_contracts.py`.
- Added `mutations.py` and `qalam_release.py`.
- Fail-closed: passport bound to agent + stored version; empty `allowed_sites` denies; receipt agent/task/site/payload/passport/mutation binding; approval stays inside receipt scope; snapshot required when ticket bound one; journal/apply require matching ALLOW + live receipt; policy receipts hash the ACTIVE asset bundle (real files when present), not a placeholder string.
- Authoritative Qalam pointer: `skills/qalam/RELEASE.json`. Router 1.1.0 and Bible 2.0.0 stay independent; eval pack 1.3.0 validates Bible 2.0.0.
- Overlay paths reconciled to `skills/qalam/fa-ir-overlays/*`. Loading plan is deterministic (router + Bible + every listed profile overlay + Bible companions).
- MariaDB: `path_hash` PK (no `path(191)` unique); one-ACTIVE unique generated column.
- Migration runbook precondition 5 now admits the bootstrap `INSERT IGNORE`.
- GitHub Actions workflow `.github/workflows/ada-reliability.yml` (may still be blocked by repo Actions policy; this session also ran a clean venv `pip install -e` + pytest).
- **43 pytest passed** from the working tree, including an isolated venv install/import.

### Production
- SQL not applied.
- No live Teznevise canary.
- This session has GitHub + Agiflow, not SSH to `/opt/maziyar-control-core`. AAX-3 remains blocked here even if another agent has VPS.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.

## 2026-09-17 — continue: split engine, dialect review, job contracts


**Session:** continue AdaAI Phase 1 reliability work (no VPS).

### Done this session
- Reconfirmed local engine **33 pytest green** (27 contract + adapter + 4 job/schedule/lease regressions).
- Split engine into `models.py`, `engine.py`, `mutations.py`, `seed.py` so the package can be pushed in smaller files.
- Pushed `models.py` + `seed.py` to `phase1/reliability-layer`.
- Added `docs/MARIADB-DIALECT-REVIEW.md` (document-only; SQL not applied).
- Added `tests/test_live_job_contracts.py` for documented jobs/schedules/leases/retries/DLQ (no VPS call).
- Packaged restored sources as `ada-reliability-restored.zip` for a host that can `git add` the remaining large files.

### Still on the branch as placeholders until a git push of the zip contents
- `engine.py` (still placeholder on remote)
- `test_phase1_contracts.py` (still placeholder on remote)
- `mutations.py` (local only until pushed)

### Still blocked
1. No VPS/SentinelX → cannot import `/opt/maziyar-control-core`.
2. Production SQL not applied.
3. Live Teznevise canary not authorized.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.

## 2026-09-17 — restore full engine + contract tests (no VPS)

**Session:** continue Phase 1 reliability (VPS still unavailable).

### Done this session
- Restored `ada-reliability/src/ada_reliability/engine.py` from last complete
  historical blob (`2c5e723` / `4f1fb06`, 1075 lines) after remote had only
  the `PLACEHOLDER_WILL_BE_REPLACED` stub.
- Restored `tests/test_phase1_contracts.py` (22 contract cases + helpers).
- Re-exported `seed_phase1` from `seed.py` so package imports stay coherent
  with the dict-based engine API used by tests.
- **28 pytest green** locally: 22 phase1 contracts + 2 adapter + 4 live
  job/schedule/lease regressions.
- Confirmed models.py remains valid dataclasses (supplementary shapes).
- Confirmed MariaDB dialect review and SQL remain document-only / not applied.
- No VPS import, no production SQL apply, no Teznevise canary.

### Still blocked
1. No VPS/SentinelX → cannot import `/opt/maziyar-control-core`.
2. Production SQL not applied (needs backup + restore drill + approval).
3. Live Teznevise canary not authorized.

### Rule
Models propose. Deterministic code authorizes. Independent validators prove the live result.
