---
name: persian-medical-human-writing
description: >
  Write and edit Persian medical/clinic website content so it reads like a
  careful Iranian human editor, not generic AI, translated Mayo/NHS copy, or
  beauty-clinic SEO. Use whenever drafting, rewriting, reviewing, or outlining
  Persian copy for Dr Bastaninejad or similar clinics: service pages, medical
  articles, FAQs, booking/visit copy, patient education, titles, meta
  descriptions, CTAs, headings, snippets, reception/staff wording, and
  competitor-inspired revisions. Also use when the user pastes writing they
  like or dislike, competitor URLs, clinic feedback, or phrases to ban, so the
  voice can be refined. Do not use for academic papers, English copy, invented
  medical facts, fake reviews, or guarantees.
version: 0.2-corpus-informed-draft
language: fa
status: not-final
---

# Persian Medical Human Writing

Teach the model to **think like an editor** before it writes. Phrase lists are
memory aids, not the skill. If a sentence is medically cautious, useful to a
worried Iranian patient, and sounds like a competent clinic writer said it
aloud, it is closer to the target than any keyword-shaped paragraph.

This skill is **not final**. Do not treat it as locked until several live clinic
pages have been written with it and compared with human-written Persian the
clinic actually likes.

Load [references/registers-and-corpus.md](references/registers-and-corpus.md)
when judging a source, choosing a register, or analysing a competitor page.
Load [references/pattern-bank.md](references/pattern-bank.md) when checking
rhythm, openings, headings, or whether a pattern is confirmed or tentative.

---

## 0. Editorial stance — think before writing

Do this silently, in order. Do not dump the answers into the page.

1. **Job of the page.** What is the reader trying to decide or calm down about?
   Example jobs: “Is revision even relevant for me?”, “What happens at the visit?”,
   “When is this swelling still normal?”
2. **Register.** Choose one: `patient-clinic` (default), `staff`, `encyclopedia`,
   `academic`. Clinic websites almost always want `patient-clinic`. Do not borrow
   sentence style from the other three. Terminology and caution may be borrowed.
3. **Patient state.** Assume a real person in Iran, often anxious, comparing
   several surgeons, reading on a phone, skim-reading, and allergic to sales copy.
4. **What must not be claimed.** List the tempting overstatements for this topic
   (best, guaranteed, no risk, exact recovery day, copied statistics) and refuse them.
5. **What the clinic actually does.** In-person visit, real services, real fee,
   real booking steps. Do not describe a workflow the clinic does not run.
6. **What the piece will deliberately not say.** Human editors omit the obvious,
   the encyclopedic, the US/UK-centric, and the duplicated idea. Decide the omissions
   first.
7. **Only then write.** Open with the answer or the useful distinction, not with
   a definition of a word the reader already searched.

If a later sentence would fail step 4 or 5, cut it. Do not “balance” it with a
disclaimer tacked on the end.

---

## 1. Two layers — never mix them

Keep **medical/factual rules** and **stylistic preferences** in separate hands.

| Layer | Hardness | Examples |
|---|---|---|
| Medical / factual | Binding. Do not relax for tone, SEO, or clinic marketing. | No invented doses, recovery days, diagnosis from a symptom list, fake stats, fake quotes, guarantees, “no complications”. |
| Stylistic | Preference, with evidence tags. A rule from one example is *tentative*. | Sentence length, headings, «بیمار» vs «زیباجو», how much Latin to keep. |

If style and safety conflict, safety wins. If SEO and natural Persian conflict,
Persian wins. If a competitor sentence is fluent but makes a medical claim this
clinic cannot stand behind, do not imitate the claim.

Mark any new stylistic rule as:

- **confirmed** — seen in several sources or explicitly approved by the clinic;
- **tentative** — one example, or clinic preference not yet given.

---

## 2. Register map

Four Persian medical languages showed up in the first corpus round. They are
not interchangeable.

### A. Patient-clinic (target)

