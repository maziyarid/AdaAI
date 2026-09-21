# PhilosophyCafe empirical corpus (Slice D, 2026-09-15)

Anchor channel: `@PhilosophyCafe` — `https://t.me/s/PhilosophyCafe`
Public only. No private dialogs.

This file is **language evidence**. It is not a voice model. It is not a factual encyclopedia of Wittgenstein, Freud, or Shakespeare.

---

## Research slice

- Assigned work: reverse-engineer how skilled contemporary Iranian writers on PhilosophyCafe construct readable, intelligent, natural prose — then keep only **transferable** mechanics.
- Date: 2026-09-15
- Scope: original explanatory / argumentative / conversational / reflective posts by recurring public contributors.
- Excluded from style derivation: translated literary excerpts, classical Persian, quotations, announcements, ads, 2016–2018 forwarded newspaper interviews, relationship-psychology English-code-switch essays, media-only, link-only.
- Orthography: the live channel uses ZWNJ. This file's constructed examples follow the Teznevise production rule (no U+200C) and therefore space-separate or join compounds. That is a **site rendering rule**, not a finding about Persian.

---

## Corpus method

1. Fetch public HTML preview pages (`t.me/s/PhilosophyCafe` and `?before=ID`) until `rel=prev` ended.
2. Parse post id, datetime, full text.
3. Classify provenance **before** extracting style.
4. Weight original contemporary writing 2022–2026 for sentence mechanics; use 2018–2021 mainly as quotation/forward context.
5. Cross-check transferable rules against independent slices A (academic), D-telegram (research/thesis Telegram), F (methodology practitioners).

Result of the **full public-preview walk** (2026-09-15): **5763** posts, **300** pages, IDs **6739–13521**, dates **2018-05-03 to 2026-09-15**, **5388** nonempty. Year coverage is continuous. The live preview currently bottoms out in May 2018. A prior stratified sample also held 2016–2017 dumps; those remain labelled quotation / `EXTERNAL_EXCERPT` and are not used for contributor sentence construction.

Original contemporary 2022–2026 after provenance filter: **1583** long items (signed Naderi 209, Soltanzadeh 305, plus unsigned workshop voice).

This walk is the public archive as Telegram currently serves it. Quality of original items still matters more than raw count.

### Channel profile

- Description: «مکانی متفاوت برای آدم های متفاوت»
- Named contributors: `@NaderiOmid66` (Omid Naderi), `@Ali_soltanzadeh` (Ali Soltanzadeh), `@khadem_ar` (Arman Khademi), `@M_H_Tavassoli`, `@AmiraliEbrahimzadeh`, `@Amin_sbu`
- ~3.36k subscribers at scrape time
- Created ~2020 as a listed entity; public posts exist from 2016 (older material was posted or forwarded into the visible archive)

### Two historical layers (do not mix)

| Era | Volume in walk | Dominant material | Use for style? |
|---|---|---|---|
| 2018–2021 | 2018: 1418, 2019: 785, 2020: 511, 2021: 683 | quotes, Nietzsche one-liners, forwarded interviews, book TOC, exam-resource lists | mostly NO, except a few signed essays |
| 2022–2026 | 2022: 711 … 2026: 318 | original explainers, literary commentary, translations clearly marked as such | YES for original writing |

Long original 2022–2026 items used for rates: **~1583–1589**. Median length ~1315 characters. Colloquial markers in ~62%. Academic-formula markers (`پژوهش حاضر`) **absent**.

---

## Provenance classification

Every retained item was labelled. Full-walk provenance (n = 5763 public posts; analyser also saw a few older sample IDs, hence ~5844 unique rows in `v2/summary.json`):

| Label | n (full walk mix) | Style weight |
|---|---|---|
| ORIGINAL_CONTEMPORARY | 1146 | 3 |
| LIKELY_ORIGINAL | 437 | 2–3 |
| SHORT_CONTEMPORARY | 611 | 1–2 |
| OLDER_MIXED | 3101 | 0 for sentence construction |
| TRANSLATED_OR_EXCERPT | 107 | 0 |
| EXTERNAL_EXCERPT | 48 | 0 |
| MEDIA_ONLY | 375 | 0 |
| QUOTATION | 19 | 0 |

