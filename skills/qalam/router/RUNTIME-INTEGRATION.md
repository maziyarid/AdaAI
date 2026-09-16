# Qalam Runtime Integration Contract

Version: 1.0
Date: 2026-09-15
Applies to: thesis/research-site content workers, editorial refresh workers, UX/landing copy workers, and any other runtime that produces or materially edits user-facing prose.

## Purpose

Qalam is the single writing entrypoint. Runtime workers should not each carry their own competing style prompt. The runtime owns scheduling, queues, locks, publication and site mutation; Qalam owns writing-policy selection, memory/tool routing, and language/editorial QA orchestration.

## Bootstrap contract

At worker start, resolve the current writing configuration from the Content Factory control plane:

- `WRITING_AGENT_ENTRYPOINT=QALAM`
- `QALAM_CANONICAL_VERSION=1.4.0`
- `QALAM_GITHUB_ENTRY=https://github.com/maziyarid/agents/blob/main/writing/qalam/SKILL.md`
- `QALAM_MEMORY_PRIMARY=XMemo`
- `QALAM_MEMORY_SECONDARY=Engram`
- `QALAM_TOOL_ROUTING=ROLE_BASED_MINIMAL`
- `PERSIAN_PRODUCT_LOCALE=fa-IR`

If a later canonical version is explicitly configured, use it instead of hard-coding 1.4.0.

## Required execution sequence

For every substantial writing/editing task:

1. **Load task + site policy** — task packet, Site Profiles, canonical/search-intent owner, language, page role and risk.
2. **Enter Qalam** — load Qalam router and the configured Art of Writing Bible version.
3. **Recover relevant memory** — XMemo first for current decisions/state; Engram only when historical wording/provenance materially matters.
4. **Load only the needed overlay** — academic, research guide, service, `UX_WRITING_FA_IR`, medical or English.
5. **Load evidence packet** — Content Factory/Research Library/You.com-backed findings and other current evidence only when the task requires it.
6. **Draft or edit** — prefer surgical changes for existing canonical pages unless a full rewrite is explicitly justified.
7. **Language/register/UX QA** — naturalness, register, `fa-IR` product language, interface clarity, site-specific orthography.
8. **Fact/evidence QA** — independent from language quality; verify claims, methods, figures and freshness.
9. **SEO/canonical QA** — owner, intent, canonical, internal links, metadata/schema and anti-cannibalisation rules.
10. **Publication gate** — runtime applies its existing manager/reviewer/write/rollback rules.
11. **Live verification** — verify final URL/canonical/rendered copy where applicable.
12. **Durable write-back** — update Content Factory state, research usage, and only meaningful memory/project state.

## Memory degradation policy

Memory should improve continuity, not make the factory brittle.

### XMemo unavailable

If XMemo cannot be called:

- mark the task `MEMORY_UNAVAILABLE_XMEMO` in execution evidence/logs;
- continue using the current task packet, Config, Site Profiles, Research Library and current artefacts when they contain enough context;
- do not invent missing project decisions;
- hold only when the missing memory is material to correctness, ownership, safety or publication.

### Engram unavailable

Engram is historical/secondary. Its failure should normally be non-blocking. Mark `HISTORY_UNAVAILABLE_ENGRAM` when history/provenance was relevant.

Never silently substitute stale remembered policy for current control-plane configuration.

## Research degradation policy

Research is conditional, not ritual.

- If the task is a pure language/UX revision and makes no new factual claim, external research may be unnecessary.
- If freshness, factual completeness, statistics, methods or current SEO conditions matter, research is required.
- If You.com/current evidence is unavailable, preserve verified existing facts and stage unresolved claims rather than fabricating replacements.
- A transport failure must not trigger content regeneration or creation of a duplicate canonical URL.

## Tool-budget policy

The runtime must not expand Qalam into an “always call everything” agent.

Use tools by role:

`memory → evidence/currentness → domain → action → verification → durable write-back`