Calm, specific, practical, slightly formal without bureaucracy. Talks to one
reader. Names what happens in the room. Qualifies what varies by person.
Does not define “بینی”. Does not announce “در این مقاله قصد داریم”.

### B. Translated consumer encyclopedia (Nabz Group magazine, most `عمومی` articles)

Useful as a **negative/partial** model. Typical skeleton: definition → symptoms →
causes → risk factors → diagnosis → treatment → prevention → «جمع‌بندی»/«سخن آخر».
Openings often calqued from Mayo Clinic / NHS / Our World in Data. English
parentheticals, US/UK facts (Fahrenheit, FDA, “در انگلستان”), titles like
«هر آنچه باید بدانید». Borrow **attitude** from the better pieces (when to see
a doctor, symptom ≠ disease, “پزشکان دقیقاً نمی‌دانند”) — not the skeleton,
not the geography, not the title formulas.

### C. Academic Persian (Noormags / SID papers)

IMRAD abstracts: «سابقه و هدف»، «مواد و روش‌ها»، «یافته‌ها»، «نتیجه‌گیری».
Dense «می‌باشد», long compounds, hedged conclusions. Borrow **terms**
(رینوپلاستی، سپتوپلاستی، قوز پشتی، تیغه میانی، زاویه نازولبیال) and **hedging
discipline**. Do not copy abstract syntax onto a clinic page.

### D. Beauty-SEO / SID blog register (anti-pattern)

«زیباجو»، «یک تیر و دو نشان»، «راه حل دائمی و کامل»، «بینی دلخواه شما»،
price-as-hook, “با ما همراه شوید”. Fluent and commercial. Do not use this voice
on Dr Bastaninejad pages.

A page may **consult** B or C and must still **sound like** A.

---

## 3. Priority order

1. Medical correctness and safety
2. Natural Iranian Persian
3. Patient usefulness
4. Trust and credibility
5. Search intent
6. SEO refinement

Never sacrifice 1–4 for keyword insertion.

---

## 4. Patient psychology

The reader is not an empty vessel for “آموزش”. Common states:

- fear of a botched result or of being upsold;
- shame about caring how they look;
- confusion between breathing and shape;
- impatience with swelling and with “it depends”;
- comparison-shopping, so unsupported superlatives feel like ads;
- mobile skimming — if the first screen is a textbook definition, they leave.

Write to that person. Reassurance must be precise (“نتیجه در افراد مختلف یکسان
نیست”) rather than warm fog (“با خیال راحت به ما بسپارید”). Do not moralise
beauty-seeking. Do not flatter. Do not scare with exclamation marks
(“احتمال مرگ دارد!”). Put genuine red flags in plain sentences and tell them
who to call.

---

## 5. Clinic voice

Calm, professional, specific, respectful, non-salesy. Confident without
superiority. Reassuring without false reassurance.

Do not write:

- «بهترین جراح بینی»
- «تضمین نتیجه»
- «بدون عارضه» / «صددرصد ایمن»
- «بهترین کلینیک زیبایی تهران»
- «پایتخت جراحی بینی جهان» (even when an old paper repeats the press line)
- «راه حل دائمی و کامل»

Prefer:

- «انتخاب روش جراحی به معاینه، ساختار بینی و هدف درمان بستگی دارد.»
- «نتیجه جراحی در افراد مختلف یکسان نیست.»
- «زمان مناسب برای جراحی ترمیمی پس از معاینه و بررسی روند ترمیم مشخص می‌شود.»

Address the reader as «شما» where a decision or action is theirs; use «بیمار»
when speaking generally. **Tentative, pending clinic:** prefer «بیمار» /
«مراجعه‌کننده» over «زیباجو».

Staff-facing copy is operational, not developer-facing. See §10.

---

## 6. Persian that sounds Iranian

Write ordinary current Persian used by educated Iranian readers. Prefer verbs
people actually say: «می‌شود»، «می‌تواند»، «بستگی دارد»، «بررسی می‌شود».
Avoid bureaucratic «می‌باشد»، «می‌گردد»، «می‌نماید» on patient pages (academic
layer may use them; clinic pages should not).

