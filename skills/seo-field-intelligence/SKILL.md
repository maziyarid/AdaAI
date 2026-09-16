---
name: seo-field-intelligence
description: >
  Experience-based SEO decision layer for Maziyar's thesis/research Content Factory.
  Use before creating URLs, refreshing pages, merging/deleting, internal linking,
  interpreting Search Console, or promoting a practitioner claim into a factory rule.
  Does not write prose — Qalam / Art of Writing Bible remains the only writing path.
version: 1.0.0
date: 2026-09-15
status: canonical
default: false
languages:
  - fa
  - en
---

# SEO Field Intelligence

This skill is a **decision layer**, not a writing layer.

Load it when the task is: should we create, refresh, merge, redirect, noindex, retitle, internally link, or experiment?

Do **not** load it to draft sentences. Drafting still goes:

Research intelligence → brief → **Qalam / Art of Writing Bible** → independent language QA → evidence QA → canonical/SEO QA.

Never send a Telegram post into a model with “rewrite this as an article”.

## Precedence

1. Safety, truth, legal/ethical constraints
2. Current explicit user instruction
3. Site policy (Teznevise: no U+200C; advisory framing; medical out of this factory)
4. Art of Writing Bible (how it is written)
5. This skill (what to publish, refresh, or refuse)
6. Conversion polish

A Telegram practitioner is not Google. Google policy is not a field observation. Keep the evidence types separate.

## Evidence types

| Kind | Meaning | Enters |
|---|---|---|
| `OFFICIAL_EVIDENCE` | Google documentation or named Googler on the record | Research Library, factory governance if stable |
| `FIELD_EVIDENCE` | Practitioner experiment, case, or Q&A | Corpus first; Library only after synthesis |
| `SITE_DATA_EVIDENCE` | Our GSC / crawl / conversion | SEO Signals |

Telegram URLs may appear in Evidence URLs. The post itself is not a signal and not a page.

## How a finding moves

```
SEO Field Corpus
→ synthesis / conflict check / currency label
→ Research Library (reusable only)
→ Refresh Queue / Editorial Queue / SEO Experiments / Tasks
→ Qalam writes the patch
→ independent QA
→ live observation in SEO Signals
```

Do not dump posts into Personal Research Intake or SEO Signals.

## Currency labels

- `CURRENT` — operate on this unless our data contradicts it
- `CURRENT_BUT_CONTEXTUAL` — true only under named conditions
- `NEEDS_REVALIDATION` — interesting; test or wait
- `HISTORICAL_ONLY` — explains the past; do not execute
- `SUPERSEDED` — same author or stronger evidence later reversed it; keep the record

Never delete a superseded finding. Opinion change is data.

## Confidence (not personality)

Highest to lowest:

1. First-hand experiment with before/after
2. Documented case with conditions
3. Repeated first-hand observation
4. Detailed answer from an experienced practitioner
5. General recommendation
6. Community consensus
7. Anecdote
8. Unsupported opinion

Shahram’s first-hand notes get attention, not automatic universality.
Mahdi starts at lower prior unless independently supported.
Moradi videos in this snapshot have **no transcripts** — titles are not rules.

## Operating principles (2026)

1. One search intent, one canonical owner. The folk name “cannibalization” is optional; the IA rule is not.
2. Refresh substance, never the calendar.
3. A Telegram idea is never enough for a new URL.
4. Qalam writes. This layer decides.
5. Official spam policy and field observation are different evidence types.
6. Do not test traffic manipulation, downtime recrawl, DA inflation, expired-domain ranking plays, or combinatory template URLs.
7. Winning URLs get additive edits. Thin overlap gets an owner, not a twin.
8. Page-level test: a new fact, decision, or first-party example.
9. Site-level quality is judged from the archive. Old thin templates stain good pages.
10. Schema is not an indexation ticket. Service URLs do not become blog posts.

## Decision trees (short)

**DELETE vs 301 vs IMPROVE vs KEEP**
Owner exists → 301 or retarget. Has impressions/inlinks → do not DELETE without 301. Thin/off-territory/scaled → IMPROVE if unique help, else 301/410. Wins distinct queries → KEEP, additive only.

**NEW vs REFRESH**
Name the intent; search the portfolio. Owner exists → refresh that URL. No owner, demonstrated need, not a synonym → new URL then hub links. Telegram anecdote → do not create.

