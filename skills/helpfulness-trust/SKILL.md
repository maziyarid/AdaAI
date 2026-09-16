---
name: helpfulness-trust
description: >
  Operating rules for trustworthy, useful, accessible pages in Maziyar's content
  factory. Load before auditing or changing Teznevise (or sister) pages for
  E-E-A-T, authorship, original value, UX writing, accessibility, schema,
  interactive assets, or AI-search eligibility. Does not replace Qalam or the
  SEO field corpus.
version: 1.1.0
date: 2026-09-16
---

# Helpfulness and trust

Qalam writes. The factory decides whether a page deserves work.

This skill does **not** create:

- E-E-A-T percentages
- fake authors
- fake testimonials
- GEO scores
- word-count gates
- engagement gimmicks
- a second writing prompt
- feasibility or validity percentage scores

## Audience

Humans first. Google Search, AI Overviews, and AI Mode are discovery systems.

Official: [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features). Ordinary technical SEO is the bar. Important content must be text. Structured data must match visible text. No special AI file.

## WHO / HOW / WHY

Every important URL:

1. Who created or reviewed it, and why this source deserves attention.
2. How claims, calculations, or recommendations were produced.
3. Why the page exists (a user job). Volume is not a reason.

If a person cannot be named honestly, keep the organisation and leave the contributor slot **unassigned**. Never invent credentials.

## Page roles

Different evidence for research guide, service, tool, download, AI workspace. See factory `/factory/trust`.

Service pages need legitimate scope, process, limits, contact, privacy for research files, no guaranteed grades.

Tools need methodology, assumptions, limitations, version, owner, and crawlable fallback text. No parameter-URL explosion. Do not mint another calculator on the hub without those fields.

## Original value

Before a new URL: name one real reason it should exist. Gate lives at `/factory/intake`. A generic web summary is not enough.

## Decisions

KEEP / SURGICAL_UPDATE / EVIDENCE_REFRESH / UX_REWRITE / ADD_FIRST_PARTY_VALUE / ADD_INTERACTIVE_ASSET / ADD_MEDIA / MERGE / REMOVE / NEW_PAGE.

Default: preserve useful existing content.

## Gap register

Every material gap is `fixed_here`, `queued` with owner, `accepted`, or `blocked`. See `/factory/os`. Do not call the OS complete while a gap is untracked.

## UX writing

fa-IR. Market fit for Iranian Persian. CTA names the action. Errors name the field. Empty and 404 states offer a next step.

Qalam remains the writer of interface strings.

## Accessibility

Keyboard, labels, contrast, semantic headings, lang/dir, touch targets, skip link. Do not hide the job in canvas, hover, or image-only text.

## Schema

Descriptive. Never fake Review/AggregateRating. Do not chase FAQ rich results. Person markup only with a visible real author.

## Measurement

GSC_WEB, GSC_AI, GSC_DISCOVER, GA4, vendor tools, and PRODUCT_UX are different sources. Do not add them. GSC generative-AI reports launched as **impressions**, not clicks.

«Was this useful?» is a product signal, not a ranking factor.

## Interactive assets

Only if they complete a named user job. Demo in this workspace: `/tools/stat-test`, `/tools/feasibility`, `/tools/questionnaire`, `/tools/defence`.

Live Teznevise pattern to copy: sample-size calculator (Cochran vs Morgan, limitations for complex designs).