Keep «ی» and «ک» Persian. Use Persian digits in patient-facing copy unless a
unit, code, URL, schema field, or medical convention needs Latin digits
(HIV, 38.3 °C if that unit is required).

### Sounds Iranian

- «اگر هنوز ورم بینی زیاد است، درباره نتیجه نهایی زود قضاوت نکنید.»
- «در جلسه معاینه، وضعیت تیغه بینی، پوست و ساختار غضروفی بررسی می‌شود.»
- «اگر سابقه بیماری یا داروی خاصی دارید، قبل از مراجعه اعلام کنید.»

### Sounds translated (live in the Nabz corpus)

- «این امکان را می‌دهد که با محیط اطراف خود تعامل برقرار کنیم.»
- «ارائه‌دهنده مراقبت‌های بهداشتی»
- «پلن درمانی»، «ریسک فاکتور»، «گایدلاین» as default words
- «مراقبت‌های اولیه» used as if the reader works in a US clinic
- «بدن شما» repeated as a calque of English *your body*
- «X اصطلاحی است که به هرگونه … اطلاق می‌شود.»

### Banned as defaults (AI + magazine SEO)

«در دنیای امروز» · «یکی از مهم‌ترین موضوعاتی که باید به آن توجه داشت» ·
«در این مقاله قصد داریم» · «همانطور که می‌دانید» · «در نهایت می‌توان گفت» ·
«با ما همراه باشید» · «از صفر تا صد» · «همه چیز درباره» · «هر آنچه باید بدانید» ·
«راهنمای جامع و کامل» · repeated «لازم به ذکر است» · repeated «نکته مهم این است که» ·
«سخن آخر» / «کلام آخر» as obligatory closings · «بهره‌گیری از جدیدترین متدهای روز دنیا»

### Confirmed calques to rewrite

| Avoid as default | Prefer |
|---|---|
| ریسک فاکتور | عوامل زمینه‌ساز / عوامل مستعدکننده |
| پلن درمانی | برنامه درمان / مسیر درمان |
| گایدلاین (patient page) | توصیه بالینی / راهنمای درمانی, if needed at all |
| پروسیجر | روش / جراحی / اقدام |
| زیباجو | بیمار / مراجعه‌کننده (tentative) |
| ارائه‌دهنده مراقبت سلامت | پزشک / کلینیک |

---

## 7. Rhythm, openings, headings, transitions, closings

### Rhythm

Vary sentence and paragraph length. Short sentence for the point. Medium
sentence for the mechanism. A longer sentence only when a medical distinction
needs both parts held together.

Do not make every paragraph the same width. Do not give every heading exactly
three bullets. Symptom lists may be bullets; explanations should not.

### Openings — what to do

Answer the query or name the distinction that changes the answer. A good
opening often:

- assumes the reader already knows the topic exists;
- names 2–4 variables that actually matter (skin, cartilage, breathing, timing);
- refuses a common false certainty.

Do **not** open with: a definition of an obvious word; global importance
(“یکی از شایع‌ترین عمل‌ها در جهان”); a stack of rhetorical questions the article
will “answer below”; «در ادامه با ما همراه باشید».

### Headings

Patient-centred, as if asked at reception:

- «چه زمانی جراحی ترمیمی بینی انجام می‌شود؟»
- «ورم بینی تا چه زمانی طبیعی است؟»
- «قبل از معاینه چه اطلاعاتی را آماده کنید؟»

Keep «چه زمانی باید به پزشک مراجعه کرد؟» when the page needs a real safety
threshold. That convention is **confirmed** useful.

Avoid keyword slabs («جراحی بینی تهران هزینه») unless the search query truly
is the heading. Avoid Latin-first headings («Lumbar Puncture چیست؟») on clinic
pages; lead with Persian unless the user searched the Latin term.

### Transitions

Do not march «از سوی دیگر»، «علاوه بر این»، «همچنین»، «در نتیجه» down the page.
A new heading is often the transition. If two sentences say the same thing,
delete one rather than bridging them.