High-value original 2022–2026 = ORIGINAL_CONTEMPORARY + LIKELY_ORIGINAL with length ≥ 280: **1583**.

**Rule:** a Chekhov / Winterson / Freud / Ibn Arabi / Saadi passage is evidence about the **translator or the source author**, not about the channel's sentence construction. Original frames around those passages (the 🗯 commentary, the millipede setup, the carpenter setup) may be original.

---

## Contributor map (without cloning)

| Contributor | Public role | Original register | Transferable? |
|---|---|---|---|
| Omid Naderi | Wittgenstein, philosophy of science, Lebensform | mixes educated written Persian with spoken-like teaching; analogy; numbered distinctions; self-upgrade (`یا قوی تر`) | mechanics YES; catchphrases NO |
| Ali Soltanzadeh | literature, history of ideas, cultural objects | written-colloquial throughout (`یه`, `می دونن`, `توی`); first person; quote-then-comment | hinge YES; objects and 🗯 habit NO |
| Unsigned 2022–2026 | often same workshop voice as Naderi | analogy, question-pivot, register drop | treat as PC-STRONG if the move recurs |
| Arman Khademi | Freud / psychoanalytic excerpts | mostly translation frames (27 signed mentions) | low |
| Tavassoli / Ebrahimzadeh / Amin | named in the channel description | too few original items (11 / 5 / 3 mentions) | do not generalise |

`AUTHOR_SPECIFIC — DO NOT GENERALISE`: millipede story, carpenter book-title gag, toolbox as house metaphor, «حضرت ویتگنشتاین», «پرسش کوفتی», Game of Thrones recap → Hobbes, 2017 English-code-switch relationship essays.

---

## Comparison corpus (independent)

Used to stop PhilosophyCafe quirks from becoming "how Persian works":

- Slice A — Iranian علمی پژوهشی articles and author guidelines
- Slice D telegram — thesis/statistics/education channels
- Slice F — Pars-Modir, Kiara, Faradars, Cochrana, etc.
- GeminiDS / PerplexityDS as corroboration only

A rule is COMMON if it appears in PC original writing **and** in at least one independent slice, or is the default of educated Iranian prose. A rule is PC-STRONG if it is characteristic of this intellectual-explanatory register but not of thesis-mill Telegram or journal abstracts.

---

## High-confidence findings

IDs below are language findings. Confidence: high unless noted.

### Sentence architecture

**FN-01** Original explainers start with a **job**, a distinction, a scene, or a compact claim — not with the existence of the article. (PC-STRONG, COMMON with slice A abstracts which also skip `در این مقاله قصد داریم`.)

**FN-02** Information order is Persian: known / condition → new → verb. English subject-first calques feel translated. (COMMON)

**FN-03** Long sentences exist and are fine when they carry one argumentative arc. They are braked by a short sentence. Uniform medium length is the AI tell, not length itself. (PC-STRONG)

**FN-04** `که`-clauses stack for a reason; decorative stacking is inflation. (COMMON with A)

**FN-05** Verb-final order is kept. Journalistic verb-fronting is rare in original PC explainers. (COMMON)

**FN-06** `نه X بلکه Y` is a workhorse distinction machine. (PC-STRONG, COMMON)

**FN-07** Parenthetical Latin citations `(Wittgenstein, 2009, §201)` appear in the academic-explanatory subregister. They are REGISTER-SPECIFIC; do not export into service pages.

### Clause order and rhythm

**FN-08** Recurring rhythm: long explanation → short correction → question → example → medium restatement. (PC-STRONG)

**FN-09** Recurring rhythm: claim → اما → hidden assumption → sharper claim. (PC-STRONG, COMMON)

**FN-10** Paragraph-final short sentences are used as brakes, not as slogans. (PC-STRONG)

**FN-11** Numbered 1/2/3 appears when the thought has three jobs, not because lists convert. (PC-STRONG)

**FN-12** Telegram single-clause-per-line is platform scaffolding. On the web, rejoin into paragraphs. (REGISTER: Telegram)

### Questions

