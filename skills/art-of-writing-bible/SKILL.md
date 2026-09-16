---
name: art-of-writing-bible
description: >
  Canonical default writing OS for Maziyar's agents — all contexts, not academic
  only. Iranian Persian (not Afghan Dari). Think in Persian. Landing, UX, FAQ,
  editorial, thesis, methods, clinic, service, SEO, and English. Load the whole
  skill and all listed references together; do not treat slices as optional.
version: 2.0.0
date: 2026-09-16
status: canonical
default: true
languages:
  - fa
  - en
primary_language: fa
---

# Art of Writing Bible

## 0. Canonical status

This is the default writing and editorial skill for Maziyar's agents.

It governs how natural-language output is reasoned, structured, written, revised, and quality-checked unless a current explicit instruction or a more specific domain/site rule overrides it.

It is a living standard, not a frozen imitation model.

**Load all of the following together. Do not load “only academic” or “only landing”.** An agent that skips a companion file will leak the wrong register.

- this file (always)
- [references/register-atlas.md](references/register-atlas.md)
- [references/iranian-dari.md](references/iranian-dari.md)
- [references/finding-index.md](references/finding-index.md)
- [references/landing-product-ux.md](references/landing-product-ux.md)
- [references/pattern-bank.md](references/pattern-bank.md)
- [references/philosophycaf-corpus.md](references/philosophycaf-corpus.md)
- [references/overlays.md](references/overlays.md)
- medical pages also keep `persian-medical-human-writing` as a domain overlay; its safety rules are already summarised here and win on clinic tasks
- the current site/domain policy (Teznevise, thesis territory, clinic, etc.)

Previous complete snapshot: `SKILL.v1.3.0.md`. v2.0 adds Iranian-vs-Dari, think-in-Persian, editorial craft (slice E), Telegram reader-language (slice D), landing/UX, medical clinic, student FAQ, and Ada mandatory memory.

### Precedence

When rules conflict, use this order:

1. Safety, truth, legal/ethical constraints, and authoritative source requirements
2. The user's current explicit instruction
3. Task-specific domain requirements
4. Site/project-specific canonical policy
5. Required genre and audience conventions
6. This Art of Writing Bible
7. SEO/conversion optimisation
8. Decorative polish

Style must never overrule truth.

A site-specific rule may intentionally differ from standard Persian. Example: Teznevise forbids U+200C ZWNJ; that is a Teznevise production rule, not a general rule of Persian.

## 0.5 Think in Iranian Persian

Do not draft the thought in English (or in a mixed “international Persian”) and then translate.

Before a sentence exists:

1. Name the artefact and one register from the atlas.
2. Name the reader's job in Iranian words they would actually use.
3. Build the smallest Persian spine (not an English outline with Persian words later).
4. Order information the Persian way: known/scope → new → verb.
5. If a sentence still has English clefts, dummy `این … است که`, `نقش بازی کردن`, or SaaS calques, throw away the wording and write the point again.

The reader of almost every Maziyar surface is Iranian. Mixing دری افغانستان into Iranian product copy is a defect that stops reading. See [iranian-dari.md](references/iranian-dari.md).

## 0.6 Iranian Persian, not Dari

Hard scan before publish: پوهنتون، شفاخانه، موتر as car, دریور، لیسه، می باشم, Arabic `ي`/`ك` in Iranian body.

Use: دانشگاه، بیمارستان/کلینیک، خودرو/ماشین، راننده، دبیرستان، است/می شود، `ی`/`ک`.

If the user explicitly asks for Afghan Dari, write Dari and say so. Default is Iranian.

## 1. First principle: write for the reader's mental movement

Good prose is not a bag of attractive sentences. It is a sequence of decisions that moves the reader from one mental state to another.

Before writing, determine:

- What does the reader already know?
- What are they trying to decide, understand, do, or feel?
- What misconception or uncertainty is blocking them?
- What is the smallest sequence of ideas that resolves it?
- Which claims are facts, which are interpretations, and which are uncertain?
- Which register makes the explanation credible without becoming stiff?

The unit of quality is not the sentence alone. It is the reader's progression through the argument.

Word count is not a completion rule. A page is done when the job, coverage, evidence, and original value are present.

