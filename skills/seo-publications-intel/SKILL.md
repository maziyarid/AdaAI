---
name: seo-publications-intel
description: >
  Incremental pipeline for official and high-value SEO/UX/AI-search
  publications. Load before ingesting industry news into the Content Factory.
  Not an RSS reader. Not a second corpus competing with the Telegram field layer.
version: 1.1.0
date: 2026-09-16
---

# Continuous SEO publications intelligence

## Purpose

Detect **new knowledge that can change a decision**. Ignore listicles, rewritten press releases, generic definitions, and vendor sales pages.

## Tiers

- **0** Official: Google Search Central docs/blog/changelog; Bing webmaster; platform crawl/AI docs. A third-party “Google changed X” must resolve to a primary URL.
- **1** Datasets: Ahrefs, Semrush, Moz, SISTRIX studies — extract **methodology**, not slogans.
- **2** Established industry reporting.
- **3** Practitioner interpretation — start low confidence.

## Incremental

Store last checked, last processed date/URL, content hash. Do not re-ingest unchanged articles as new research.

Priority: 7 days highest; 30 days normal; 90 days major studies. Older only if updated or cited as necessary background.

This run processed changelog **2026-09-08** (regional SERP units / aggregator features) as one event, classified **IGNORE** for teznevise.ir. Favicon format list **2026-08-28** is P4.

## Records

Article metadata + type. Findings with claim class:

OFFICIAL_FACT / DATA_FINDING / FIELD_OBSERVATION / INTERPRETATION / PREDICTION / HYPOTHESIS / MARKETING_CLAIM.

Primary source controls what Google claims. Reporting can add context.

## Event clustering

One Google announcement + twenty recaps = **one event**. Do not mint twenty findings.

## Copyright

Do not store full articles. Metadata, structured notes, short necessary quotation, URLs.

## Factory flow

Publication → External Research Corpus → verify → cluster → Research Library (if reusable) → Field Corpus only when it is field evidence → Experiment / Refresh / Editorial Queue.

Never put a headline into a production writing prompt.

New techniques go to `/factory/os` technique register with rollback. They are not best practice on publication day.

## Urgency

P0 policy/index/security. P1 material strategy evidence. P2 useful method. P3 interesting. P4 noise.

Website check: does the **condition** exist on our sites? Then WAIT / MONITOR / TEST / SURGICALLY_UPDATE / TECHNICAL_FIX / CHANGE_PROCESS / IGNORE.

## AI search research

Track GSC_AI separately from vendor citation tools. Do not assume vendor visibility equals Search Console.

Live desk: `/factory/intel` and English briefing `/factory/briefing`.