**FN-13** Questions that **change the type of next move** are native (`پس راه خروج چیست؟`, `چرا این مهم است؟`). Questions that advertise the rest of the article are promotional (slice D service channels). (PC-STRONG vs D-SEO)

**FN-14** Question → immediate answer is common. Leaving a rhetorical question hanging is rare in the good original posts. (PC-STRONG)

**FN-15** `یعنی چه؟` / `منظورم چیست؟` function as reformulation cues, not as confusion. (PC-STRONG)

**FN-16** Academic research questions stay indirect (`آیا`, `چگونه`). Conversational explainers may be direct. (REGISTER)

### Restatement

**FN-17** Useful restatement changes **altitude**: abstract → plain → consequence. Empty restatement changes **synonyms**. (PC-STRONG)

**FN-18** `به بیان ساده تر` / `به عبارت دیگر` / `یعنی` are legitimate **once** after density. Repeating them every sentence is an AI tell. (PC-STRONG, COMMON, also an anti-pattern when stacked)

**FN-19** Self-upgrade (`دقیق تر بگویم`, `یا قوی تر`) is a human reasoning move. (PC-STRONG)

### Analogy and example

**FN-20** Difficult ideas are often **preceded** by an ordinary situation (repairing, walking, cycling, tools). (PC-STRONG)

**FN-21** The return from analogy is explicit. Without return, the story is decoration. (PC-STRONG)

**FN-22** Analogies are simple and local, not "imagine you are a scientist unlocking mysteries". (PC-STRONG, F)

**FN-23** Do not reuse source analogies. Invent new ordinary scenes. (editorial)

### Register switching

**FN-24** The same writer may explain a distinction in relatively formal Persian and land the point in spoken-like Persian (`پس فلسفه چیکار می کنه؟ هیچی`). The drop is **functional**. (PC-STRONG)

**FN-25** Written-colloquial (`یه`, `می شه`, `رو`, `دیگه`) is native in INTELLECTUAL_CONVERSATIONAL. It is off-register in ACADEMIC_READABLE and in service headings. (PC-STRONG + A + D)

**FN-26** Object marker: `را` in formal body; `رو` in deliberately conversational segments. Mixing inside one bureaucratic sentence is a clash tell (D). (COMMON)

**FN-27** Do not import journal `مقاله حاضر` into a cafe explainer; do not import `شما کاربران عزیز` into a thesis chapter.

### Epistemic and personal voice

**FN-28** First person marks interpretation (`به نظرم`, `من می خواهم نشان دهم`), not prestige. (PC-STRONG)

**FN-29** Academic artefacts prefer `پژوهش حاضر` / `نگارنده`. (A) Do not flatten these into one universal pronoun rule.

**FN-30** Hedging is dense where the claim is inferential; absent where the claim is a definition. Performative hedging of obvious facts is fake caution. (PC-STRONG + A)

**FN-31** Self-correction and "دوباره باید تاکید کنیم" are honesty moves. (PC-STRONG)

**FN-32** `ما` is often pedagogical, not royal. (PC-STRONG)

**FN-33** Direct `شما` appears in teaching (`شما داری زندگیت رو می کنی`). Zero in journal articles. (REGISTER)

### Verbs and lexicon

**FN-34** Strong prose chooses a precise verb (`نشان می دهد`, `رفع می کند`, `خنثی می کند`, `سنجد`) over a noun pile. (PC-STRONG + Bible 4.3)

**FN-35** Bureaucratic verbs (`می گردد`, `می باشد`, `اقدام نمودن`, `صورت پذیرفت`) are rare in original PC explainers; common in university notices (D) and older textbooks. Avoid in reader-facing web copy. (COMMON)

**FN-36** `است` is the definitional copula. `هست` is emphasis or speech. (D, F)

**FN-37** Software and index names stay Latin (`SPSS`, `RMSEA`). Technique names stay Persian (`تحلیل عاملی اکتشافی`). (F, D)

**FN-38** `پروپوزال` is universal; do not invent a "pure" equivalent. (D)

**FN-39** Fix a term and repeat it. Synonym roulette is an AI/SEO tell. (COMMON)

### Transitions

