# Writing agents

This directory contains the reusable writing layer for Maziyar's agents.

## Canonical entrypoint

Use `skills/qalam/router/SKILL.md` as the single entrypoint for substantial writing, editorial, UX-copy and content work.

**Authoritative current versions** live in `skills/qalam/RELEASE.json` (router, Bible, eval pack, overlay paths). Do not hard-code a "current" Qalam or Bible version in workers.

Qalam must:

1. recover relevant project/site policy from Ada Context Core memory;
2. load the Art of Writing Bible version named in `RELEASE.json`;
3. load every overlay listed for the selected task profile (not unrelated profiles);
4. research only when the task needs current or external evidence;
5. keep factual QA separate from language/UX QA;
6. persist meaningful completed decisions back to durable memory.

The user should not need to manually select a long list of tools.

## Canonical writing standard

Current versions are **not** a single number:

- Qalam router: see `RELEASE.json` → `components.qalam-router.version` (currently 1.1.0)
- Art of Writing Bible: see `RELEASE.json` → `components.art-of-writing-bible.version` (currently 2.0.0)
- Eval pack: see `RELEASE.json` → `components.art-of-writing-bible-evals.version` (currently 1.3.0, validating Bible 2.0.0)

The historical `1.4.0` label in older integration notes is **not current**. It is recorded in `RELEASE.json` `legacy_labels`.

Bible 2.0.0 adds:

- Iranian Persian (`fa-IR`) UX-writing and landing-page rules;
- interface/form/error/success/empty/loading microcopy;
- Iranian product-vocabulary consistency;
- protection against unintended Dari/`fa-AF` localisation leakage on Iran-targeted interfaces.

## Repository files

Paths below are the in-repo locations. They match `RELEASE.json` / `REGISTRY.json`.

- `skills/qalam/router/SKILL.md` — orchestration/router layer.
- `skills/qalam/fa-ir-overlays/ux-writing-fa-ir.md` — product/UI/landing Persian overlay.
- `skills/qalam/fa-ir-overlays/tool-routing.md` — role-based tool routing.
- `skills/qalam/fa-ir-overlays/fa-ir-product-lexicon.md` — Iranian product lexicon.

## Runtime integration contract

Any content worker that drafts, rewrites, edits, refreshes or publishes user-facing prose should call Qalam before generation rather than embedding separate style prompts.

Recommended worker sequence:

`task/site policy → Qalam → evidence/fact packet → draft/edit → independent editorial QA → SEO/canonical QA → publish gate → durable write-back`

Do not make Qalam responsible for publication scheduling, queue ownership or site mutation itself. Those remain worker/runtime concerns.
