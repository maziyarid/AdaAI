# AdaAI Implementation Roadmap

This roadmap reconciles the Genspark/Gemini/Claude research with the live VPS state verified on 2026-09-16.

The target state is broad, but the build order is intentionally narrow: prove one safe end-to-end workflow before generalizing.

## Guiding rule

> Do not replace an inaccurate model with another model and call that reliability. First make unverified model output unable to become unverified production state.

## Phase 0 — protect and inventory production

Status: partially complete through live inspection.

### Completed/verified

- Existing `maziyar-control-core.service` is active on `127.0.0.1:8770`.
- Existing control core already has jobs, schedules, leases, retries, DLQ, audit, content gates, snapshots and external sync.
- Existing MariaDB 10.11 is healthy and already backs the control core.
- Existing Mistral worker is active on `127.0.0.1:9102` and already delegates durable local jobs/schedules to the control core.
- Existing WordPress/GSC/OAuth/MCP services are active.
- VPS is 4 vCPU / 3.6 GiB RAM / no NVIDIA runtime; no serious local LLM belongs here.

### Remaining

- Produce a complete MCP/tool inventory.
- Classify every tool as read / write / delete / external communication / policy mutation.
- Establish an emergency global kill switch for agent writes.
- Confirm current backup coverage for MariaDB and production files.
- Add off-host encrypted backup target.
- Test one real restore, not just backup creation.
- Document secret ownership/rotation without committing credentials.

### Exit criteria

- Recovery procedure tested.
- Every consequential tool has a mutation class.
- Emergency write-disable path works.

---

## Phase 1 — merge Ada into the existing control core

Status: **contract implemented in-repo; live VPS import and canary blocked.** See `docs/BLOCKERS.md`.

### Done in repository (2026-09-16)

- Deterministic bootstrap + scoped receipts (`ada-reliability`).
- Additive MariaDB SQL (`ada_*` tables only).
- Agent passports, `authorize()`, approval tickets, mutation journal.
- Untrusted external envelope + prompt-injection fixture.
- Teznevise zero-U+200C validator.
- Mistral shadow-mode adapter (no writes).
- Qalam registry mirrored from `maziyarid/agents` + archive Bible.
- 22 automated tests including the 18 required cases.
- Migration/rollback runbooks and ADRs.

### Not done (blocked)

- Import of live `/opt/maziyar-control-core` source (no VPS access this session).
- Applying SQL to production MariaDB.
- Wrapping a real scheduled Mistral job on the VPS.
- Live Teznevise canary.

### Explicitly defer


- pgvector;
- semantic/autonomous memory promotion;
- local LLM serving;
- multi-model routing;
- unrestricted publishing.

### Exit criteria

- Existing control-core jobs still work.
- Bootstrap returns correct P0/P1 context for test scopes.
- Only relevant dependency changes stale a receipt.
- Superseded memory remains queryable but does not override active canonical state.

---

## Phase 2 — make Qalam and Persian writing mandatory infrastructure

Goal: every user-facing writing task uses one versioned writing constitution.

### Work

- Mirror the complete current Qalam/Art-of-Writing stack into Ada's skill registry.
- Include:
  - Qalam router;
  - Art of Writing Bible v1.4 archive/current pointer;
  - `ux-writing-fa-ir.md`;
  - `fa-ir-product-lexicon.md`;
  - tool-routing rules;
  - academic/methodology/service overlays;
  - English and medical overlays;
  - site-specific policies;
  - approved examples/evaluation cases.
- Represent skill releases by immutable version/hash.
- Make `qalam_release` and relevant overlays receipt dependencies for writing tasks.
- Remove embedded replacement style prompts from workers over time.
- Replace Qalam's XMemo/Engram-primary recall with Context Core primary; XMemo/Engram remain mirrors/provenance aids.

### Exit criteria

- Persian candidate jobs cannot start without current Qalam dependencies.
- Teznevise zero-U+200C rule is deterministic and testable.
- A Qalam release change invalidates only writing tasks that depend on it.

---

## Phase 3 — authorization, approvals and hostile-input quarantine

Goal: the model can propose, but cannot authorize itself.

### Work

- Implement one deterministic `authorize()` used by MCP/executor paths.
- Decisions: `ALLOW`, `DENY`, `ESCALATE`.
- Validate caller identity, passport, tool, site, resource, receipt, payload schema, batch bounds and prerequisites.
- Add durable approval tickets for headless scheduled jobs.
- Bind approval to payload hash, snapshot hash, receipt/dependency versions, requester and expiry.
- Human/model identities must be separate; proposer cannot grant.
- Add one-time grant/replay protection.
- Add untrusted content envelopes for Firecrawl/Tavily/Exa/Telegram/YouTube/web/document ingestion.
- Prevent untrusted content from modifying policy, permissions, approval or P0/P1 memory.
- Add per-action audit events.

### Exit criteria

- Direct call of a hidden/unauthorized tool still fails.
- Stale approval cannot be replayed.
- Prompt-injection fixtures cannot produce a privileged mutation.
- Context/authorization service outage fails closed for writes.

---

## Phase 4 — independent validators and mutation journal

Goal: success is proven from live state, never from model self-report.

### Work

- Build validators for:
  - WordPress object existence/state;
  - HTTP status/redirect chain;
  - canonical/hreflang;
  - schema parsing and visible-content consistency;
  - internal links and destination status;
  - ZWNJ/site Unicode constraints;
  - image type/metadata;
  - expected before/after diff;
  - publication status/date.