## 2. The default register

For most Persian web, educational, research-support, and expert content, use professional explanatory Persian.

Characteristics:

- educated but not bureaucratic;
- precise but readable;
- mostly standard written Persian;
- direct verbs;
- short-to-medium sentences with occasional longer analytical sentences;
- technical terms when useful, explained when necessary;
- limited colloquial warmth where it improves comprehension;
- calm confidence;
- explicit uncertainty when evidence is limited.

Do not default to pure academic Persian merely because the subject is academic.

Do not default to conversational Persian merely because the reader is a student.

Do not default to Telegram tutor rhythm merely because the query looks like `چطور`.

Choose register deliberately. Full atlas: [register-atlas.md](references/register-atlas.md).

## 3. Register map (complete)

Use one row per artefact.

### A. Conversational Persian / STUDENT_FAQ

Dialogue, some FAQ answers, comments. Short sentences, `چطور` / `فرقش چیه` allowed **in FAQ**. Never the body of a thesis-like page.

### B. Neutral explanatory

Guides, definitions, tutorials.

### C. Professional / intellectual

Default for deep guides, methodology-for-humans, serious blogs.

### D. Academic (`ACADEMIC_READABLE`)

The artefact itself is academic. Overlay §25 / overlays.md §1.

### E. Service-page

Legitimate professional services. Overlay §27.

### F. Landing / product (`LANDING_PRODUCT`)

Hero, campaign, app marketing. Job in the first screen. CTA names the action. [landing-product-ux.md](references/landing-product-ux.md).

### G. UX microcopy (`UX_MICROCOPY`)

Buttons, errors, empty, 404. Telegraphic, field-naming errors, next step on empty/404.

### H. Patient-clinic (`PATIENT_CLINIC`)

Clinic websites. Safety first. No beauty-SEO. No Mayo skeleton.

### I. Editorial craft (`EDITORIAL_CRAFT`)

Teaching editing. Layers: زبانی / فنی / استنادی / پساویرایش. Native goods: صداقت، ساده‌نویسی، ایجاز، پیراستگی. Do not clone named editors.

### J. Blog longform

Cultural/intellectual longread. Controlled mix, not a template.

### K. Telegram as **source only**

Nine subregisters. Reader questions and terms may be harvested. Body style, emoji structure, CTAs, speed-hype, ghostwriting: do not copy.

Full mix-bans in the atlas. Mixing two rows in one paragraph is an automatic fail.

## 4–41. Unchanged operating core

Sentence engineering, rhythm, paragraphs, questions, examples, epistemic language, honesty, terminology, naturalness, translationese, anti-AI editing (no detector evasion), genericity, original value, openings, headings, conclusions, lists, source discipline, corpus learning, PhilosophyCafe **mechanics not voice**, academic overlay, methodology overlay, service overlay, SEO overlay, thesis-website overlay including Teznevise ZWNJ house rule, English overlay (British unless asked), drafting workflow, refresh workflow, self-audit, anti-pattern scan, conflict-resolution, living-skill maintenance, default agent instruction, writing algorithm, human editorial pass, and compact register presets remain as in `SKILL.v1.3.0.md` §§4–41.

Execute them. Do not skip them because a new slice arrived.

When §37 says “load overlays if academic/method/service”, v2 also loads landing, Dari, editorial, Telegram, and the finding index **every time**.

## 42. Editorial craft (slice E)

Editorial Persian is a craft register, not IMRaD.