### Closings

A closing is optional. If used, make it a practical next step (what to bring,
how to book an in-person visit, what not to judge yet). Do not add «جمع‌بندی»
or «سخن آخر» because magazines and models do. Do not restate the whole page.

---

## 8. Medical safety and fact-checking

For every medical claim, classify it:

- established fact;
- common clinical guidance;
- context-dependent;
- uncertain;
- patient-specific;
- clinic-policy (workflow, fee, what this clinic offers).

If patient-specific or context-dependent, say so in the sentence, not in a
footnote.

Good:

- «زمان بازگشت به فعالیت عادی به نوع جراحی، میزان ورم و روند ترمیم شما بستگی دارد.»
- «اگر خونریزی شدید، تب، درد غیرعادی یا علائم نگران‌کننده دارید، با پزشک یا مرکز درمانی تماس بگیرید.»

Bad:

- «بعد از ۷ روز می‌توانید کاملاً به زندگی عادی برگردید.»
- «این روش هیچ خطری ندارد.»
- «این علائم یعنی شما X دارید.»

Hard bans:

- inventing doses, contraindications, recovery clocks, diagnostic claims;
- inferring a diagnosis from a generic symptom list;
- publishing unsourced statistics, or copying WHO/IHME/US figures onto an
  Iranian clinic page as if they were local or the clinic’s outcomes;
- copying one paper’s anthropometry (angles, percentages, “بینی ایرانی”)
  into marketing;
- fake quotes, fake reviews, fabricated patient stories;
- US/UK operational facts presented as Iranian practice (Fahrenheit cut-offs,
  FDA drug lists, “در انگلستان شایع‌ترین راه…”, neonatal pathways that are NHS).

For Iranian emergencies in patient copy, «۱۱۵» is the local number
(**confirmed** in corpus). Do not send an Iranian reader to 911 or “your GP”.

If uncertain, rewrite conservatively. When sources are supplied, use only what
they support. Distinguish established guidance from this clinic’s policy.

---

## 9. How to explain medical terms

Pattern that reads naturally in Persian medical prose (**confirmed**):

> everyday Persian first, then the specialist term if it helps, Latin in
> parentheses only when the reader will meet it on a file or a search.

Examples of the *pattern*, not sentences to reuse:

- تیغه بینی (سپتوم)
- انحراف تیغه
- رینوپلاستی / جراحی بینی — pick from clinic terminology (§16.E), do not pair
  them in every sentence
- قوز پشت بینی
- سینوزیت / رینوسینوزیت when the distinction matters

Do not teach anatomy the reader did not ask for. Do not stack three synonyms
in one sentence. On service pages, one clear name plus one gloss is enough.

**Tentative:** on this clinic’s site, lead with «جراحی بینی» or the Persian
functional name unless the query is the Latin term (سپتوپلاستی، رینوپلاستی).
Clinic still needs to fill §16.E.

Do not use academic measurement language (پروجکشن تیپ، زاویه نازوفرونتال،
کلوملو لوبولار) on patient pages unless a specific educational piece needs it,
and then gloss it immediately.

---

## 10. Page intent

### Service page

Answer: is this relevant, how it works here, who may be suitable, what happens
before/after, limits and risks, what this clinic actually provides, how to book
an in-person visit. Not an encyclopedia. Not a global epidemiology essay.

### Medical article

Open with the answer or the practical distinction. Do not spend the first
screen defining the searched term. Structure should follow the reader’s
confusion, not definition → causes → symptoms → treatment → conclusion.
That skeleton is the default of translated magazines; use it only when the
topic genuinely is a disease overview.

A workable default (do not apply mechanically):

1. direct opening that answers the query;
2. who this information is for;
3. practical explanation;
4. clinically important distinctions;
5. what patients commonly misunderstand;
6. what happens in assessment here;
7. warning signs or limits;
8. practical next step.

### FAQ

