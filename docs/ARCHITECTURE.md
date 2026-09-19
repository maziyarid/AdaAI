# AdaAI Canonical Architecture

Status: Phase-1 reliability layer implemented in-repo (2026-09-16). Live VPS import still pending. Prototype PostgreSQL Context Core is **not** deployed.


## 1. Core principle

Ada is not a single model. Ada is the durable operating system around replaceable models.

> Memory is authoritative. Policy is deterministic. Models are replaceable. Tools are bounded. Mutations are authorized. Results are independently verified. Failures are visible.

The model may propose. It never owns truth, permission, task state, or production success.

## 2. Live baseline we are evolving

The VPS already has a real control plane. Do not deploy a second competing one.

Verified live services include:

- `maziyar-control-core.service` on `127.0.0.1:8770`.
- MariaDB 10.11 as its durable database.
- Durable jobs, schedules, leases, retries, dead-letter queue, audit log, content gates, snapshots and external-sync state.
- `maziyar-mistral-worker.service` on `127.0.0.1:9102`, already delegating local durable job/schedule operations to the control core.
- WordPress MCP, GSC MCP, OAuth gateway, session router and local WordPress bridges.

The production VPS is approximately 4 vCPU / 3.6 GiB RAM with no NVIDIA runtime and heavy swap usage. It is a control-plane/storage host, not a serious inference host.

## 3. Target topology

```text
                         Maziyar
                            |
                            v
                  +-------------------+
                  | Ada Control Plane |
                  +-------------------+
                     |             |
                     v             v
          +------------------+   +-------------------+
          | Ada Context Core |<->| MariaDB authority |
          +------------------+   +-------------------+
             |  memory/state       jobs/schedules
             |  receipts           approvals/audit
             |  authorization      snapshots/history
             |
             v
       +----------------+
       | Context MCP    |
       +----------------+
             |
      mandatory bootstrap
             |
   +---------+-----------+------------+-------------+
   |                     |            |             |
   v                     v            v             v
Mistral               ChatGPT        Grok         Gemini / future local worker
workers               / Codex        Build        models
   |                     |            |             |
   +---------------------+------------+-------------+
                         |
                         v
                 +----------------+
                 | Qalam Registry |
                 +----------------+
                         |
          Art of Writing Bible + overlays
                         |
                         v
                 +----------------+
                 | Tool Gateway   |
                 +----------------+
                   |     |      |
                   v     v      v
                 WP MCP VPS   research/data tools
                   |
                   v
            independent validators
                   |
                   v
             production mutation
```

## 4. Ada Context Core

Ada Context Core is the single authority for operational context and durable state.

It must evolve the existing `/opt/maziyar-control-core` system rather than run as a parallel source of truth.

### Stores

- P0/P1 canonical memory and policy pointers.
- Project/site/task state.
- Scoped dependency versions.
- Context receipts.
- Agent passports.
- Tool registry and mutation classes.
- Approval tickets and approval events.
- Task runs, events, leases and checkpoints.
- Mutation journal and idempotency records.
- Snapshots and rollback metadata.
- Model registry and AdaEval outcomes.
- External-memory mirror status.
- Audit records.

### Memory classes

- `P0` Mandatory constitutional rules.
- `P1` Current canonical project/site decisions.
- `P2` Verified operational knowledge.
- `P3` Reusable contextual guidance/examples.
- `P4` Historical/superseded state.
- `P5` Candidate or unverified findings.

### Provenance classes

At minimum: `PROPOSED`, `OBSERVED`, `CONFIRMED`, `VERIFIED`, `CANONICAL`, `SUPERSEDED`.

Model output and scraped research never become P0/P1 automatically.

## 5. Scoped context receipts

Do not use one global revision as the only freshness control.

A receipt records exactly what a task depends on, for example:

```json
{
  "task_run_id": "...",
  "agent_id": "mistral-worker",
  "dependencies": [
    {"scope": "global", "version": 42},
    {"scope": "project:teznevise", "version": 18},
    {"scope": "site:teznevise.ir", "version": 27},
    {"scope": "task_type:content_refresh", "version": 9},
    {"scope": "qalam", "release": "current"}
  ],
  "allowed_mutations": ["update_post_metadata"],
  "payload_hash": "...",
  "expires_at": "..."
}
```

A consequential write fails with `STALE_CONTEXT` only when one of its actual dependencies changed.

Use HMAC only inside one trusted shared-secret boundary. Use asymmetric signatures when remote/semi-trusted workers must verify receipts without being able to mint them.

## 6. Qalam is mandatory and first-class

Qalam is not optional style guidance. It is the mandatory writing/orchestration policy for all user-facing prose.

The full writing stack must be mirrored into Ada's versioned skill registry, not merely referenced from chat memory:

- Qalam router.
- Art of Writing Bible v1.4 and future releases.
- Iranian Persian `fa-IR` UX-writing rules.
- `fa-IR` product lexicon.
- academic/methodology/service overlays.
- British-English overlay.
- medical fact-check overlay.
- site-specific policies, including Teznevise's zero-U+200C rule.
- approved examples/evaluation cases.

Workers must not embed their own replacement style prompts.

Required writing path:

`task/site policy -> Context bootstrap -> Qalam -> evidence packet -> candidate -> language/UX QA -> factual QA -> SEO/canonical QA -> mutation gate -> live verification`

## 7. Execution contract

Every job follows this lifecycle:

1. Scheduler creates a durable task run and idempotency key.
2. Worker claims the task with a lease.
3. Worker bootstraps Context Core.
4. Context Core loads exact mandatory P0/P1 context and current project state.
5. A scoped receipt is issued.
6. Qalam/other task policies are loaded as required.
7. Worker performs read-only inspection.
8. Model proposes a plan/candidate/tool call.
9. Deterministic validators inspect it.
10. `authorize()` returns `ALLOW`, `DENY`, or `ESCALATE`.
11. Approval is obtained when required.
12. Snapshot is created when mutation requires rollback/recovery.
13. One canary mutation executes.
14. Independent validators re-read live state.
15. Fan-out is permitted only after canary success.
16. Every child task is independently verified.
17. Project/task state and audit are finalized.
18. External memory mirrors update asynchronously.

Never permit `prompt -> production mutation`.

## 8. Authorization boundary

Authorization must be enforced at the actual MCP/executor call boundary, not only in prompts or client middleware.

Conceptually:

```text
authorize(action, passport, receipt, policy) -> ALLOW | DENY | ESCALATE
```

### Automatic DENY examples

- missing/expired/stale receipt;
- unknown site or canonical resource;
- tool outside passport;
- malformed payload;
- missing required snapshot;
- invalid idempotency key;
- policy modification attempted by a worker;
- external/scraped content attempting to issue instructions.

### ESCALATE examples

- deletion;
- bulk publish/update across sites;
- canonical ownership change;
- P0/P1 policy change;
- first production action for a new workflow/site;
- sensitive external communication;
- failed independent verification.

## 9. Approval tickets

Headless scheduled workers must never block inside an MCP call waiting for a human.

On `ESCALATE`:

- create a durable approval ticket;
- bind exact tool, site, resource, payload hash, snapshot hash, receipt hash, dependency versions, requester and expiry;
- notify the human out of band;
- move the job to `WAITING_APPROVAL`;
- on approval, re-bootstrap context and re-authorize;
- approval is one-time and replay-resistant.

The proposing model can create a pending request. It cannot grant its own approval.

## 10. Independent verification

A model saying "published successfully" is not evidence.

Validators must re-read live state independently, including where applicable:

- HTTP status and redirects;
- WordPress object/status/content/meta;
- canonical/hreflang;
- schema parse/visible-content agreement;
- internal links and destination status;
- Teznevise ZWNJ constraint;
- image type/metadata;
- rendered output and language/dir;
- expected post-condition hash/diff.

A successful mutation makes previous verification stale. Completion requires fresh verification after the latest successful mutation.

## 11. Untrusted external content

Anything fetched through Firecrawl, Tavily, Exa, Telegram, YouTube, web pages, PDFs or other research sources is data, not instruction.

External content may not directly:

- modify policy;
- grant tool permissions;
- approve a ticket;
- change memory priority;
- call tools;
- override Qalam;
- create canonical memory.

It enters an evidence/research lane and must be synthesized/verified before promotion.

## 12. Research and evidence services

Research providers are replaceable evidence sources, not authorities.

- Acumen: recency preflight; identify developments/questions worth checking.
- Context7: current SDK/API/framework documentation.
- Exa: broad/deep source discovery and source-backed research.
- Firecrawl: crawl/search/scrape/developer-index and structured extraction.
- treg: intended unified SEO/SERP/backlink/provider layer when installed/connected.
- Sixtyfour: people/company intelligence when relevant.
- first-party systems (GSC/GA/WP/live HTTP): authoritative about our own sites.

Provider results must preserve provenance and freshness.

## 13. Mistral's role

Mistral is the first bounded routine worker, not the control plane.

Before replacement, wrap the current Mistral worker in Ada's execution contract and run it in shadow mode.

Good initial responsibilities:

- candidate drafting;
- structured classification;
- metadata suggestions;
- extraction/summarization;
- bounded routine page updates after validation;
- routine QA proposals.

Mistral must not independently alter policy, architecture, canonical ownership, or run unrestricted bulk publishing.

## 14. ChatGPT/Grok/Gemini roles

Frontier models should do high-leverage work:

- architecture and difficult engineering;
- complex research/synthesis;
- debugging failures;
- skill/policy evolution;
- high-risk review;
- migration planning;
- evaluation design;
- multimodal or specialist work.

They remain replaceable workers. They do not own memory.

## 15. Local model strategy

No serious local LLM should run on the current production VPS.

The VPS remains the state/control plane. A future inference node may be local, rented, or cloud-hosted.

No model becomes a production worker until its registry contains verified official model-card/license evidence and AdaEval results on our workloads.

Model selection is by task performance, not parameter count or leaderboard rank.

## 16. Database decision

The long-term architecture is database-agnostic, but the implementation starts from the live MariaDB-backed control core.

Do **not** install PostgreSQL merely because earlier design drafts assumed it.

First extend MariaDB with the missing Ada entities and prove the reliability contract. Revisit PostgreSQL/pgvector only if a measured requirement justifies migration later.

For MariaDB recovery, use encrypted backups plus binary-log based point-in-time recovery/restore testing rather than PostgreSQL-specific WAL instructions.

## 17. External memories

XMemo and Engram become optional asynchronous mirrors/history aids.

They must never override active Context Core records. Mirror failure must not block the core workflow.

## 18. Infrastructure control

- SentinelX: VPS inspection, service/file operations, recovery and administration.
- VPS MCP: normal bounded infrastructure tool surface for agents.
- WordPress MCP: bounded site mutation surface.
- OAuth gateway: caller authentication.
- Ada authorization: per-action authorization.

Authentication proves who is calling. Ada still decides whether this action is allowed.

## 19. Completion definition

Ada is not considered reliable because a model produces good prose.

A workflow is promotable only when it demonstrates:

- deterministic context bootstrap;
- correct scoped receipt invalidation;
- bounded tool use;
- idempotent recovery;
- fresh independent verification;
- visible failure states;
- tested rollback/recovery;
- reproducible AdaEval performance.