Default to one sufficient tool/source per role. Add another only for triangulation, missing evidence or a distinct capability.

## Persian locale contract

For Iran-targeted product/landing/interface work:

- target `fa-IR`;
- load `UX_WRITING_FA_IR`;
- reject unreviewed `fa-AF`/Dari localisation leakage;
- use contemporary Iranian product vocabulary and conventions;
- review copy in the rendered interface when possible.

For Teznevise Persian specifically, the existing no-U+200C/ZWNJ site rule remains mandatory even though ZWNJ is normal in general Persian.

## QA separation

Never let one PASS cover all of these:

- `LANGUAGE_UX_QA`
- `FACT_EVIDENCE_QA`
- `SEO_CANONICAL_QA`
- `LIVE_RENDER_QA` where relevant

A fluent sentence is not evidence that a statistical, methodological, medical or SEO claim is correct.

## Existing-page refresh policy

For an established canonical page:

- patch surgically by default;
- preserve useful winning language/query coverage where supported by current data;
- keep URL/media unless a separate decision changes them;
- do not regenerate an approved READY_TO_APPLY payload because transport previously failed;
- do not create synonym pages while a canonical owner exists.

## Worker implementation rule

Integrate Qalam **once in the shared worker/bootstrap layer**. Do not paste the full Bible into every task prompt.

A worker may pass a compact task envelope such as:

```yaml
writing_agent: QALAM
writing_version: 1.4.0
site: teznevise.ir
page_role: SERVICE|GUIDE|BLOG|HUB|TOOL|DOWNLOAD|CASE_STUDY
locale: fa-IR|en-GB
mode: CREATE|SURGICAL_REFRESH|UX_REWRITE|EDITORIAL_REVIEW
fact_risk: low|medium|high
research_required: auto|yes|no
canonical_owner: <resolved URL or ID>
```

Qalam resolves the rest from current control-plane/site policy.

## Logging contract

Each substantial run should record, without secrets:

- Qalam version;
- loaded overlay(s);
- memory status (`XMEMO_OK|UNAVAILABLE`, `ENGRAM_OK|NOT_NEEDED|UNAVAILABLE`);
- evidence packet/version/source IDs where applicable;
- QA statuses separately;
- canonical owner;
- publication/live-verification status;
- reasons for HOLD/REVISION_REQUIRED.

Do not log raw API keys, tokens, passwords or private memory content.

## Deployment verification matrix

Before calling runtime integration complete, execute at least these three non-destructive or review-gated tests:

### A. Informational article/edit
- Qalam version is logged.
- appropriate academic/readable overlay loads.
- Teznevise output contains 0 U+200C.
- no invented factual additions when evidence is absent.

### B. Landing/service/UX edit
- `UX_WRITING_FA_IR` loads.
- button/form/error/trust copy is explicit and contemporary `fa-IR`.
- no unreviewed Dari/fa-AF localisation leakage.
- language/UX QA and fact QA are logged separately.

### C. Existing-page research refresh
- canonical owner is resolved before write.
- current Research Library/You.com-backed evidence is consumed when relevant.
- edit is surgical rather than duplicate-page generation.
- service/internal-link policy is preserved.
- live URL/canonical is verified after any approved write.

## Deployment steps for the server runtime

When server access is available:

1. locate the shared worker/bootstrap and current content-factory configuration in the live runtime;
2. add Qalam resolution/loading there, not in individual task payloads;
3. map the current Sheet Config keys to runtime configuration;
4. ensure the worker reads the priority-0 `Mistral_Instructions` rules;
5. add the logging fields above;
6. run the three verification cases;
7. restart/reload only the affected worker/timer services;
8. inspect logs and queue advancement;
9. roll back the bootstrap change if tasks lose canonical/evidence gates or publication safety.

## Definition of done

Runtime integration is complete only when the **live worker logs** prove that scheduled/generated content is entering Qalam and the verification matrix passes. Repository, Drive and Sheet configuration alone are necessary but not sufficient proof of deployment.
