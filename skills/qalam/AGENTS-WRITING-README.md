# Writing agents

This directory contains the reusable writing layer for Maziyar's agents.

## Canonical entrypoint

Use `writing/qalam/SKILL.md` as the single entrypoint for substantial writing, editorial, UX-copy and content work.

Qalam must:

1. recover relevant project/site policy from memory;
2. load the latest Art of Writing Bible;
3. select only the required register/domain overlay;
4. research only when the task needs current or external evidence;
5. keep factual QA separate from language/UX QA;
6. persist meaningful completed decisions back to durable memory.

The user should not need to manually select a long list of tools.

## Canonical writing standard

Current canonical standard: **Art of Writing Bible v1.4.0 (2026-09-15)**.

v1.4 adds:

- Iranian Persian (`fa-IR`) UX-writing and landing-page rules;
- interface/form/error/success/empty/loading microcopy;
- Iranian product-vocabulary consistency;
- protection against unintended Dari/`fa-AF` localisation leakage on Iran-targeted interfaces;
- Qalam's single-agent tool-routing contract.

Preserved from v1.3:

- PhilosophyCafe corpus findings are used as public-corpus evidence, not as a living-person imitation target;
- academic, methodology/statistics and service-page overlays;
- Teznevise's no-U+200C rule remains site-specific;
- detector-evasion tricks and fabricated quirks remain forbidden.

## Repository files

- `qalam/SKILL.md` — orchestration/router layer.
- `art-of-writing-bible/references/ux-writing-fa-ir.md` — product/UI/landing Persian overlay.
- `art-of-writing-bible/references/tool-routing.md` — role-based tool routing.

The full v1.4 Bible, version archive, corpus references and evaluation pack remain in the canonical Google Drive bundle and should be mirrored here only when the runtime needs a fully self-contained repository copy.

## Runtime integration contract

Any content worker that drafts, rewrites, edits, refreshes or publishes user-facing prose should call Qalam before generation rather than embedding separate style prompts.

Recommended worker sequence:

`task/site policy → Qalam → evidence/fact packet → draft/edit → independent editorial QA → SEO/canonical QA → publish gate → durable write-back`

Do not make Qalam responsible for publication scheduling, queue ownership or site mutation itself. Those remain worker/runtime concerns.