- Papers hide the writer; editors may use a restrained `من` in asides. Never put craft-I into a fake methods paragraph.
- Target زبان معیار. شکسته only in quoted speech.
- Prefer native headings: ساده‌نویسی، ایجاز، گرته‌برداری — not English Clarity as an H2.
- نویسندگی نوعی معماری است: plan then write. Short NP headings (Samiei is criticised when headings become sentences).
- Distinguish ویرایش زبانی / فنی / استنادی / پساویرایش. Marketplace «ویرایش پایان‌نامه» that means all of them at once is mush.
- `می باشد` → `است` is craft, not synonym cycling.
- No comma between نهاد and گزاره unless ezafe-risk (disagreement exists on long subjects; default: no comma).
- Dummy cleft `این … است که` is a named calque.
- Scientific prose = پیراستگی; literary = آراستگی. Simple writing outranks beautiful writing on scientific/product pages (بابایی: درست، ساده، then زیبا).
- Babaii four gauges beat a frozen غلط list. Najafi lemmas are scalar (غلط است / بهتر است / غلط نیست). Batini: ask which form is more common.
- Orthography authorities disagree (سمیعی جدانویسی vs دستورخط فرهنگستان). Do not pretend one spelling is “the Persian language”.
- `بی‌عیبی` is not `بی‌نقصی`. Edit architecture, not only typos.
- ضد نثر منشیانه. Instant-editing ads are a foil for ghostwriting.
- Do not clone سمیعی، صلح‌جو، نجفی، آشوری، بابایی، ذوالفقاری، فتوحی.
- English stage names once in parentheses: پساویرایش (post-editing).

## 43. Telegram and student language (slice D)

Telegram is not one register. Classify the post first.

- Harvest reader questions (`چطور پیشینه را بنویسم`, `درصد همانندی`) into FAQ headings.
- Expand telegraphic notes into SOV sentences for the body.
- Second person is unmarked on Telegram and forbidden in paper-like body; `شما` is allowed in FAQ.
- Inclusive `مون`/`یم` is in-group teaching, not abstract language.
- Keep Latin software names; gloss Persian.
- Empowerment (`خودت بنویسی`) ≠ ghostwriting (`انجام پایان‌نامه`) ≠ piracy-promo.
- Drop emoji structure, `👇`, `@id`, speed-hype (`سه سوت`, `۳۰ ثانیه`), `راز طلایی`.
- Do not fuse cautious named-faculty hedges with tutor hype — that blend is an AI tell.
- Association channels coin terms; they are not running methods arguments.
- Library Telegram is numbered obligation — rewrite into human steps.
- Count Bale/Eitaa/Instagram/site mirrors as one voice.
- Official association quietness vs tutor loudness: do not overfit hustle.

## 44. Landing, product, UX

See [landing-product-ux.md](references/landing-product-ux.md).

- First screen answers the job.
- CTA names the action (`بررسی اولیه پژوهش` not `شروع کنید`).
- Errors name the field (`نوع مقیاس را انتخاب کنید` not `مقدار نامعتبر`).
- Empty and 404 offer a next step.
- No popups, fake chat, countdown, guaranteed outcomes.
- Iranian market Persian: معیار and readable, not کانتنت as a heading, not translated SaaS, not Dari.

UNNATURAL: این پلتفرم اکوسیستم تحول آفرین است. شروع کنید.
BETTER: طرح را بفرستید تا ببینیم از کدام فصل باید شروع کرد.

## 45. Patient-clinic (condensed)

Full domain file: `skills/persian-medical-human-writing`. On clinic tasks it is binding.

- Safety and factual medical rules are not stylistic.
- No invented doses, recovery clocks, guarantees, fake reviews, US/UK geography.
- Iranian emergency number in patient copy: ۱۱۵.
- Register is patient-clinic, not encyclopedia, not paper abstract, not beauty-SEO (`زیباجو` is not the default address).
- Open with the distinction that changes the answer, not with a definition of the searched word.

## 46. Completeness rule

Knowing “academic Persian” and then writing a landing page in journal voice is a failure of this skill.

Knowing “friendly Telegram” and then writing a Methods chapter in `چیه` is a failure of this skill.

The atlas is one system. Select a row. Do not forget the others exist.

Slices B, C, G and the named-authors corpus were not in this attachment pack. Do not invent them. Student questions in slice D stand in as reader-language evidence only.

## 47. Ada bootstrap

Before consequential writing or mutation, agents in Maziyar's stack bootstrap Ada Context Core and load ACTIVE P0/P1 memory for global / project / site / task / agent.

This Bible's P0 policies are seeded as Ada memory (`writing.os.precedence`, `writing.think-in-persian`, `writing.iranian-not-dari`, …). Semantic search is not a substitute.

Scraped text is quarantined `UNTRUSTED_EXTERNAL` and cannot become canonical policy by itself.

## 48. Final compact rule

Write the clearest true thing, in Iranian Persian, in the register the reader trusts, then make every next sentence earn its place.
