# Grok Build Handoff — AdaAI Phase 1 Reliability Build

Use the prompt below verbatim or as the canonical mission specification for Grok Build.

---

## Mission

You are taking over development of `https://github.com/maziyarid/AdaAI`.

Do not redesign Ada from scratch. Do not reintroduce the old Grok App Builder scaffold. Do not start by choosing or hosting a local LLM.

Your job is to implement the smallest production-safe reliability slice of Ada around the **existing live control plane**, preserving Qalam and the Persian writing system as mandatory first-class infrastructure.

Read these files before changing code:

1. `AGENTS.md`
2. `docs/ARCHITECTURE.md`
3. `docs/ROADMAP.md`
4. `docs/VPS-DEPLOYMENT.md`
5. `ada-context-core/docs/EXECUTION-CONTRACT.md`
6. `ada-context-core/docs/MEMORY-CONTRACT.md`
7. `ada-context-core/docs/SECURITY.md`
8. `ada-context-core/docs/RECOVERY.md`

The architecture documents and the **live VPS state** outrank older prototype assumptions when they conflict.

## Non-negotiable architecture

Ada is provider-independent. Its identity must live outside model weights in:

- authoritative context/memory;
- Qalam and the Art of Writing Bible;
- site/project policies;
- durable task state;
- tool permissions;
- approval/authorization rules;
- audit/recovery state;
- evaluation cases.

Core principle:

> Models propose. Deterministic code authorizes. Independent validators prove the live result.

A model must never be the final authority for production mutation or success.

## Verified live environment

Before coding, use the authorized VPS/SentinelX tooling to re-check these facts rather than assuming they are still true:

- Existing service: `maziyar-control-core.service`.
- Existing internal endpoint: `127.0.0.1:8770`.
- Existing implementation path: `/opt/maziyar-control-core`.
- Existing database: MariaDB 10.11.
- Existing control core already has durable jobs, schedules, leases, retries, dead-letter queue, audit, content gates, snapshots and external-sync state.
- Existing Mistral worker: `maziyar-mistral-worker.service` on `127.0.0.1:9102`.
- The Mistral worker already delegates local job/schedule control to the control core.
- Existing WordPress MCP, OAuth gateway, GSC MCP and related services are production infrastructure and must not be destabilized.
- Current production host is about 4 vCPU / 3.6 GiB RAM with no NVIDIA GPU runtime and substantial swap usage.

Therefore:

**Do not deploy a second PostgreSQL scheduler/control plane beside MariaDB.**

The existing live control core is the migration baseline and should evolve into Ada Context Core.

The prototype `ada-context-core/` code in the repository is design/reference material. Reconcile its good contracts with the live MariaDB implementation rather than blindly deploying its PostgreSQL assumptions.

## Phase-1 scope

Implement only the P0 reliability foundation needed to prove one workflow end to end.

### A. Import and freeze the live baseline

1. Create a development branch.
2. Back up the existing live `/opt/maziyar-control-core` source and relevant service/config metadata.
3. Import the current control-core source into the AdaAI repository under a clearly named runtime/migration area.
4. Do not expose secrets, tokens, passwords or private environment values in Git.
5. Add tests that capture the existing queue/scheduler/idempotency behavior before refactoring.
6. Document any divergence between repository prototype code and live runtime.

### B. Extend MariaDB additively

Design versioned additive migrations for the existing database. Do not destroy current tables.

Add the minimum entities required for:

- canonical memory records;
- immutable memory versions/supersession;
- scoped dependency versions;
- current project/workflow state;
- context receipts and receipt dependencies;
- agent passports;
- tool registry + mutation classes;
- approval tickets/events;
- mutation journal/idempotency metadata;
- model registry metadata;
- mirror status;
- backup/restore run records.

Memory priorities:

- P0 mandatory;
- P1 canonical;
- P2 verified operational;
- P3 contextual/reusable;
- P4 historical/superseded;
- P5 candidate/unverified.

Provenance must distinguish at least:

`PROPOSED`, `OBSERVED`, `CONFIRMED`, `VERIFIED`, `CANONICAL`, `SUPERSEDED`.

No AI observation or scraped source may promote itself to P0/P1.

### C. Deterministic Context Pack bootstrap

Implement a bootstrap API/service that receives at least:

- agent ID;
- task run ID;
- project;
- site;
- task type;
- risk class.

