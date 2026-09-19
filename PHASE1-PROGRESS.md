# Phase 1 reliability progress log

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