- Add mutation-intent journaling before writes.
- Reuse idempotency key after crash/retry.
- If a worker crashes after remote success but before local completion, re-read live state before retrying.
- Implement rollback handlers where safe/possible.
- Mark prior verification stale after every successful mutation; only fresh post-mutation verification closes a job.

### Exit criteria

- Simulated crash after remote write does not duplicate the mutation.
- Failed live verification cannot be marked succeeded.
- Rollback/recovery path is tested for the pilot mutation class.

---

## Phase 5 — wrap current Mistral in shadow mode

Goal: test whether architecture, not model replacement, fixes current scheduled-task errors.

### Work

- Keep the current Mistral API/model.
- Route exactly one existing scheduled task through:

`bootstrap -> inspect -> propose -> validate -> authorize -> record expected post-condition`

- Do not execute writes initially.
- Compare proposal with canonical site/resource ownership and deterministic validator results.
- Save the comparison as AdaEval evidence.
- Track error classes:
  - wrong target;
  - stale policy;
  - malformed tool args;
  - unsupported assertion;
  - missing required asset;
  - policy violation;
  - false success claim.

### Recommended first workflow

A low-risk Teznevise metadata or harmless formatting workflow with deterministic before/after verification.

### Exit criteria

- Enough shadow runs to expose the dominant failure modes.
- No direct production write bypasses Ada.
- Proposal accuracy and gate catch-rate are measured.

---

## Phase 6 — one live canary

Goal: prove the full contract on production with minimal blast radius.

### Work

- One approved site.
- One reversible mutation class.
- Batch size = 1.
- Snapshot first.
- Fresh receipt.
- Independent live verification.
- Stop on any verification/policy failure.

### Measure

- proposal accuracy;
- validator catches;
- authorization decisions;
- retries;
- verification latency;
- recovery behavior;
- human intervention time.

### Exit criteria

- Repeated canary success without silent state divergence.
- Recovery tested at least once.

---

## Phase 7 — controlled production fan-out

Goal: move routine work from long model sessions into durable bounded child jobs.

### Work

- Parent task decomposes into per-site/per-asset children.
- Every child has its own receipt and idempotency key.
- Canary must succeed before fan-out.
- Configure maximum parallelism per workflow.
- Isolation policy decides whether one child failure stops the whole batch or only that lane.
- Agent passports constrain:
  - sites;
  - tools;
  - page roles;
  - mutation types;
  - batch size;
  - retries;
  - allowed hours;
  - approval requirements.

### Exit criteria

- Multiple routine jobs complete with no shared-state corruption.
- A failed child cannot silently advance sibling or parent state incorrectly.

---

## Phase 8 — AdaEval and model registry

Goal: choose models from our workload evidence.

### AdaEval domains

- Persian writing and RTL.
- Qalam compliance.
- Exact memory/context use.
- Tool selection/arguments.
- WordPress workflows.
- SEO/canonical reasoning.
- Structured output.
- Prompt-injection resistance.
- Unauthorized mutation refusal.
- stale receipt behavior.
- crash/retry recovery.
- hallucination/error rate.
- latency/cost.
- measured memory use and concurrency.

### Registry requirement

No model becomes `CURRENT_WORKER` without:

- official model card URL and immutable revision/hash;
- license/usage-policy review;
- measured hardware profile;
- AdaEval results;
- role assignment;
- rollback/fallback provider.

### Exit criteria

- Existing Mistral baseline is measurable.
- New model candidates can be compared on identical task envelopes.

---

## Phase 9 — local inference on separate compute

Goal: reduce recurring model cost/privacy exposure without destabilizing production.

### Rules

- Do not host a serious worker model on the production VPS.
- Start with a separate GPU machine/rented worker.
- The inference node stores no authoritative state.
- It receives bounded/redacted Context Packs only.
- It cannot mint its own receipts/approvals.
- Model server is replaceable behind a stable worker protocol.

### Exit criteria

- Local candidate matches/exceeds the baseline for its assigned task class.
- Production can fall back to a hosted model without state loss.

---

## Phase 10 — semantic recall and learning

Only after deterministic memory/reliability is proven:

- add full-text/semantic historical recall;
- consider pgvector or another index if measured retrieval needs justify it;
- collect approved successful/failed traces;
- build training dataset;
- fine-tune a small router/task worker only when enough high-quality examples exist;
- promote only if AdaEval improves.

Semantic retrieval never overrides P0/P1 deterministic context.

---

## Phase 11 — external memory mirrors and broader integrations

- XMemo/Engram async mirrors only.
- Google/Drive/ClickUp/etc. integrations as bounded tool adapters.
- Research providers remain evidence sources.
- Add dashboards/UX only after the underlying contracts are reliable.

---

## Immediate build backlog for Grok Build

P0 implementation backlog:

1. Import the live MariaDB control-core baseline into the repo without breaking production.
2. Add integration tests for existing queue/scheduler behavior.
3. Design additive MariaDB migrations for Ada memory/context/passport/approval/journal entities.
4. Implement deterministic bootstrap + scoped dependency receipts.
5. Mirror Qalam/writing stack into a versioned skills registry.
6. Implement untrusted external-content type/envelope.
7. Implement deterministic authorization skeleton.
8. Implement one approval-ticket path.
9. Implement one independent WordPress/live validator.
10. Add shadow-mode adapter around one Mistral scheduled task.
11. Produce migration/runbook before any production cutover.

No local model, pgvector or bulk publishing belongs in this backlog.