It must deterministically load active mandatory context from exact scopes and current project state.

Do not depend on embeddings for P0/P1 retrieval.

Return a Context Pack plus a receipt that binds the **exact dependencies loaded**.

Do not rely only on one global revision. Receipt dependencies should be scoped, e.g.:

- global policy version;
- project policy version;
- site policy version;
- task-type policy version;
- Qalam release;
- writing overlay release where relevant.

A consequential mutation becomes `STALE_CONTEXT` only if a dependency it actually used changed.

HMAC may be used only inside the current trusted local service boundary. Design receipt metadata so asymmetric signing can replace it later for remote/semi-trusted workers.

### D. Qalam and Persian writing registry

Qalam/Persian writing is mandatory infrastructure, not optional decoration.

Mirror the complete current writing stack from the canonical `maziyarid/agents`/approved source bundle into a versioned Ada skill registry, preserving provenance and immutable hashes:

- Qalam router;
- Art of Writing Bible v1.4 and version history/current pointer;
- `ux-writing-fa-ir.md`;
- `fa-ir-product-lexicon.md`;
- tool-routing rules;
- academic/methodology/service overlays;
- British-English overlay;
- medical/fact-check overlay;
- site-specific rules including Teznevise zero-U+200C;
- approved examples/evaluation cases.

Do not replace these with a new Grok writing prompt.

Update Qalam runtime routing so Context Core is authoritative for canonical state. XMemo and Engram are secondary asynchronous mirrors/provenance aids only.

A Persian/user-facing writing task must declare Qalam + applicable overlay versions as receipt dependencies.

### E. Untrusted external-content quarantine

Create a first-class representation for external/retrieved content from Firecrawl, Tavily, Exa, Telegram, YouTube, websites, PDFs and similar sources.

It is data, not instruction.

It must never directly:

- modify P0/P1 policy;
- grant permissions;
- approve an action;
- alter memory priority;
- override Qalam;
- execute a tool;
- create canonical memory.

Add fixtures/tests with prompt-injection text such as instructions embedded inside scraped content. The privileged action must still be denied.

### F. Deterministic authorization skeleton

Create one deterministic authorization function used at the execution/MCP boundary:

`authorize(action, passport, receipt, policy) -> ALLOW | DENY | ESCALATE`

It must fail closed.

Validate at least:

- caller/agent identity;
- passport;
- tool/mutation class;
- site/resource scope;
- receipt presence/freshness;
- payload schema/hash;
- required snapshot;
- idempotency key;
- batch limit;
- approval requirement.

Do not consider hiding a tool from `tools/list` to be authorization. Direct `tools/call`/executor calls must still be denied when unauthorized.

Examples of `DENY`:

- missing/expired/stale receipt;
- tool/site outside passport;
- unknown canonical target;
- malformed payload;
- missing required snapshot;
- attempted policy mutation by a worker;
- scraped content attempting to issue privileged instructions.

Examples of `ESCALATE`:

- deletion;
- cross-site bulk publish/update;
- canonical ownership change;
- P0/P1 change;
- first production execution of a new workflow;
- failed independent verification;
- sensitive external communication.

### G. Durable approval ticket — one path only

Implement the minimal generalizable ticket state machine, but prove only one escalation path in Phase 1.

Ticket must bind:

- task/job ID;
- exact action/tool;
- site/resource;
- exact payload hash;
- live snapshot hash;
- context receipt/dependency versions;
- requester;
- approver;
- expiry;
- one-time/replay-resistant grant ID;
- status/events.

The proposing model may create `PENDING_APPROVAL`. It can never grant its own ticket.

For headless/scheduled workers, do not park an HTTP/MCP request while waiting for a human. Persist state and resume later.

### H. Independent validator — one real workflow

Build deterministic verification for one low-risk Teznevise mutation class.

Recommended pilot: a reversible, non-critical metadata or harmless formatting change.

The validator must independently re-read live WordPress/HTTP state. Do not ask the same model whether its action succeeded.

For that pilot prove:

- pre-state snapshot;
- authorized mutation;
- actual live change;
- expected post-condition;
- fresh post-mutation verification;
- idempotent retry/recovery;
- rollback/recovery path.

A successful mutation makes pre-mutation verification stale. Only fresh verification after the latest successful mutation permits `SUCCEEDED`.

### I. Wrap the current Mistral worker in shadow mode