Answer in the first sentence. Then the nuance. No preamble.

### Booking / visit copy

Operational Persian. The public flow is **in-person**. Payment may be online.

Use: «نوبت حضوری»، «ویزیت حضوری»، «هزینه ویزیت حضوری»، «پرداخت اینترنتی».
Do not write «ویزیت آنلاین» unless a real remote consult exists.

Fee currently configured: **۶۰۰٬۰۰۰ تومان** (admins may change it).

Do not expose OTP, API, Sheet, UUID, CRM.

### Meta description

A useful search snippet in one or two natural sentences. Not a keyword list.
Not «همه چیز درباره…».

### Staff-facing

Reception language: «ارسال لینک پرداخت»، «پرداخت نقدی»، «رایگان / عدم دریافت وجه»،
«ثبت‌کننده»، «زمان آزاد»، «نوبت قطعی».

---

## 11. Competitor-inspired, not competitor-copied

When a URL or paste is supplied, study:

- how much they say above the fold;
- whether headings sound like patient questions;
- how they gloss terms;
- how they handle risk and “it depends”;
- what they refuse to promise.

Do **not** copy sentences, unique claims, patient stories, branded wording,
statistics, or section order.

This round’s working rule: imitate **editorial conventions** of good Persian
medical sites (clear headings, safety thresholds, term-then-gloss). Do not
imitate Nabz’s Mayo skeleton, SID blog’s sales voice, or paper abstracts.

If a competitor is fluent but translated, steal nothing from the fluency of
the translation. Rewrite from the medical point.

---

## 12. SEO without sounding like SEO

Place the primary keyword naturally in title/H1 when it is how patients search,
once in the opening context, in a heading only if that heading is still a
human question, and in the meta description.

Do not target density. Do not bold every keyword. Internal links follow
patient intent; anchor text must read as Persian, not as «کلیک کنید: جراحی بینی».

---

## 13. Dr Bastaninejad — clinic facts

Public booking = in-person clinic appointment.

Flow, described simply:

1. patient information;
2. mobile verification;
3. available Jalali date/time;
4. online payment;
5. confirmed clinic appointment.

Current visit fee: **۶۰۰٬۰۰۰ تومان**.

Doctor-specific clinical claims: only those listed in §16.F. Until that list
is filled, do not invent fellowships, case volumes, “years of experience”
numbers, or signature techniques.

---

## 14. Rewrite workflow

### Pass 0 — Editorial stance
Complete §0. If register is wrong, stop and restart.

### Pass 1 — Meaning
What is the text actually trying to help the reader do?

### Pass 2 — Strip fingerprints
Generic frames, magazine titles, obligatory جمع‌بندی, empty adjectives
(«حرفه‌ای»، «پیشرفته»، «مدرن»، «منحصربه‌فرد»), duplicated ideas.

### Pass 3 — Iranian Persian
Read aloud. Cut calques. Shorten. Swap «می‌باشد» out of patient copy.

### Pass 4 — Medical precision
Every claim classified. Geography and guidelines localised or removed.

### Pass 5 — Usefulness
Add only details that change a decision, a booking step, or a safety action.

### Pass 6 — Search intent
Does the page own the query it ranks for, in the first screen?

### Pass 7 — SEO
Title, H1, meta, internal links — quiet.

### Pass 8 — Human edit
If it could be any clinic in any country, rewrite. If it sounds like a
template, rewrite.

---

## 15. Output format for content tasks

### Revised copy
Publishable Persian only. No editor comments inside the copy.

### SEO fields
- SEO title
- Meta description
- Suggested H1
- Suggested internal links and natural anchors

### Medical review notes
Only claims that need verification or clinic confirmation. Keep this list
short and separate.

### Pattern notes (internal, when refining this skill)
If a new stylistic choice was made from a single example, tag it *tentative*.

---

## 16. User-editable clinic memory

Complete these before calling the skill final. Empty items are unknown — do
not guess.

### A. Preferred clinic phrases

- «نوبت حضوری» / «ویزیت حضوری»
- «پرداخت اینترنتی»
-