**FN-40** Contrast: `اما` is the engine. `ولی` more spoken. `لذا` is formal-heavy (A). Default consequence: `بنابراین` / `از این رو` / `پس`. (COMMON)

**FN-41** Do not stack two consequence markers. (A)

**FN-42** Semantic transition beats explicit signposting. A new paragraph or heading is often enough. (PC-STRONG)

**FN-43** `لازم به ذکر است` marks notice/textbook register. Prefer `نکته:` or just say the note. (D, F)

### Paragraphs and headings

**FN-44** A paragraph has a job. If it only rephrases the previous one, cut it. (Bible + PC)

**FN-45** Telegram emoji bullets (`🔹`, `✅`) are platform. Convert to real lists on the web. (D)

**FN-46** Headings in educational Persian: `X چیست؟`, `چگونه ... کنیم؟`, `تفاوت X و Y`, `N اشتباه رایج`. Academic headings stay noun phrases (`روش پژوهش`). (D + A)

**FN-47** Question headings are genre-dependent. Fine in guides; wrong as Results headings. (COMMON)

### Punctuation and visual rhythm

**FN-48** Emphasis quotes: Persian guillemets `«...»`. (A, PC)

**FN-49** Hashtag clusters and symbol rulers are Telegram. Strip for web. (D, PC)

**FN-50** Ellipsis in PC original writing often means a thought trailing into the next move, not "and more features...". Feature-list ellipsis is sales. (REGISTER)

### Edited conversational Persian

**FN-51** Keep: direct order, questions, `اما`, ordinary verbs, one `رو` zone, pedagogical `ما`.
Remove: filler, unfinished references, doubling the same clause, untranslated English where Persian is standard.

**FN-52** "Edited speech" is the target of INTELLECTUAL_CONVERSATIONAL: it can be read aloud without becoming a transcript. (PC-STRONG)

### Anti-translationese

**FN-53** `نقش X را بازی می کند` → `نقش X را به عهده دارد` / a real verb. (A, GeminiDS)

**FN-54b** `توسط` is native when it names a narrative or historical agent («روایت می شود توسط آنری»، «افسون شدن فهم توسط زبان»). The translationese to rewrite is only the method-passive calque «داده ها توسط SPSS تحلیل شد» → «داده ها با SPSS تحلیل شد». Do not blanket-ban `توسط`. (PC original 2022–2026: ~10% of posts contain the word; sampled contexts were almost all narrative.)

**FN-55** `این روش، روشی است که...` → `این روش برای ... به کار می رود`. (F)

**FN-56** `در پایان روز` and other idiom maps: rewrite from meaning. (A)

**FN-57** Do not treat every formal construction as translationese. Academic density can be native. (A vs F)

### Anti-AI (corpus distribution, not a detector)

**FN-58** Sweeping temporal openers are absent from original PC explainers and from Iranian abstracts. Ban them. (PC negative evidence + A)

**FN-59** Adjective-stack tool boilerplate (`قدرتمند، جامع، یکپارچه`) circulates in thesis Telegram via reposts. Ban. (D)

**FN-60** Structural symmetry of every paragraph is not how PC original threads develop. Thoughts are lopsided on purpose. (PC-STRONG)

**FN-61** Absence of uncertainty is a tell when the topic is interpretive. (PC-STRONG)

**FN-62** Do not add random errors, slang, or burstiness to "look human". 2026 evidence: generation and editing leave different traces; genre dominates; marker lists reverse. (external research + user constraint)

**FN-63** Register clash inside one sentence is one of the strongest unnaturalness markers. (D)

### Reader engagement

**FN-64** The reader is treated as a thinking adult, not as `کاربران عزیز`. (PC-STRONG)

**FN-65** Student copy should open from a situation (deadline, reviewer objection, stuck stage), then reframe with the precise term. (D, G)

**FN-66** Flattery vocatives (`دوست عزیز`) mark the seam into CTA on service Telegram. Strip for editorial prose. (D)

### Academic vs cafe (do not flatten)

**FN-67** Journal Persian: third-person nominal author, agentless methods, hedged findings, IMRaD-ish headings, no `شما`. (A)

**FN-68** Cafe explanatory Persian: pedagogical `ما`/`شما`, analogies, questions, register drops, first-person interpretation. (PC)