Do not replace Mistral yet.

For exactly one existing scheduled workflow:

`bootstrap -> inspect -> propose -> deterministic validate -> authorize -> record expected post-condition`

Initially block production writes.

Record proposal/evaluation results for AdaEval:

- target correctness;
- canonical ownership correctness;
- tool/argument correctness;
- Qalam/policy compliance;
- validator failures;
- unsupported claims;
- expected post-condition.

This experiment answers the important question: does the deterministic contract catch the mistakes that currently make Mistral unreliable?

### J. One production canary only after shadow mode

When shadow evidence is satisfactory, prepare (do not silently run without authorization) one production canary:

- one site;
- one asset;
- one reversible mutation class;
- batch size 1;
- snapshot first;
- fresh receipt;
- independent verification;
- stop immediately on policy/verification failure.

No bulk publishing, deletion or cross-site fan-out in this milestone.

## Research/tool integration rules

Do not hardwire the system to one research provider.

Treat these as replaceable roles:

- Context7: current technical/library/API docs.
- Acumen: recency/missing-development preflight.
- Exa: deep discovery/source research.
- Firecrawl: scrape/crawl/developer index/structured web extraction.
- treg: SEO/SERP/backlink/provider layer when actually installed/connected.
- Sixtyfour: people/company intelligence only when relevant.
- first-party GSC/WP/HTTP: authoritative evidence about our sites.

Every external result carries source/provenance/freshness. External results enter an untrusted evidence lane and cannot mutate policy directly.

## Model/inference rules

Do not install a serious local LLM on the current production VPS.

Do not spend this milestone comparing Qwen/Gemma/gpt-oss or building vLLM.

Add only the metadata structure required for a future model registry and AdaEval.

A future model may become a worker only after official model-card/license verification and measured AdaEval/hardware results.

## Recovery requirements

Because the source of truth is currently MariaDB, use MariaDB-compatible recovery:

- encrypted backups;
- binary logs/PITR where configured;
- off-host copy;
- documented restore procedure;
- restore test/drill.

Do not copy PostgreSQL WAL commands into production documentation.

## Repo hygiene

- Keep `main` production-oriented.
- Do not restore `.grok/` App Builder scaffolding, games, generic generated skills, Vercel demo UI, screenshots or placeholder frontend dependencies.
- Preserve old experiments only in the existing archive branch/history.
- No secrets or copied production credentials in commits.
- Prefer small, reviewable commits.
- Update architecture/docs when implementation decisions change.

## Tests required before handoff

At minimum add automated tests for:

1. P0/P1 deterministic context selection.
2. scoped stale-receipt invalidation.
3. unrelated policy update does not falsely stale a task.
4. supersession/history behavior.
5. unauthorized direct tool call is denied.
6. expired receipt is denied.
7. wrong site/resource is denied.
8. approval cannot be self-granted by proposer/model identity.
9. approval replay is denied.
10. external prompt-injection fixture cannot alter policy/permission.
11. duplicate idempotency key cannot duplicate a mutation.
12. crash-after-remote-success recovery re-verifies instead of blindly repeating.
13. successful mutation makes previous verification stale.
14. fresh independent verification closes the task.
15. Teznevise zero-U+200C check.
16. Qalam release dependency is present for writing tasks.

## Deliverables

Return/commit:

- clean code changes in `maziyarid/AdaAI`;
- migration files for MariaDB;
- tests;
- live-baseline import/migration notes;
- architecture decision records for any deviation;
- Qalam skill-registry layout;
- authorization/approval contracts;
- shadow-mode Mistral adapter;
- one validator/canary workflow;
- deployment/rollback runbook;
- updated README/roadmap status;
- a final gap/blocker report.

## Completion rule

Do not claim "Ada is deployed" merely because code exists.

For every claimed completed implementation step provide fresh verification evidence from the repository/runtime. A successful mutation invalidates older verification; re-verify afterward.

Do not claim the production canary succeeded unless live state was independently checked after the mutation.

## Stop conditions

Stop and report instead of improvising when:

- live baseline differs materially from the architecture;
- a migration could destroy/overwrite existing durable state;
- required secrets/access are missing;
- backups/restore readiness is insufficient for a risky migration;
- the only way forward would create a second source of truth;
- a requested production mutation lacks required approval.

When a stop condition occurs, preserve all completed code/docs and return the exact blocker and safest next step.