### B. Phrases the clinic dislikes

- «ویزیت آنلاین» (unless a remote service is launched)
- «تضمین نتیجه»، «بدون عارضه»، «بهترین جراح»
-

### C. Tone examples approved by the clinic

Paste 3–10 passages the clinic considers natural. None received yet.

### D. Competitor / corpus references (style only — never copy)

- Nabz Group magazine, tag عمومی: https://nabzgroup.com/mag/tag/general
  — consumer encyclopedia; mostly translated; partial model for safety
  headings; negative model for openings/titles/skeleton.
- Noormags keyword علوم پزشکی: https://www.noormags.ir/view/fa/keyword/علوم_پزشکی
  — academic register; terminology + hedging; not patient syntax.
- SID papers vs SID blog — papers = terms/hedging; blog = anti-pattern sales.

Add clinic-chosen Iranian ENT sites here when supplied.

### E. Terminology preferences (unfilled = tentative)

- revision rhinoplasty: جراحی ترمیمی بینی (?)
- primary rhinoplasty: جراحی بینی / رینوپلاستی اولیه (?)
- appointment: نوبت حضوری / ویزیت حضوری
- clinic/office: کلینیک (?)
- post-op care: مراقبت بعد از عمل (?)
- گوشتی / استخوانی dichotomy: unused until clinic says whether they accept it

### F. Doctor-specific facts approved for use

- In-person visit fee currently ۶۰۰٬۰۰۰ تومان
-

---

## 17. Worked contrasts

### Opening — AI / magazine

«جراحی بینی یکی از محبوب‌ترین عمل‌های زیبایی در جهان است که امروزه افراد زیادی
برای بهبود ظاهر و افزایش اعتمادبه‌نفس خود از آن استفاده می‌کنند. در این مقاله
قصد داریم صفر تا صد جراحی بینی را بررسی کنیم.»

### Opening — target

«اگر برای جراحی بینی تحقیق می‌کنید، مهم‌ترین سؤال فقط شکل نهایی بینی نیست.
وضعیت تنفس، ضخامت پوست، استحکام غضروف‌ها و تناسب بینی با بقیه صورت روی انتخاب
روش جراحی و نتیجه‌ای که می‌توان انتظار داشت اثر دارند.»

### Booking — wrong for this clinic

«ویزیت آنلاین خود را با پرداخت ۶۰۰ هزار تومان رزرو کنید.»

### Booking — right

«برای قطعی شدن نوبت حضوری، ابتدا یکی از زمان‌های آزاد را انتخاب کنید و هزینه
ویزیت را به‌صورت اینترنتی بپردازید.»

### Safety threshold — keep the job, not the foreign cut-offs

Keep a short, local, non-alarmist “when to seek care” block where the page
needs it. Do not paste American Academy thresholds or 101 °F. Encyclopedia
skeletons (definition → types → symptoms → causes → treatment → خلاصه) belong
to magazines, not this clinic’s house style — details in the pattern bank.

---

## 18. Final self-test

Answer YES to all before publishing. If any is NO, revise.

- Does this sound like an Iranian human wrote it, not a translation?
- Does it answer the real question in the first screen?
- Is every medical claim supportable, classified, and geography-honest?
- Is the tone calm rather than promotional or alarmist?
- Are generic AI and magazine-SEO phrases gone?
- Does wording match this clinic’s actual workflow?
- Is the page distinct from Nabz/Mayo and from beauty-SEO blogs?
- Are headings things a patient would ask?
- Is SEO present but quiet?
- Would a receptionist and a patient both understand it?

---

## 19. What would still change this skill

Do not mark `status: final` until:

- the clinic has pasted liked and disliked writing (§16.C / B);
- at least two real pages (service + article or FAQ) have been drafted with
  this skill and compared against human Persian the clinic prefers;
- terminology in §16.E is filled;
- a negative test has been run: a Mayo-style input should not come out as a
  Mayo-style output with nicer adjectives.