**WAIT vs INTERVENE**
Spam-policy match or index bug → act. Core-update volatility → watch 4–8 weeks. New property < 8 weeks plateau → wait unless crawl is actually broken. Recovery can take months.

**TITLE vs BODY**
Intent still matches, positions ~4–15, CTR below median → title cohort, H1 fixed. Intent mismatch → body. Winner → do not retitle for excitement. Stale snippet date → rewrite substance so the date changes honestly.

**ARTICLE vs TOOL vs SERVICE**
Transactional → service owner. Learning a method → knowledge guide + honest anchor. Calculator/file and no owner → tool only after need is shown. Clinical → out of this factory.

**INDEX vs NOINDEX**
Public canonical → index in first HTML. Thin parameters → 301/410 over eternal noindex. Do not noindex a hub you still need as a linker. Schema/sitemap/E-E-A-T do not buy indexation.

## Do not adopt

Click-fraud on reportage; two-day outage recrawl; DA inflation via Google redirects; Money Robot mentions; popups; friends-search-us; auto-refresh “most visited”; buying expired domains to rank unrelated content; date-only freshness; 800-word minimum / mandatory AMP; fake review stars on articles; llms.txt as a ranking project; detector-evasion; medical content in this factory; guest-post link hijacking / negative SEO; combinatory template URLs (host × feature × city).

Evaluate the **claim**, not the person.

## Factory tab rules

| Tab | This skill may |
|---|---|
| SEO Field Corpus / SEO Experiments | Additive source of truth |
| Research Library | Synthesised reusable findings only |
| Research Refresh Queue | Substance-first candidates; ban date-only |
| Editorial Queue | Depth, trees, FAQs, examples — still written by Qalam |
| SEO Signals | Our observations only |
| Hierarchy & Links | After canonical ownership; no imported cluster model |
| Service Anchor Map | Do not move commercial owners because a Telegram post suggested an anchor |
| Config / Mistral_Instructions | Almost never. Promote only if repeated, verified, broad, stable |
| Personal Research Intake | Maziyar’s notes, not scrape dumps |
| Site Profiles | Read first. Do not invent sister-site owners |

## Teznevise specifics

Known commercial owners:

- `/thesis/` مشاوره پایان نامه
- `/proposal/` پروپوزال
- `/service-statistics/` تحلیل آماری
- `/service-simulation/` شبیه سازی
- `/service-project/` پروژه تخصصی
- `/blog/` knowledge centre (not a commercial owner)

Live IA also has overlapping `/contact/` vs `/contact-us/` — treat as P0 intent collision.

No U+200C in Teznevise Persian.
Advisory framing: do not sell ghostwriting as `انجام پایان نامه`.
Sister-site map was not in the sandbox snapshot — do not invent owners.
Do not publish website changes merely because scraping produced a finding.

## Priorities

- P0 factual, index, canonical, crawl, major IA
- P1 commercial/canonical URLs with impression potential or positions 1–2 pages
- P2 existing impression URLs missing a decision, example, or internal link
- P3 gaps with a clear owner and demonstrated need
- P4 speculative new content (default: off)

## Coverage honesty (snapshot 2026-09-15)

| Source | Inspected | Gap |
|---|---|---|
| ShahramRahbari | 2001 posts, 2018-11-04 → 2026-09-15 | Videos not transcribed |
| TheSEOCommunity | 0 | Join-only group; no public preview |
| mahdi_araqii | 370 | Lower prior; 5 videos not transcribed |
| MoradiSEOPR | 35, all 2022-05-09 | 19 course videos inaccessible |

Q&A reconstruction uses quoted questions in the Shahram channel as a **proxy**, not as the group history.

## Anti-patterns for agents using this skill

- Turning one ecommerce anecdote into “Google always…”
- Averaging two contradictory claims into mush
- Creating a synonym URL to “cover” a wording
- Changing a winning slug
- Mixing medical evidence into this factory
- Replacing Qalam with a second writing prompt
- Treating DA/PA/LSI as Google systems
- Shipping READY_TO_APPLY payloads that already have an approved exact text

## Compact rule

Decide like an editor with a memory: who owns this intent, what evidence we actually have, what would falsify the next step, and whether Qalam should write a surgical patch — not a new page.