**FN-69** A thesis website needs **both**, never a blend in one paragraph. Choose the artefact's register first.

**FN-70** `مورد بررسی قرار گرفت` is native in current academic Persian (A) even if purists dislike it. In web explainers, prefer `بررسی شد`. Soft anti-pattern only when stacked. (A vs F)

**FN-71** Methodology pages: define in third person, then steps in second-person or pedagogical first-person plural. (F)

**FN-72** Empty methods (`کیفی توصیفی تحلیلی`) is a canonical defect. Force data source, sampling, analytic technique, tool. (A, F)

**FN-73** Language naturalness ≠ statistical truth. PC and F both contain fluent sentences with contestable claims. Fact-check separately. (F, PC design)

**FN-74** ZWNJ is standard in the live PC corpus (**82.8%** of original 2022–2026 long posts). Teznevise forbids it. Do not teach agents that "real Persian has no half-space". (site vs language)

**FN-75** `مقاله حاضر` / `پژوهش حاضر` occur in **0.0%** of original 2022–2026 long posts. Journal self-reference is REGISTER-SPECIFIC to academic artefacts. (PC negative + A)

**FN-76** `لازم به ذکر است` **0.1%**; line-start `همچنین` **0.3%**; `تضمینی` **0.1%** in original explainers. These are notice/sales tells, not intellectual-explanatory Persian. (PC negative + D)

**FN-77** Teaching `شما` appears in **12.6%** of original long posts. Zero in journal articles. REGISTER. (PC + A)

**FN-78** `نه X بلکه Y` in **11.5%**; `یعنی` in **30.0%**. Distinction and altitude-change are workhorses, not decoration. (PC-STRONG)

**FN-79** `جهت` is native in `از این جهت` / `به این جهت`. The defect is bureaucratic `جهت سفارش` / `جهت نیل به`. Do not blanket-ban the word. (PC + D)

**FN-80** Other named handles besides Naderi and Soltanzadeh lack original mass. Do not mint style rules from excerpt frames. (coverage finding)

---

## Composite model (not a person)

Name: `CONTEMPORARY_IRANIAN_INTELLECTUAL_EXPLANATORY_PERSIAN`

1. Opens with the actual point, a scene, or a distinction.
2. Introduces ideas by use, not by museum definition.
3. Asks a question only to change the viewpoint.
4. Moves abstract → concrete → abstract-plus, or concrete → concept.
5. Glosses terminology once, then stays loyal to one term.
6. Mixes colloquial warmth **locally** when it helps seeing; returns to precise diction for the distinction.
7. Marks interpretation as interpretation.
8. Lets paragraphs do one job; varies shape with the thought.
9. Ends a beat with a criterion or a short brake, not with `در نهایت می توان گفت`.
10. Avoids temporal fluff, synonym stacks, guarantee language, detector hacks, and anyone's catchphrases.

---

## Disagreements and uncertainty

- How much colloquialism a thesis **service page** should borrow from cafe writing: keep near zero in headings and deliverables; allow a little in FAQ empathy. Positioning choice, not a language law.
- First-person plural in qualitative theses: journals increasingly tolerate it; many manuals still want passive. Follow the artefact.
- `می باشد`: dead in modern explainers; still seen in management articles. Default `است`.
- Theme: `مضمون` vs `تم` — gloss once, then one term.
- Public preview does not currently paginate earlier than May 2018. Treat 2016–2017 material from the older sample as quotation/interview dump.

---

## Recommendations for the master skill

1. Load register first. Cafe mechanics are for INTELLECTUAL_CONVERSATIONAL / BLOG / RESEARCH_GUIDE, not for Methods chapters. Academic / method / service: load `overlays.md`.
2. Learn the move, not the signature.
3. Strip Telegram scaffolding before judging naturalness.
4. Keep impersonal service passives (`انجام می شود`); they are native.
5. Ban detector-evasion explicitly.
6. Keep fact review independent of language review.
7. Invent new examples every time.

See `pattern-bank.md` for operational templates and constructed examples.
See `overlays.md` for academic, method, and service execution rules.
See `SKILL.md` v1.3 for the writing algorithm and human editorial pass.
