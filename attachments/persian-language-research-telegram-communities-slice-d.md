# Research Slice

- **Assigned slice:** D — Telegram/public communities (research, university, methodology, statistics, thesis, academic-writing channels and public discussions)
- **Date:** 15 September 2026
- **Agent/model:** Vibe agent (GLM served on Mistral AI infrastructure)
- **Scope boundaries:**
  - Public Telegram channels and public comment threads only. The global message search also surfaced private dialogs belonging to the account owner; all private messages were excluded from the corpus and from every finding.
  - Individual commenters are cited by channel and thread, not by personal username, to minimise exposure of private individuals.
  - This slice covers Telegram community language only. It does not cover peer-reviewed academic prose (Slice A), editorial publications (Slice E), or forums (Slice C), except where Telegram posts quote or imitate those registers.
  - Language evidence (`LANGUAGE_FINDING`) is kept separate from factual claims (`FACT_FINDING`). No claim found in a service channel (e.g., "free article extraction with every thesis") was treated as fact.
  - Orthography rule for Teznevise (U+200C forbidden) is recorded as a site constraint supplied by the master system; it is not inferred as a general Persian-web rule.

---

# Executive Summary

1. **Telegram thesis Persian is a five-register system, not one style.** The corpus cleanly separates into (a) formal explanatory prose, (b) colloquial educational/sales prose with written-colloquial verbs, (c) bureaucratic notice prose, (d) student conversational prose, and (e) service-provider sales prose. A thesis website needs (a) as its base register, borrowing warmth patterns from (b) and vocabulary from (d), while avoiding (c) and the excesses of (e).
2. **Written-colloquial Persian (`می‌تونه`, `پیام بدید`, `رو`) is fully native on educational Telegram channels** and signals approachability, but the same channels keep formal items (`است`, `را`, `می‌شود`) when they want credibility. The skill should prescribe a deliberate mixed register, not pure formal or pure colloquial.
3. **The passive `انجام می‌شود` is the natural default for describing services** — unlike English, Persian service copy does not sound weak in the impersonal passive. What makes copy sound bad is bureaucratic verbs (`می‌گردد`, `ابلاغ`, `جهت`, `می‌بایست`, `حاصل فرمایید`), not the passive itself.
4. **Student readers describe situations and deadlines, not services or terminology** ("defense is done, reviewers only gave writing objections", "a few questions that must be answered by Saturday"). Effective copy reframes these situations into precise expert terminology without mocking the informal phrasing.
5. **A recognisable AI/tool-description cliché cluster exists in the wild** (`قدرتمند، جامع، یکپارچه، تعاملی، هوشمند` + "در یک پلتفرم ... گردهم آورده است"), and identical boilerplate circulates between channels via reposts. The master skill must ban this cluster and must not learn "naturalness" from reposted marketing copy.
6. **Orthography is genuinely unsettled in the corpus**: `پایان نامه` / `پایان‌نامه` / `پایاننامه` all appear, sometimes within one organisation. The Teznevise ZWNJ ban therefore has real precedent (space-separated forms are attested), but the skill must apply one consistent policy rather than mimic the wild variance.
7. **Pre-2017 "textbook" orthography and verbs (Arabic `ي`/`ك`, `مي گردد`, `به كار گرفته مي‌شود`, `چنانچه`) now read dated**, and are confined to old archive posts and official notices. Modern explanatory prose has moved to shorter, active constructions.

---

# Methodology

- **Discovery:** Public chat search with Persian seed terms (`پایان نامه`, `پروپوزال`, `مقاله نویسی`, `آموزش SPSS`, `دانشجو`, `آمار پژوهش`) identified public channels and groups; relevant channels were then read directly (25–30 recent messages each).
- **Corpus assembly:** 16 public channels plus 4 public comment threads, spanning educational, statistical-practitioner, service-provider, student-community, student-request, and official-news registers. Where a single channel mixes genres, individual message clusters were treated as separate source items. The corpus holds roughly 400 messages; 35 were catalogued as source items.
- **Supplementary fact search:** One Talarion facts query on the Iranian academic Telegram ecosystem returned only tangential results (Iran internet-restriction developments in 2026). This was recorded as environmental context, not language evidence.
- **Exclusions:** All private dialogs surfaced by search were discarded. `@maghalehub`, discovered via search, proved to be an off-topic personal channel and was excluded from findings.
- **Evidence discipline:** No passage longer than ~15 words is quoted, and only for linguistic evidence. All constructed examples in this report are newly written; none are copied from sources. No single author's style was imitated.
- **Limitations:**
  - Telegram global message search is biased toward the reading account's own dialogs, which limited discovery of additional public communities; the corpus was reached mainly through chat-name search.
  - Comment threads represent only channels with enabled discussion; quieter student groups were not reachable.
  - Two channels (`@spsslearn2`, `@researchsterategy`) had not posted recently; their evidence is dated 2016 and 2024 respectively, which is itself useful for register history but weakens currency claims.
  - Dates in the register table are the observed post dates, not channel creation dates.

---

# Source Register

| ID | Source | Type | Register | Audience | Date range | Why useful | Credibility | Last updated |
|---|---|---|---|---|---|---|---|---|
| TG-01 | [روش تحقیق و مقاله نویسی](https://t.me/Raveshtahghighh) | Educational channel, 39k | Formal explanatory + reposts | MA/PhD students | Aug–Sep 2026 | Cleanest formal explanatory prose in corpus; definitional and comparative patterns | 4/5 | 2026-09-13 |
| TG-02 | [آموزش مقاله و پایان‌نامه‌نویسی](https://t.me/dr_amaniiii) | Educational/sales channel, 62k | Colloquial educational | Students, early-career | Jan 2025–May 2026 | Best example of written-colloquial educational register and question-hook pattern | 5/5 | 2026-05-24 |
| TG-03 | [پژوهشگر شو](https://t.me/pajooheshgarsho) | Coaching channel, 9k | Sales/coaching | Thesis students | Jul–Aug 2026 | Sales-register verbs, pricing talk, testimonial framing | 4/5 | 2026-08-24 |
| TG-04 | [آمارکده](https://t.me/Amar_kadeh) | Statistics channel, 16k | Mixed stats-education/news | Stats students | Sep 2026 | Practitioner explaining stats/math concepts; mixed-register drift | 4/5 | 2026-09-15 |
| TG-05 | [Psy_Data](https://t.me/Psy_Data) | Stats/psychology channel, 4.5k | Konkur sales | Psychology candidates | 2024 | Contrast case: konkur marketing register | 3/5 | 2024-04-28 |
| TG-06 | [آمار و روش پژوهش (دکتر خانزاده)](https://t.me/researchsterategy) | Academic personal channel, 159 | Academic essay | Researchers | Dec 2024 | Long-form academic argument style; editor-of-journal voice | 3/5 | 2024-12-17 |
| TG-07 | [آموزش SPSS](https://t.me/spsslearn2) | Stats tutorial archive, 2.2k | Textbook formal | Stats learners | 2016 | Dated textbook register; Q&A format; old orthography | 3/5 | 2016-07-28 |
| TG-08 | [درخواست دانشجویی رایگان \| اِسکورایز](https://t.me/scorize_request) | Student-request channel, 3.7k | Student conversational | Students | 2021–2024 | Pure student language: how students phrase needs before knowing terminology | 5/5 | 2024-06-24 |
| TG-09 | [پایان نامه مقاله پروپوزال (خوارزمی)](https://t.me/KH15b) | Service channel, 46k | Sales/bureaucratic hybrid | Thesis buyers | Nov 2025 | Archetypal thesis-mill sales copy; emoji-structure; trust claims | 4/5 | 2025-11-27 |
| TG-10 | [انجام پایان نامه رساله پایاننامه](https://t.me/vu9fr) | Service channel, 8.5k | Sales | Thesis buyers | Dec 2025 | "مزایا" bullet sales format; note title uses space-separated `پایاننامه` | 4/5 | 2025-12-14 |
| TG-11 | [پروپوزال _ پایان نامه _ مقاله](https://t.me/Proposal) | Educational + service channel, 24k | Educational/sales | Students | Sep 2026 | Reference-formatting explainers; divider-line formatting genre | 4/5 | 2026-09-14 |
| TG-12 | [منابع پروپوزال،مقاله،پایان نامه](https://t.me/PAPhd) | Resource archive, 64k | Newsy/resource | Students | Jun–Aug 2026 | Casual news register with `@paphd` footer template | 3/5 | 2026-08-22 |
| TG-13 | [آموزش نوین مقاله نویسی با هوش مصنوعی](https://t.me/tephd) | Educational channel, 77k | Conversational educational | Researchers | Sep 2026 | Modern conversational-explanatory register; uncertainty expression; engagement questions | 5/5 | 2026-09-15 |
| TG-14 | [مقاله نویسی](https://t.me/maghalehnevisi) | Tips channel, 10k | Explanatory | Researchers | Jul–Aug 2026 | AI-tool description genre; conference CTA genre | 3/5 | 2026-08-05 |
| TG-15 | [یِ دانشجو](https://t.me/ye_daneshjue) | Student community, 303k | Colloquial humor | Students | Sep 2026 | Fully colloquial baseline for comparison | 4/5 | 2026-09-15 |
| TG-16 | [اخبار دانشجویان دانشگاه آزاد](https://t.me/Azadtnb1) | News channel, 167k | Bureaucratic notice | Azad students | Sep 2026 | Official-notice register: `می‌بایست`, `می‌گردد`, `لازم به ذکر است` | 4/5 | 2026-09-15 |
| TG-17 | @tephd public comment thread (post 32834) | Comments | Researcher conversational | Researchers | Sep 2026 | Rejection discourse: `ریجکت`, `دسک ریجکت`, `گیر دادن` | 4/5 | 2026-09-15 |
| TG-18 | @tephd public comment thread (post 32836) | Comments | Polite student-to-expert | Students | Sep 2026 | Politeness bundles; code-switching (English rejection letter inside Persian question) | 4/5 | 2026-09-15 |
| TG-19 | @tephd public comment thread (post 32831) | Comments | Expert/mixed | Researchers | Sep 2026 | Lay explanation of technical topic; `بعید می‌دونم` hedging | 4/5 | 2026-09-11 |
| TG-20 | TG-01 message cluster: thesis-vs-dissertation explainer | Post | Formal explanatory | Students | Aug 2026 | `رساله`/`پایان‌نامه` distinction; `واژۀ` old-style ezafe spelling | 4/5 | 2026-08-31 |
| TG-21 | TG-01 message cluster: scientific-terms glossary | Post | Explanatory glossary | Students | Aug 2026 | Glossary item pattern: English term + `🔍` + short Persian gloss | 3/5 | 2026-08-31 |
| TG-22 | TG-01 message cluster: tool/AI descriptions | Posts | Formal explanatory (reposted) | Researchers | Aug–Sep 2026 | Reposted boilerplate detection; AI-cliché cluster | 3/5 | 2026-09-13 |
| TG-23 | TG-01 message cluster: news items | Posts | News lede | Students | Aug–Sep 2026 | News-report syntax: agent + verb + elaboration | 3/5 | 2026-09-07 |
| TG-24 | TG-02 message cluster: `#سوال` hooks + course ads | Posts | Colloquial educational/sales | Students | 2025–2026 | Question-hook pattern; urgency language | 4/5 | 2026-05-24 |
| TG-25 | TG-02 message cluster: `#نمونه_تدریس` how-tos | Posts | Colloquial how-to | Students | 2025 | How-to phrasing: `چطور ... کنیم!؟` | 4/5 | 2025-03-10 |
| TG-26 | TG-07 message cluster: `#پاسخ_به_سوالات` Q&A | Posts | Q&A formal + student question | Stats learners | 2016 | Real student stats question embedded; dated formal answer | 4/5 | 2016-07-23 |
| TG-27 | TG-09/TG-10 message cluster: service menus | Posts | Sales | Thesis buyers | 2025 | Service-menu bullet grammar; trust/payment claims | 4/5 | 2025-12-14 |
| TG-28 | TG-08 message cluster: thesis/analysis requests | Posts | Student conversational | Students | 2021–2024 | How students outsource work; `توافقی`, `فوری` | 5/5 | 2024-06-24 |
| TG-29 | TG-16 message cluster: directives/notifications | Posts | Bureaucratic | Students | Sep 2026 | Officialese markers to avoid | 4/5 | 2026-09-15 |
| TG-30 | TG-04 message cluster: brand announcement | Post | Corporate-relations | Followers | Sep 2026 | Persian corporate-cliché register ("یک مسیر رو به رشد") | 3/5 | 2026-09-15 |
| TG-31 | TG-13 message cluster: AI/math news + caveats | Posts | Conversational explanatory | Researchers | Sep 2026 | Best-in-corpus uncertainty/qualification phrasing | 5/5 | 2026-09-09 |
| TG-32 | TG-11 message cluster: reference-format explainers | Posts | Instructional list | Students | Sep 2026 | Step/sequence instructional phrasing | 4/5 | 2026-09-12 |
| TG-33 | TG-15 message cluster: student humor posts | Posts | Colloquial | Students | Sep 2026 | Baseline colloquial orthography and rhythm | 4/5 | 2026-09-15 |
| TG-34 | TG-14 message cluster: AI-tool + conference CTA | Posts | Marketing explanatory | Researchers | Jul–Aug 2026 | AI-tool cliché genre; conference call-for-papers register | 3/5 | 2026-08-05 |
| TG-35 | TG-06 message cluster: editor's essay | Post | Academic argumentative | Researchers | Dec 2024 | Rhetorical-question chains; long-clause academic prose | 3/5 | 2024-12-17 |

Credibility above scores usefulness as **language evidence**, not trustworthiness of claims. Service channels (TG-09, TG-10) are excellent evidence for the sales register while being unreliable for facts.

---

# High-Confidence Language Findings

Finding IDs are referenced by the constructed examples and the YAML block. "Evidence" cites source IDs; quotes are minimal and used only as linguistic evidence.

## Syntax

**LF-S1 — Definitional copula is `است`, never `می‌باشد` or `هست`.**
Modern explanatory prose defines things as `X یک ... است که ...` (TG-01, TG-13). `می‌باشد` appears only in bureaucratic notices (TG-16) and dated textbooks (TG-07).
*Register:* explanatory, service. *Exceptions:* some universities' thesis templates still prescribe `می‌باشد`; that is a template convention, not natural usage. *Confidence:* high.

**LF-S2 — `می‌گردد`, `خواهد گردید`, `صورت پذیرد` are officialese markers.**
Confined to official notices and pre-2017 textbook prose (TG-16, TG-07). Their presence in a service page immediately reads governmental.
*Confidence:* high.

**LF-S3 — The impersonal passive `انجام می‌شود` is the natural service frame.**
"تحلیل آماری ... با بالاترین کیفیت انجام میشه" (TG-03); "در صورت سفارش ... فایل ارائه ... انجام خواهد شد" (TG-09). Persian does not share English's aversion to this passive. Colloquial channels write `انجام میشه` (TG-03).
*Register:* service, explanatory. *Exceptions:* none observed. *Confidence:* high.

**LF-S4 — `جهت` signals bureaucratic register; `برای` is the neutral choice.**
`جهت سفارش یا مشاوره رایگان به اکانت زیر پیام بدهید` (TG-09) — note the hybrid: bureaucratic `جهت` with colloquial `پیام بدهید`. Educational channels consistently use `برای`.
*Confidence:* high.

**LF-S5 — Object marker split: `را` formal, `رو` colloquial, mixed use is deliberate.**
Channels keep `را` when building credibility and switch to `رو` when being friendly (TG-02 uses `رو` in hooks; TG-13 keeps `رو` throughout its conversational posts; TG-01 keeps `را`).
*Confidence:* high.

**LF-S6 — Long ezafe chains are tolerated up to ~3–4 links in service prose.**
`امکان تسویه بعد از تایید استاد راهنما` (TG-09) is acceptable; longer chains appear only in officialese (TG-16).
*Confidence:* medium.

**LF-S7 — Question-word split: `چگونه` (written), `چطور` (conversational hook), `چجوری` (speech-like only).**
Educational hooks use `چطور ... کنیم!؟` (TG-02); formal explainers use `چگونه` (TG-01); `چجوری` appears only in comments and student posts (TG-17, TG-33).
*Confidence:* high.

**LF-S8 — Pre-2017 textbook syntax reads dated: `چنانچه`, `به كار گرفته مي‌شود`, `مورد مطالعه قرار مي‌گيرد`, Arabic `ي`/`ك`.**
TG-07 (2016) uses all of these; no 2024–2026 educational channel does.
*Confidence:* high (for the perception; the corpus dates are the evidence).

**LF-S9 — `است` vs `هست`: `هست` marks emphasis or colloquial speech, not neutral description.**
Explanatory definitions use `است`; `هست` appears in comments for emphasis (`سطحم B2 هستش`, TG-28) or in news-register claims (`کاملاً جعلی هست`, TG-17).
*Confidence:* medium-high.

**LF-S10 — Conditional split: `اگر` neutral, `چنانچه`/`در صورتی که` formal-to-officialese.**
`اگر` dominates conversational and educational registers; `چنانچه` only in old textbook prose (TG-07).
*Confidence:* high.

## Lexicon

**LF-L1 — Verb field for "doing" a thesis is register-stratified.**
`انجام دادن` (service/colloquial: `انجام پایان نامه`, TG-09), `نگارش` (formal written: `نگارش پروپوزال`, TG-11), `نوشتن` (neutral), `تدوین` (academic-administrative), `آماده کردن/آماده‌سازی` (conversational/process, TG-09). A service page can use all five, but each belongs to a slot: `نگارش` in headings, `انجام` in offers, `آماده می‌شود` in process descriptions.
*Confidence:* high.

**LF-L2 — Stable Perso-Arabic borrowings: `پروپوزال`, `پاورپوینت`, `پارتنر`, `ریجکت`, `اکسپت`, `سابمیت`, `فول‌تکست`, `سرچ`.**
`پروپوزال` is universal — no Persian equivalent is ever used (TG-01, TG-02, TG-09, TG-11). Publication verbs (`ریجکت`, `دسک ریجکت`, `اکسپت`) are researcher-jargon, used in comment threads (TG-17) but glossed for students in channels (`دریافت اکسپت`, TG-14).
*Confidence:* high.

**LF-L3 — Latin script retained for: ISI, SPSS, R, SmartPLS, AMOS, ANOVA, EFA, CFA, SEM, P-value, Impact Factor, Turnitin.**
Persian transliteration (`اس پی اس اس`) exists (TG-07 channel name, TG-01) but the Latin form dominates in 2024–2026 posts. Software names are never translated.
*Confidence:* high.

**LF-L4 — `رساله` = PhD dissertation; `پایان‌نامه` default for MA (and loosely for PhD).**
TG-20 explains the distinction explicitly and adds the English terms as glosses; TG-09 uses `پایان نامه و رساله دکتری` as a pair.
*Confidence:* high.

**LF-L5 — `دانش‌آموخته` is official-notice vocabulary; `فارغ‌التحصیل` is neutral.**
TG-16 uses `دانش‌آموختگی` in system names; service channels use `دانش آموخته عزیز` only in testimonial framing (TG-09) — where it carries a slightly ceremonial tone.
*Confidence:* high.

**LF-L6 — Bureaucratic lexicon to avoid in reader-facing copy: `ابلاغ`, `می‌بایست`, `مورد تقاضا`, `در راستای`, `لغایت`, `مندرجات`, `بدواً`.**
All attested in TG-16 (official notices). Their correct home is quoting regulations, not service prose.
*Confidence:* high.

**LF-L7 — Fixed collocations (do not paraphrase):**
`تحلیل آماری`, `تحلیل داده‌ها`, `گردآوری داده‌ها/اطلاعات`, `تجزیه و تحلیل`, `جامعه آماری`, `حجم نمونه`, `نمونه‌گیری`, `روایی و پایایی`, `بیان مسئله`, `اهمیت و ضرورت تحقیق`, `پیشینه تحقیق`, `مبانی نظری`, `چکیده مقاله`, `جلسه دفاع`, `استاد راهنما/مشاور`, `همانندجویی`, `سرقت علمی/ادبی`, `استخراج مقاله`, `دوره تکمیلی`. Attested across TG-01, TG-02, TG-07, TG-11, TG-13.
*Confidence:* high.

**LF-L8 — `همانندجویی` is the IranDoc-era official term for similarity checking; `سرقت ادبی/علمی` for plagiarism.**
TG-01 offers both `همانندجویی` and `سرقت علمی` in the same post; students say neither — they say `درصدش پایین بیاد` (inferred from topic framing; see Open Questions).
*Confidence:* medium-high.

**LF-L9 — Student verbs for research actions: `پخش کردن` (distribute questionnaires), `گیر دادن` (reviewer objects), `تموم کردن`, `جلو بردن`, `پایین آوردن`.**
`گیر داده بودن که ... با هوش نوشتی` (TG-17); request posts use `پیش بریم`, `با هم پیش ببریم` (TG-28).
*Confidence:* high.

**LF-L10 — `توافقی` is the standard student/market word for "price negotiable"; `فوری` marks urgency.**
Both recur in TG-28 request templates.
*Confidence:* high.

## Discourse

**LF-D1 — Question-hook pattern: `#سوال:` + short question + `!؟` + thinking emoji, then answer.**
`#سوال: چطور فول تکست پایان‌نامه‌های انگلیسی رو رایگان دانلود کنیم!؟` (TG-02, TG-24). The `#سوال` hashtag itself is a genre marker.
*Register:* educational, blog-convertible. *Confidence:* high.

**LF-D2 — Definitional opening: bare term, then `یک ... است که` + benefit clause.**
`Turnitin یک سامانه‌ی پیشرفته برای تشخیص سرقت علمی است که ...` (TG-01). No "In today's world" preamble.
*Confidence:* high.

**LF-D3 — News lede: agent + past verb + object, then elaboration sentence.**
`وزارت علوم مهلت دفاع ... را تا ۳۰ مهر تمدید کرد و ثبت‌نام دکتری را ... بلامانع اعلام کرد` (TG-23). Useful for "news" sections of a thesis site.
*Confidence:* high.

**LF-D4 — Qualification markers: `معمولاً`, `اغلب`, `ممکن است`, `بسته به ... دارد`, `در برخی دانشگاه‌ها`.**
`معمولاً واژۀ پایان‌نامه ... برای کارشناسی‌ارشد بیان می‌شود` (TG-20). Persian explanatory prose hedges with these adverbs rather than modal constructions.
*Confidence:* high.

**LF-D5 — Uncertainty is expressed with `باید ... بررسی و تأیید شود` and `بعید می‌دونم`.**
`این نتیجه هنوز باید توسط ریاضیدانان مستقل بررسی و تأیید شود` (TG-31) — an exemplary scientific-hedging sentence. `بعید می‌دونم` for personal doubt (TG-19).
*Confidence:* high.

**LF-D6 — CTA split: `برای X به آیدی/شماره زیر پیام بدید` natural; `جهت X تماس حاصل فرمایید` officialese.**
Natural CTAs in TG-02, TG-03 (`برای ثبت‌نام ... پیام بدید`); bureaucratic CTA in TG-09 (`جهت سفارش یا مشاوره رایگان به اکانت زیر پیام بدهید` — hybrid).
*Confidence:* high.

**LF-D7 — Emoji function as structural bullets (`✅`, `🔸`, `❗`, `🔻`), not decoration.**
Service menus use `✅` per feature line (TG-09, TG-27). On a website this should be converted to real bullets; the emoji themselves are genre markers of Telegram, not of trustworthy prose.
*Confidence:* high.

**LF-D8 — Hashtags double as in-text topic labels: `#پایان‌نامه #روش_تحقیق`.**
Universal in TG-12, TG-02. Website copy should not imitate; useful only for social redistribution.
*Confidence:* high.

**LF-D9 — Repost culture produces identical "natural-looking" boilerplate.**
The same ScienceOS tool description appears verbatim in TG-01 and TG-04. Corpus evidence must therefore be de-duplicated before being treated as independent naturalness evidence.
*Confidence:* high (direct observation).

**LF-D10 — `لازم به ذکر است` and `توجه:` mark official-notice and textbook register respectively.**
TG-16, TG-07. On a service page, `نکته:` is the neutral equivalent.
*Confidence:* high.

**LF-D11 — Trust-building in the sales register leans on payment-terms and post-delivery support claims.**
`امکان تسویه بعد از تایید استاد راهنما`, `پشتیبانی ... حتی بعد از دفاع` (TG-09, TG-27). This is the local trust vocabulary; a compliant consultancy site can express the same substance with `مشاوره` framing (see Recommendations).
*Confidence:* high.

## Rhythm

**LF-R1 — Telegram paragraphs are 1–3 lines separated by blank lines.**
Across TG-01, TG-02, TG-13. Website prose can afford 3–5 lines but should keep the blank-line breathing.
*Confidence:* high.

**LF-R2 — Structured explanations use emoji- or number-bulleted lists; definitions and arguments stay in prose.**
TG-11 uses numbered reference-format steps; TG-24 uses `✅` feature lists.
*Confidence:* high.

**LF-R3 — Good explanatory prose alternates one-clause and multi-clause sentences; officialese is uniformly long.**
TG-31 mixes a 4-word reaction (`البته یک نکته مهم`) with long informational sentences. TG-16 sentences run uniformly 15+ words.
*Confidence:* medium-high.

**LF-R4 — Headings are either short noun phrases (`نحوه ...`, `مزایای ...`, `تفاوت ... و ...`) or `X چیست؟` questions.**
TG-01, TG-11. Compound-noun headings (`آموزش قدم‌به‌قدم ...`) are common in course contexts.
*Confidence:* high.

## Reader Language

**LF-G1 — Students describe situations, not services or terms.**
`پایان نامه تموم شده و دفاع هم شده فقط داوران ایراد نگارشی دادند` (TG-28). No student in the corpus names a service ("ویرایش نگارشی"); they narrate the state of their work.
*Confidence:* high.

**LF-G2 — Deadline-first framing: `فوری`, `تا شنبه`, `تا آخر امسال`.**
TG-28 request posts lead with or prominently feature deadlines.
*Confidence:* high.

**LF-G3 — `استاد راهنمام` / `پروپوزالم` possessive + colloquial verb is the default self-description frame.**
TG-18, TG-28. Copy addressing students should mirror the possessive frame (`پروپوزال شما`) rather than institutional frames (`متقاضی محترم`).
*Confidence:* high.

**LF-G4 — Politeness bundle in student-to-expert questions: greeting + well-wish + gratitude + `میشه ... بفرمایید`.**
`سلام! وقت بخیر! متشکر از پست‌های آموزشی ... میشه ... بنده رو راهنمایی بفرمایید` (TG-18). Note the self-reference `بنده` and honorific `بفرمایید` even in otherwise informal contexts.
*Confidence:* high.

**LF-G5 — Code-switching is normal: English source texts pasted inside Persian questions.**
TG-18 pastes a full English rejection email inside a Persian request. Expert answers then translate the concept, not the text.
*Confidence:* high (single but unambiguous thread; see TG-17 for lighter mixing).

**LF-G6 — Student spelling is error-prone (`اماده`, `چنتا`, `جواباش`, `نيار` for `نیاز`).**
TG-28, TG-17. Authentic for transcribed testimonials; never for site prose. Do not "correct" quotes inside testimonials without marking them.
*Confidence:* high.

**LF-G7 — Novices lack terminology and use generic verbs: `چکار کرده`, `نمیدونم چجوری`, `میشه راهنماییم کنی`.**
TG-26 student question, TG-28. Expert reframe pattern observed: restate the need with the precise term, then answer (`برای هر سوال می‌توانید از آمار توصیفی ... استفاده نمایید`, TG-26).
*Confidence:* high.

**LF-G8 — `پارتنر` (study partner) is established student vocabulary, not an error.**
TG-28 requests: `پارتنر زبان`, `پارتنر تحصیلی`. Useful in blog copy about peer study, jarring in formal service prose.
*Confidence:* high.

## Anti-Patterns (AI / translationese / salesy)

**LF-A1 — AI tool-description cliché cluster: `قدرتمند`, `جامع`, `یکپارچه`, `تعاملی`, `هوشمند`, `کاربردی` + `در یک پلتفرم ... گردهم آورده است`.**
Attested in TG-22 (reposted), TG-34. This phrasing is immediately recognisable as machine-translated or copy-pasted marketing and should be banned from site copy.
*Confidence:* high.

**LF-A2 — `در دنیای امروز` / `در عصر جدید` openers are translationese.**
`در دنیای امروز، تسلط به زبان انگلیسی می‌تونه ...` (TG-01 advertisement). Native Persian openings start from the object or the reader, not from "the world today".
*Confidence:* high.

**LF-A3 — Stacked `می‌تواند ... کند` modal chains (3+ per paragraph) read AI-generated.**
Observed in TG-22/TG-34 tool descriptions. Natural Persian alternates `می‌تواند` with `اجازه می‌دهد`, `به شما کمک می‌کند`, and direct verbs.
*Confidence:* medium-high.

**LF-A4 — Emoji inflation and `‼️`/`🔥` spam mark low-credibility sales copy.**
TG-09, TG-10. Even genuine educational channels restrain emoji to structural roles (LF-D7).
*Confidence:* high.

**LF-A5 — Scarcity/urgency formulas (`ظرفیت محدود`, `از دست نده`, `فقط ۵ نفر اول`) are endemic but trust-eroding.**
TG-02, TG-03, TG-24. For a consultancy positioning itself as compliant and professional, these should be absent or used once at most.
*Confidence:* high.

**LF-A6 — Synonym rotation (cycling `نویسنده/مولف/پدیدآورنده`, `تحقیق/پژوهش/مطالعه` within one passage) is an AI marker.**
Not directly attested as an error in the corpus (channels are consistent), which itself is evidence: real channel prose fixes a term and repeats it. Inference from consistency across TG-01/02/13.
*Confidence:* medium.

**LF-A7 — Uniform sentence length and uniform paragraph shape read artificial.**
Contrast between TG-31 (varied, alive) and TG-22 (uniform, dead).
*Confidence:* medium-high.

**LF-A8 — Archaic-formal hybrids (`از آنجایی که ... عاجز هستند`, `می‌باشد` + colloquial neighbours) signal translated or unsupervised AI text.**
The hybrid `جهت ... پیام بدهید` (TG-09) shows register clash within one sentence; such clashes are the strongest single "unnatural" signal.
*Confidence:* high.

**LF-A9 — Unnecessary transliteration when a Persian term exists (`دیزرتیشن` for `رساله`).**
TG-20 uses `دیزرتیشن` only as an explicit English gloss in parentheses — the correct treatment. Transliterating it into running prose would be wrong.
*Confidence:* high.

## Orthography

**LF-O1 — ZWNJ usage is inconsistent in the wild: `پایان نامه` / `پایان‌نامه` / `پایاننامه` all occur, even within one organisation's channel titles (TG-09 vs TG-10).**
Consequence for Teznevise: the space-separated form `پایان نامه` is attested and acceptable; the skill must enforce it consistently and must not "correct" it to ZWNJ forms. This rule is site-specific per the master system.
*Confidence:* high (for the variance; the ban itself is a supplied constraint).

**LF-O2 — Arabic characters `ي` and `ك` (instead of `ی` and `ک`) mark pre-2017 typing and read dated or careless.**
TG-07 throughout; TG-08's footer uses `اسكورايز`. Modern copy must use Persian `ی`/`ک`.
*Confidence:* high.

**LF-O3 — `مساله` vs `مسئله` both occur; academic standard is `مسئله`, and the fixed collocation is `بیان مسئله`.**
TG-01 uses `بیان مساله` and `بیان مسئله` in different posts. Pick `مسئله` and stay consistent.
*Confidence:* medium-high.

---

# Register Map

**1. Academic prose (thesis register).** Long sentences, heavy ezafe chains, `می‌شود` passives, `می‌باشد` tolerated by tradition, hedged claims, no direct reader address. Evidence: TG-06, TG-35; quoted thesis conventions in TG-20. A thesis website quotes this register but must not write its pages in it.

**2. Professional explanatory (the recommended base register).** `است` copula, `را` object marker, `می‌شود`/`می‌دهد` verbs, short-to-medium sentences, `برای` not `جهت`, definitions then benefits, qualifications with `معمولاً`/`ممکن است`, restrained structure. Evidence: TG-01 (non-repost posts), TG-13, TG-11. This is the register Teznevise service and knowledge pages should target.

**3. Colloquial educational (Telegram-native).** Written-colloquial verbs (`می‌تونه`, `پیام بدید`, `بذارید`), `رو` object marker, question hooks, emoji, urgency formulas, `تو` address. Evidence: TG-02, TG-24, TG-25. Effective for engagement; on a website, reserve its warmth for FAQ answers and intro paragraphs, not service descriptions.

**4. Student/community.** Situation narration, deadline framing, possessive frames, borrowings (`پارتنر`), spelling errors, code-switching. Evidence: TG-08, TG-28, TG-33, TG-18. Source of empathy vocabulary and search phrasing, never a style to imitate verbatim.

**5. Service/sales.** Feature bullets with `✅`, trust claims around payment terms, `انجام` verb family, testimonial framing (`رضایت دانش‌آموخته عزیز`), hybrid officialese (`جهت`). Evidence: TG-09, TG-10, TG-03. A compliant consultancy reuses its substance (transparent process, support after delivery) with cleaner grammar and `مشاوره` framing.

**6. Bureaucratic notice.** `می‌بایست`, `می‌گردد`, `ابلاغ`, `در راستای`, `لغایت`, numbered clauses. Evidence: TG-16, TG-29. Correct only when quoting regulations (e.g., quoting a ministry directive inside an article, clearly marked as quotation).

---

# Vocabulary and Collocation Map

**Natural verb choices by slot**

| Slot | Natural | Avoid |
|---|---|---|
| Heading "writing a proposal" | `نگارش پروپوزال` | `تولید پروپوزال`, `خلق پروپوزال` |
| Offer line | `انجام تحلیل آماری` | `ارائه خدمات تحلیل` (empty), `تصدی تحلیل` |
| Process description | `آماده می‌شود`, `تحویل داده می‌شود` | `تدوین خواهد گردید` |
| Reader action | `پیام بدهید`, `تماس بگیرید`, `ثبت‌نام کنید` | `اقدام فرمایید`, `تماس حاصل نمایید` |
| Supervisor action (colloquial empathy) | `استادت ایراد گرفت`, `گیر داد` (very colloquial) | `مولف نظر مخالف ابراز نمود` |

**Nouns and terms**
- Fixed: `پایان‌نامه`, `رساله`, `پروپوزال`, `چکیده`, `بیان مسئله`, `پیشینه تحقیق`, `مبانی نظری`, `جامعه آماری`, `حجم نمونه`, `نمونه‌گیری`, `متغیر مستقل/وابسته`, `فرضیه`, `روایی و پایایی`, `آلفای کرونباخ`, `سطح معنی‌داری`, `فرض صفر`, `آزمون تی مستقل/زوجی`, `تحلیل واریانس`, `رگرسیون`, `تحلیل عاملی`, `معادلات ساختاری`, `جلسه دفاع`, `استاد راهنما/مشاور`, `داور`, `همانندجویی`, `سرقت علمی`, `استخراج مقاله`, `مقاله مستخرج`, `نشریه علمی‌پژوهشی`.
- Borrowings to keep in Latin script: `SPSS`, `R`, `SmartPLS`, `AMOS`, `NVivo`, `MAXQDA`, `ISI`, `Scopus`, `Impact Factor`, `P-value`, `EFA`, `CFA`, `SEM`, `APA`, `Turnitin`, `Zotero`, `EndNote`.
- Borrowings naturalised in Perso-Arabic script: `پروپوزال`, `پاورپوینت`, `چک‌لیست`, `تایم‌لاین`, `وبینار`, `منتور`, `پکیج`, `ریزومه/رزومه` (both spellings occur; `رزومه` is now more common).
- Student-only vocabulary (empathy layer, not service prose): `پارتنر`, `فول‌تکست`, `سرچ`, `توافقی`, `فوری`, `پخش پرسشنامه`, `گیر دادن`, `جلو بردن کار`.

**Phrases to avoid**
- `در دنیای امروز`, `در عصر حاضر` (translationese openers).
- `قدرتمند/جامع/یکپارچه/تعاملی` as an adjective stack.
- `جهت`, `می‌بایست`, `می‌گردد`, `ابلاغ`, `حاصل فرمایید`, `مورد تاکید است`.
- `بهترین کیفیت`, `با بالاترین کیفیت` (TG-03 uses it; it is sales filler — prefer specifics: `در SPSS و R`, `گزارش فصل چهارم`).
- `مزایای منحصر به فرد ما` (TG-10; empty promotional Persian).

---

# Syntax and Rhythm Rules

1. Open definitions with the bare term + `یک ... است که` (LF-S1, LF-D2).
2. Keep `است`; never `می‌باشد`, `می‌گردد`, `هست` in running prose (LF-S1, LF-S2, LF-S9).
3. Use the impersonal passive freely for services: `انجام می‌شود`, `تحویل داده می‌شود` (LF-S3).
4. `برای`, never `جهت` (LF-S4).
5. `را` in body text; `رو` only in deliberately conversational segments (LF-S5).
6. Prefer short verb phrases over `مورد ... قرار می‌گیرد` constructions: `استفاده می‌شود` not `مورد استفاده قرار می‌گیرد` (LF-S2, LF-S8).
7. `اگر` for conditions; `چنانچه` never (LF-S10).
8. Vary sentence length deliberately: follow every long informational sentence with a short one (LF-R3).
9. Paragraphs of 2–4 lines; blank line between paragraphs (LF-R1).
10. Use real bullets for lists; reserve emoji for at most one structural role per page (LF-D7, LF-A4).
11. Hedge with `معمولاً`, `ممکن است`, `بسته به رشته شما`; express uncertainty with `باید ... بررسی و تأیید شود` (LF-D4, LF-D5).
12. Fix each technical term and repeat it; do not rotate synonyms (LF-A6).

---

# Heading and Question Patterns

Attested heading forms, in order of frequency in the corpus:

1. `X چیست؟` / `X چیست و چگونه ...؟` — definitional articles (TG-01, TG-11).
2. `تفاوت X و Y چیست؟` / `تفاوت‌های X و Y` — comparison articles (TG-01).
3. `چگونه ... کنیم؟` — how-to articles, written register (TG-01).
4. `چطور ... !؟` — conversational hooks (TG-02).
5. `نحوه ...` — instructional noun-phrase headings (TG-11: `نحوه نوشتن مراجع`).
6. `N نکته/اشتباه/معیار در/برای ...` — listicle headings (TG-09: `هفت نکته کلیدی در انتخاب موضوع`).
7. `X یا Y؛ کدام ...؟` — choice headings (TG-01: `Zotero یا EndNote؟`).
8. `اگر ... چه کنیم؟` — problem-condition headings (TG-01: `اگر نتیجه آماری معنادار نشد چه کنیم؟`).

Rules: headings are questions or short noun phrases, never full sentences; they name the concrete object (`پروپوزال`, `فصل چهارم`) not abstract categories (`راهکارهای بهینه‌سازی فرآیند`); numbers in headings use Persian digits (`۱۰ اشتباه رایج`).

---

# Anti-AI / Translationese Findings

Summary of detectable markers, ranked by reliability:

1. **Register clash inside one sentence** (`جهت ... پیام بدهید`) — most reliable single marker (LF-A8).
2. **Adjective stacks from the `قدرتمند/جامع/یکپارچه/تعاملی/هوشمند` cluster** (LF-A1).
3. **`در دنیای امروز`-style openers** (LF-A2).
4. **Uniform sentence length + uniform paragraphs** (LF-A7).
5. **Modal-chain monotonies (`می‌تواند` three times in a row)** (LF-A3).
6. **`می‌باشد`/`می‌گردد` in modern self-published prose** (LF-S2).
7. **Synonym rotation of fixed terms** (LF-A6).
8. **Emoji punctuation like `‼️` mid-sentence + scarcity formulas** (LF-A4, LF-A5).
9. **Reposted boilerplate** — check phrasing against known circulating templates; identical tool blurbs across channels are not independent naturalness evidence (LF-D9).

---

# Constructed Before/After Examples

All examples below are newly written for this report. ZWNJ is used naturally in `BETTER_PERSIAN`; the Teznevise-specific substitution (site orthography) is governed by the master system and is demonstrated separately in Example 21.

**1. Definitional opening**
- `UNNATURAL_OR_WEAK:` «پایان نامه یک سند آکادمیک جامع می باشد که در جهت نمایش توانمندی های پژوهشی دانشجو تدوین می گردد.»
- `BETTER_PERSIAN:` «پایان نامه مهم ترین سند مقطع تحصیلات تکمیلی است؛ سندی که نشان می دهد دانشجو می تواند مستقل پژوهش کند.»
- `WHY:` Stacks `می باشد`، `در جهت`، `می گردد` (LF-S1, LF-S2, LF-S4). Native definitions use `است` + a benefit clause (LF-D2).

**2. Question heading**
- `UNNATURAL_OR_WEAK:` «آیا می دانید که روایی و پایایی چیستند؟»
- `BETTER_PERSIAN:` «روایی و پایایی چیست و چگونه سنجیده می شود؟»
- `WHY:` `چیستند` is unidiomatic for paired abstract nouns; attested headings use `چیست و چگونه` (LF-R4, LF-S7).

**3. Call to action**
- `UNNATURAL_OR_WEAK:` «جهت دریافت مشاوره تخصصی، لطفا با کارشناسان ما تماس حاصل فرمایید.»
- `BETTER_PERSIAN:` «برای مشاوره رایگان، به ما پیام بدهید یا با شماره زیر تماس بگیرید.»
- `WHY:` `جهت ... حاصل فرمایید` is officialese (LF-S4, LF-D6); corpus CTAs are `برای ... پیام بدهید`.

**4. Service description**
- `UNNATURAL_OR_WEAK:` «تحلیل های آماری شما توسط متخصصان مجرب و باتجربه ما با بالاترین کیفیت انجام خواهد شد.»
- `BETTER_PERSIAN:` «تحلیل آماری پایان نامه شما در SPSS، R یا SmartPLS انجام می شود و گزارش فصل چهارم تحویل داده می شود.»
- `WHY:` Passive is correct (LF-S3), but `مجرب و باتجربه` and `بالاترین کیفیت` are empty fillers; concrete deliverables replace them (LF-A4-adjacent; vocabulary map).

**5. Expressing uncertainty**
- `UNNATURAL_OR_WEAK:` «لازم به ذکر است که نتایج احتمالا قابل تعمیم نخواهند بود.»
- `BETTER_PERSIAN:` «این نتیجه برای جامعه های آماری کوچک با احتیاط تعمیم داده شود؛ بهتر است پیش از هر جمع بندی، تکرار پژوهش بررسی شود.»
- `WHY:` `لازم به ذکر است` is notice-register (LF-D10); corpus hedging uses `با احتیاط`, `بهتر است`, `باید ... بررسی شود` (LF-D4, LF-D5).

**6. Qualification in a methodology explainer**
- `UNNATURAL_OR_WEAK:` «همه پایان نامه ها باید حتما از روش کمی بهره بگیرند.»
- `BETTER_PERSIAN:` «معمولا در رشته های مدیریت و روانشناسی روش کمی رایج تر است، اما بسته به سوال پژوهش، روش کیفی یا آمیخته هم می تواند مناسب باشد.»
- `WHY:` Mirrors attested hedging (`معمولاً`، `بسته به ...`، `می تواند`) instead of absolutes (LF-D4).

**7. Empathy line addressing a student pain point**
- `UNNATURAL_OR_WEAK:` «ما درک می کنیم که فرآیند نگارش پایان نامه برای شما چالش برانگیز بوده است.»
- `BETTER_PERSIAN:` «اگر ماه هاست فایل پایان نامه را باز و بسته می کنید و پیشرفتی نیست، تنها نیستید؛ بیشتر دانشجویان در همین مرحله می مانند.»
- `WHY:` The first is translated empathy («چالش برانگیز») — the second narrates the student's own situation (LF-G1), the pattern real channels use.

**8. Reframing student language into expert language**
- `UNNATURAL_OR_WEAK:` «دفاع کرده اید و الان داورها گیر داده اند؟ ما ایرادهایشان را حل می کنیم.»
- `BETTER_PERSIAN:` «اگر داوران فقط ایراد نگارشی گرفته اند، اصلاح و ویرایش نهایی پایان نامه سریع ترین مسیر تاکارشناسی ارزیابی است: ابتدا فهرست ایرادها دسته بندی می شود، سپس متن ویرایش و پاسخ هر ایراد مستند می شود.»
- `WHY:` Keeps the student's framing in the condition clause, then reframes with precise terms (`ویرایش`, `مستند`) without colloquial `گیر داده اند` in the offer itself (LF-G1, LF-G7; `گیر دادن` is comment-register, LF-L9).

**9. Choosing between borrowing and Persian term**
- `UNNATURAL_OR_WEAK:` «دیزرتیشن شما نیاز به منبع یابی گسترده دارد.»
- `BETTER_PERSIAN:` «برای رساله دکتری، جست وجو در پایگاه های علمی را از همین مرحله پروپوزال شروع کنید.»
- `WHY:` `دیزرتیشن` in running prose is unnecessary transliteration (LF-A9); `رساله` is the term (LF-L4).

**10. Writing for students about questionnaires**
- `UNNATURAL_OR_WEAK:` «توزیع پرسشنامه باید با دقت و ظرف بازه زمانی مشخصی صورت پذیرد.»
- `BETTER_PERSIAN:` «پرسشنامه را همه جا پخش نکنید؛ ابتدا جامعه آماری و حجم نمونه را مشخص کنید تا داده ها قابل تحلیل بماند.»
- `WHY:` `پخش کردن` is what students actually say (LF-L9), and `صورت پذیرد` is officialese (LF-S2); the imperative-second-person form matches educational register.

**11. Avoiding a translationese opener**
- `UNNATURAL_OR_WEAK:` «در دنیای امروز، انتشار مقالات علمی اهمیت بی نظیری دارد.»
- `BETTER_PERSIAN:` «دو نمره درس پایان نامه مقطع ارشد به مقاله مستخرج اختصاص دارد؛ همین یک نمره می تواند در ادامه تحصیل تفاوت ایجاد کند.»
- `WHY:` `در دنیای امروز` is a banned opener (LF-A2); concrete stakes beat abstract importance claims.

**12. Avoiding the AI tool-description cluster**
- `UNNATURAL_OR_WEAK:` «ابزار قدرتمند و جامع ما یک پلتفرم یکپارچه و تعاملی برای مدیریت هوشمند فرآیند پژوهش شماست.»
- `BETTER_PERSIAN:` «از انتخاب موضوع تا جلسه دفاع، هر فصل در یک صفحه وضعیت خودش را دارد؛ می بینید کدام مرحله جا مانده و چه کاری بعد از آن است.»
- `WHY:` The first sentence is the exact circulating boilerplate cluster (LF-A1); the second replaces adjectives with a concrete user-visible behaviour.

**13. Bullet rhythm**
- `UNNATURAL_OR_WEAK:` «ما خدمات متنوعی شامل نگارش پروپوزال، تحلیل آماری، ویرایش و مشاوره دفاع ارائه می دهیم که همه با کیفیت عالی و قیمت مناسب همراه هستند.»
- `BETTER_PERSIAN:» «هر مرحله، خدمات خودش را دارد:
  - پروپوزال: از بیان مسئله تا تصویب
  - تحلیل آماری: در SPSS و R، با گزارش فصل چهارم
  - ویرایش نهایی: طبق فهرست ایرادهای داوران»
- `WHY:` Corpus service menus are one line per service with concrete scope (LF-R2, LF-D7); the prose run-on hides the offer.

**14. Transition sentence**
- `UNNATURAL_OR_WEAK:` «علاوه بر این، لازم به ذکر است که moreover نکات دیگری نیز وجود دارد.»
- `BETTER_PERSIAN:` «تا اینجا روش را انتخاب کردید؛ قدم بعدی، تعیین حجم نمونه است.»
- `WHY:` Native transitions recap what was just established and name the next step (pattern from TG-13); `لازم به ذکر است` is notice-register (LF-D10).

**15. Introducing an example**
- `UNNATURAL_OR_WEAK:` «برای روشن تر شدن موضوع، مثال زیر را ملاحظه فرمایید.»
- `BETTER_PERSIAN:` «به عنوان مثال، فرض کنید سوال های پرسشنامه طیف ۱ تا ۵ دارند؛»
- `WHY:` `ملاحظه فرمایید` is officialese; `به عنوان مثال، فرض کنید` is the attested explanatory pattern (LF-D10, TG-26).

**16. Expressing caution about a claim**
- `UNNATURAL_OR_WEAK:` «این ابزار تضمین می کند که مقاله شما حتما پذیرش شود.»
- `BETTER_PERSIAN:` «هیچ ابزاری پذیرش را تضمین نمی کند؛ داوری به کامل بودن مرور ادبیات و روش شناسی شما بستگی دارد.»
- `WHY:` Trust is built by refusing guarantees (contrast with sales-register guarantee claims, TG-09); hedging follows `بستگی دارد` pattern (LF-D4, LF-D11).

**17. Conclusion / جمع بندی**
- `UNNATURAL_OR_WEAK:` «در پایان می توان گفت که تمامی موارد فوق الذکر به نحوی در افزایش کیفیت پایان نامه سهیم هستند.»
- `BETTER_PERSIAN:` «جمع بندی: اگر فقط یک کار را انجام می دهید، حجم نمونه را قبل از پخش پرسشنامه تعیین کنید؛ بقیه مراحل قابل جبران است، این یکی معمولا نیست.»
- `WHY:` The weak form is empty closure with `فوق الذکر` (officialese); strong closers prioritise (`اگر فقط یک کار...`) — pattern common in TG-13 posts.

**18. Heading, noun-phrase style**
- `UNNATURAL_OR_WEAK:` «بررسی تطبیقی راهکارهای بهینه سازی فرآیند تدوین فصل دوم»
- `BETTER_PERSIAN:` «فصل دوم را مقاله به مقاله ننویسید؛ روش دسته بندی موضوعی»
- `WHY:` Attested headings are concrete and name the artefact (`فصل دوم`) (LF-R4); abstract academic title style belongs to journals, not help content.

**19. Trust line for a consultancy page**
- `UNNATURAL_OR_WEAK:` «موسسه ما با کادر مجرب و پرسنل متخصص خود بهترین خدمات را با ضمانت کامل ارائه می نماید.»
- `BETTER_PERSIAN:` «پشتیبانی تا جلسه دفاع ادامه دارد؛ اگر داوران بعد از دفاع اصلاحی خواستند، همان اصلاح ها انجام می شود.»
- `WHY:` Replaces institutional self-praise with the attested local trust vocabulary (post-delivery support, payment terms) stated as concrete commitments (LF-D11).

**20. Acknowledging a deadline**
- `UNNATURAL_OR_WEAK:` «در صورت وجود محدودیت زمانی، لطفا موضوع را با کارشناسان ما در میان بگذارید.»
- `BETTER_PERSIAN:` «اگر دفاع تا آخر مهر است، از همین هفته شروع کنید؛ برای برنامه فشرده، ابتدا فصل هایی را می بینیم که داوران بیشترین ایراد را می گیرند.»
- `WHY:` Students frame needs as deadlines (LF-G2); copy that names the actual date pressure and responds with sequencing sounds native.

**21. Site orthography under the Teznevise ZWNJ rule**
- `UNNATURAL_OR_WEAK:` mixing `پایان‌نامه` (ZWNJ), `پایان نامه` (space), and `پایاننامه` (joined) across one page.
- `BETTER_PERSIAN:` «پایان نامه» written with a plain space, everywhere, on Teznevise.
- `WHY:` The corpus shows all three variants in the wild (LF-O1); the Teznevise constraint (no U+200C) makes the space-separated form the correct consistent choice on that site; consistency matters more than which variant.

**22. Politeness in contact-copy**
- `UNNATURAL_OR_WEAK:` «کاربر گرامی، در صورت تمایل به دریافت راهنمایی، فرم زیر را تکمیل نمایید.»
- `BETTER_PERSIAN:` «سوال تان کوتاه است؟ همین جا بنویسید؛ طولانی است؟ فایل تان را بفرستید تا با جزئیات پاسخ بدهیم.»
- `WHY:` `کاربر گرامی ... نمایید` is notice-register; corpus politeness pairs short requests with fast, specific channels (LF-G4, LF-D6).

**23. Explaining a statistical concept simply**
- `UNNATURAL_OR_WEAK:` «آزمون t یک روش آماری است که برای مقایسه میانگین دو گروه به کار می رود و در صورت معنادار بودن تفاوت ها را نشان می دهد.»
- `BETTER_PERSIAN:` «آزمون t جواب یک سوال ساده را می دهد: آیا تفاوت میانگین دو گروه واقعی است یا شانسی؟ اگر سطح معنی داری کوچک تر از ۰٫۰۵ باشد، تفاوت واقعی در نظر گرفته می شود.»
- `WHY:` The reframing-as-question pattern and the `کوچک تر از ۰٫۰۵` threshold phrasing mirror the practitioner channels (TG-07 content, modernised orthography; LF-S8).

**24. Question-hook opening for a blog post**
- `UNNATURAL_OR_WEAK:` «مقدمه: در این مقاله قصد داریم به بررسی موضوع نمونه گیری بپردازیم.»
- `BETTER_PERSIAN:` «قبل از پخش پرسشنامه، این برنامه تحلیل آماری را بنویسید»
- `WHY:` The weak form announces the article (`قصد داریم ... بپردازیم` — textbook register, LF-S8); the strong form is a concrete imperative hook, the dominant educational-channel title pattern (LF-D1, TG-02).

---

# Disagreements and Uncertainty

1. **Orthography of compound terms.** No consensus exists between `پایان نامه`, `پایان‌نامه`, and `پایاننامه` — even one holding company uses different forms in two channel titles (TG-09, TG-10). The corpus cannot arbitrate; the Teznevise ZWNJ ban resolves it locally, but this must not be generalised to other Persian sites.
2. **Formality of educational prose.** TG-01 (formal `است` register) and TG-02 (fully colloquial `می‌تونه` register) coexist with comparable audiences (39k vs 62k members). Both are successful; the corpus does not show which converts better. Recommendation to use a mixed register is therefore medium-confidence inference, not measurement.
3. **`رساله` scope.** TG-20 states the `پایان‌نامه`/`رساله` distinction explicitly, while TG-09 uses `پایان نامه` loosely for both degrees in the same post. Both usages are current; the distinction is prescriptive but not universal.
4. **`مساله` vs `مسئله`.** Both attested even within one channel (TG-01). Academic convention favours `مسئله`; confidence medium.
5. **Emoji acceptability.** Emoji are structural in every sales and most educational channels (LF-D7), yet the most credible explanatory posts (TG-13, TG-31) use them sparingly. The corpus supports restrained use; zero use is also defensible.
6. **Sales formulas.** Scarcity and urgency language is endemic (TG-02, TG-03) and presumably effective commercially, while eroding professional trust. The recommendation to avoid it is a positioning choice, not a corpus-proven language rule.
7. **`همانندجویی` vs `سرقت ادبی`.** Both are used (TG-01); `همانندجویی` is IranDoc-official, `سرقت ادبی` more common in general prose. No student usage of either term was observed in the corpus (students discuss the percentage, not the term) — flagged as an open question.
8. **Whether 2016-textbook register is "wrong".** It is not wrong Persian; it is dated register. Sites targeting older faculty reviewers may still need it in quoted regulation or template contexts.

---

# Recommendations for the Master SKILL

Only rules supported by more than one source are listed as rules; provisional items are labelled.

1. **Base register:** professional explanatory — `است` copula, `را`, `می‌شود`, `برای`, short-to-medium sentences, hedged claims. (TG-01, TG-11, TG-13 — rule.)
2. **Warmth layer:** permit written-colloquial verbs (`می‌تونه`, `پیام بدهید`) only in FAQ answers, intro empathy paragraphs, and comment replies; never in service descriptions or headings. (TG-02, TG-13, TG-25 — rule for placement; effectiveness provisional.)
3. **Banned list:** `می باشد`، `می گردد`، `خواهد گردید`، `جهت`، `می‌بایست`، `لازم به ذکر است`، `حاصل فرمایید`، `ملاحظه فرمایید`، `صورت پذیرد`، `مورد استفاده قرار می گیرد`، `در دنیای امروز`، `در عصر حاضر`، adjective stacks from the `قدرتمند/جامع/یکپارچه/تعاملی` cluster. (TG-16, TG-07, TG-22, TG-34, TG-01-ad — rule.)
4. **Keep the impersonal passive for services** (`انجام می شود`، `تحویل داده می شود`) — it is native and credible. (TG-03, TG-09, TG-11 — rule.)
5. **Fix terminology and repeat it**; no synonym rotation of `پروپوزال`، `پایان نامه`، `تحلیل آماری` etc. (Consistency across TG-01/02/09/13 — rule.)
6. **Borrowing policy:** `پروپوزال`، `پاورپوینت`، `چک لیست` in Perso-Arabic script; software, statistics, and index names in Latin script (`SPSS`, `P-value`, `ISI`, `EFA`); never transliterate a term that has a Persian equivalent in running prose (`رساله` not `دیزرتیشن`). (TG-01, TG-02, TG-07, TG-13, TG-20 — rule.)
7. **Address students through their situations:** open with the deadline, the reviewer objection, or the stage they are stuck at — not with service categories. (TG-28, TG-18, TG-17 — rule.)
8. **Reframe, do not mock:** when quoting student phrasing, restate it accurately with the precise term in the answer (`ویرایش نگارشی` for "داوران ایراد نگارشی دادند"). (TG-26 answer pattern — rule.)
9. **Uncertainty and non-guarantee:** use `بستگی دارد`، `معمولا`، `باید بررسی شود`; explicitly refuse acceptance guarantees. (TG-31, TG-19, contrast TG-09 — rule.)
10. **Headings:** `X چیست؟`، `چگونه ... کنیم؟`، `تفاوت X و Y`، `N اشتباه رایج ...` with Persian digits; never sentence-length or abstract-academic headings. (TG-01, TG-02, TG-09, TG-11 — rule.)
11. **Trust vocabulary for a consultancy:** concrete commitments (support until defense, documented responses to reviewer objections, per-stage deliverables) instead of `مجرب`، `باکیفیت`، `منحصر به فرد`. (TG-09/TG-27 provide the substance; cleaned form is our adaptation — provisional wording, firm principle.)
12. **Legal framing (from the master system, not this slice):** service language on Teznevise must be `مشاوره انجام پایان نامه` style — advisory framing — as required for compliance. This slice's evidence (TG-09, TG-10) shows the non-compliant `انجام پایان نامه` framing is the ecosystem default; the site must deliberately diverge from it.
13. **Orthography:** Persian `ی`/`ک` only (never Arabic `ي`/`ك`); `مسئله` consistently; Teznevise ZWNJ ban applies site-wide with space-separated compounds. (TG-07, TG-08 vs modern channels; TG-09/TG-10 variance — rule.)
14. **De-duplicate reposted boilerplate** before treating any circulating Persian template as "natural". (TG-22/TG-04 duplication — rule.)
15. *(Provisional)* Scarcity/urgency formulas should be omitted from Teznevise; they are endemic in the ecosystem but conflict with a compliance-first positioning.

---

# Machine-Readable Findings

```yaml
findings:
  - id: LF-S1
    category: syntax
    rule: "Definitional copula is 'است'; 'می باشد' and 'هست' are not used in modern explanatory prose"
    applies_to: [explanatory, service]
    confidence: high
    source_ids: [TG-01, TG-13, TG-16]
    exceptions: "university thesis templates may prescribe 'می باشد'"
  - id: LF-S2
    category: syntax
    rule: "'می گردد', 'خواهد گردید', 'صورت پذیرد' are officialese markers; avoid in reader-facing copy"
    applies_to: [explanatory, service, blog]
    confidence: high
    source_ids: [TG-16, TG-07]
    exceptions: "quoting regulations verbatim"
  - id: LF-S3
    category: syntax
    rule: "Impersonal passive 'انجام می شود' is the natural default frame for service descriptions"
    applies_to: [service]
    confidence: high
    source_ids: [TG-03, TG-09, TG-11]
    exceptions: ""
  - id: LF-S4
    category: syntax
    rule: "Use 'برای', never 'جهت', in reader-facing text"
    applies_to: [explanatory, service]
    confidence: high
    source_ids: [TG-09, TG-02, TG-13]
    exceptions: ""
  - id: LF-S5
    category: register
    rule: "Object marker 'را' in formal body text; 'رو' only in deliberately conversational segments"
    applies_to: [explanatory, conversational]
    confidence: high
    source_ids: [TG-01, TG-02, TG-13]
    exceptions: ""
  - id: LF-S6
    category: syntax
    rule: "Ezafe chains acceptable up to 3-4 links; longer chains read bureaucratic"
    applies_to: [service, explanatory]
    confidence: medium
    source_ids: [TG-09, TG-16]
    exceptions: ""
  - id: LF-S7
    category: syntax
    rule: "Question words: 'چگونه' written register, 'چطور' conversational hooks, 'چجوری' only in student speech"
    applies_to: [blog, headings, conversational]
    confidence: high
    source_ids: [TG-01, TG-02, TG-17]
    exceptions: ""
  - id: LF-S8
    category: anti_ai
    rule: "Pre-2017 textbook markers (Arabic ي/ك, 'چنانچه', 'به كار گرفته مي شود', 'مورد ... قرار مي گيرد') read dated; avoid"
    applies_to: [explanatory, service]
    confidence: high
    source_ids: [TG-07, TG-08]
    exceptions: "quoting old sources"
  - id: LF-S9
    category: syntax
    rule: "'هست' marks emphasis or colloquial speech, not neutral description"
    applies_to: [explanatory, conversational]
    confidence: medium
    source_ids: [TG-17, TG-28]
    exceptions: ""
  - id: LF-S10
    category: syntax
    rule: "Conditional 'اگر' neutral; 'چنانچه' officialese"
    applies_to: [explanatory]
    confidence: high
    source_ids: [TG-07, TG-02]
    exceptions: ""
  - id: LF-L1
    category: lexicon
    rule: "Verb slots: 'نگارش' headings, 'انجام' offers, 'نوشتن' neutral, 'تدوین' academic-administrative, 'آماده می شود' process"
    applies_to: [service, blog]
    confidence: high
    source_ids: [TG-01, TG-09, TG-11]
    exceptions: ""
  - id: LF-L2
    category: terminology
    rule: "'پروپوزال' is universal; publication jargon (ریجکت، اکسپت، سابمیت) is researcher-register and needs glossing for students"
    applies_to: [blog, explanatory]
    confidence: high
    source_ids: [TG-01, TG-09, TG-17, TG-14]
    exceptions: ""
  - id: LF-L3
    category: terminology
    rule: "Software and index names stay in Latin script (SPSS, R, ISI, EFA, P-value); never translated"
    applies_to: [explanatory, service]
    confidence: high
    source_ids: [TG-01, TG-02, TG-13, TG-14]
    exceptions: "'اس پی اس اس' transliteration exists but is dated"
  - id: LF-L4
    category: terminology
    rule: "'رساله' = PhD dissertation; 'پایان نامه' default for MA"
    applies_to: [all]
    confidence: high
    source_ids: [TG-20, TG-09]
    exceptions: "loose usage of 'پایان نامه' for both degrees is common"
  - id: LF-L5
    category: lexicon
    rule: "'دانش آموخته' official/testimonial register; 'فارغ التحصیل' neutral"
    applies_to: [service, news]
    confidence: high
    source_ids: [TG-16, TG-09]
    exceptions: ""
  - id: LF-L6
    category: lexicon
    rule: "Bureaucratic lexicon (ابلاغ، می‌بایست، در راستای، لغایت، مندرجات) belongs only to quoted regulations"
    applies_to: [service, explanatory]
    confidence: high
    source_ids: [TG-16]
    exceptions: ""
  - id: LF-L7
    category: lexicon
    rule: "Fixed collocations (تحلیل آماری، جامعه آماری، روایی و پایایی، بیان مسئله، جلسه دفاع، استاد راهنما) must not be paraphrased"
    applies_to: [all]
    confidence: high
    source_ids: [TG-01, TG-02, TG-07, TG-11, TG-13]
    exceptions: ""
  - id: LF-L8
    category: terminology
    rule: "'همانندجویی' is the official IranDoc term for similarity; 'سرقت ادبی/علمی' for plagiarism"
    applies_to: [blog, explanatory]
    confidence: medium
    source_ids: [TG-01]
    exceptions: "students use neither; they discuss the percentage"
  - id: LF-L9
    category: reader_language
    rule: "Student verbs: 'پخش کردن' (questionnaires), 'گیر دادن' (reviewer objects), 'جلو بردن', 'تموم کردن'"
    applies_to: [empathy copy, FAQ]
    confidence: high
    source_ids: [TG-17, TG-28]
    exceptions: "not for service prose"
  - id: LF-L10
    category: reader_language
    rule: "'توافقی' and 'فوری' are the standard student request markers for price and urgency"
    applies_to: [empathy copy]
    confidence: high
    source_ids: [TG-28]
    exceptions: ""
  - id: LF-D1
    category: discourse
    rule: "Question-hook pattern '#سوال:' + short question + '!؟' dominates educational Telegram and converts to blog hooks"
    applies_to: [blog, social]
    confidence: high
    source_ids: [TG-02, TG-24]
    exceptions: ""
  - id: LF-D2
    category: discourse
    rule: "Definitional opening: bare term + 'یک ... است که' + benefit; no preamble"
    applies_to: [blog, explanatory]
    confidence: high
    source_ids: [TG-01, TG-13]
    exceptions: ""
  - id: LF-D3
    category: discourse
    rule: "News lede: agent + past verb + object, then elaboration"
    applies_to: [news, blog]
    confidence: high
    source_ids: [TG-23, TG-12]
    exceptions: ""
  - id: LF-D4
    category: discourse
    rule: "Hedge with 'معمولا', 'ممکن است', 'بسته به ...', 'در برخی دانشگاه ها'"
    applies_to: [explanatory]
    confidence: high
    source_ids: [TG-20, TG-31]
    exceptions: ""
  - id: LF-D5
    category: discourse
    rule: "Scientific uncertainty: 'باید ... بررسی و تأیید شود'; personal doubt: 'بعید می دونم'"
    applies_to: [explanatory, blog]
    confidence: high
    source_ids: [TG-31, TG-19]
    exceptions: ""
  - id: LF-D6
    category: discourse
    rule: "Natural CTA: 'برای X به ... پیام بدهید / تماس بگیرید'; officialese CTA banned"
    applies_to: [service]
    confidence: high
    source_ids: [TG-02, TG-03, TG-09]
    exceptions: ""
  - id: LF-D7
    category: rhythm
    rule: "Emoji function as structural bullets on Telegram; convert to real bullets on website, at most one emoji role per page"
    applies_to: [service, blog]
    confidence: high
    source_ids: [TG-09, TG-11, TG-13]
    exceptions: ""
  - id: LF-D8
    category: rhythm
    rule: "Hashtags as in-text topic labels are Telegram-genre; do not imitate in site prose"
    applies_to: [blog]
    confidence: high
    source_ids: [TG-12, TG-02]
    exceptions: "social redistribution snippets"
  - id: LF-D9
    category: anti_ai
    rule: "Identical tool-description boilerplate circulates via reposts; de-duplicate before treating as naturalness evidence"
    applies_to: [methodology, editorial QA]
    confidence: high
    source_ids: [TG-22, TG-04]
    exceptions: ""
  - id: LF-D10
    category: discourse
    rule: "'لازم به ذکر است' and 'توجه:' mark notice/textbook register; use 'نکته:' instead"
    applies_to: [explanatory]
    confidence: high
    source_ids: [TG-16, TG-07]
    exceptions: ""
  - id: LF-D11
    category: register
    rule: "Local trust vocabulary = concrete commitments (support until defense, documented responses, payment terms); not 'مجرب' or 'باکیفیت'"
    applies_to: [service]
    confidence: high
    source_ids: [TG-09, TG-27]
    exceptions: ""
  - id: LF-R1
    category: rhythm
    rule: "Short paragraphs (1-4 lines) with blank-line separation"
    applies_to: [blog, service]
    confidence: high
    source_ids: [TG-01, TG-02, TG-13]
    exceptions: ""
  - id: LF-R2
    category: rhythm
    rule: "Lists for structure and steps; prose for definitions and arguments"
    applies_to: [explanatory]
    confidence: high
    source_ids: [TG-11, TG-24]
    exceptions: ""
  - id: LF-R3
    category: rhythm
    rule: "Alternate short and long sentences; uniform length reads artificial"
    applies_to: [explanatory, blog]
    confidence: medium
    source_ids: [TG-31, TG-22]
    exceptions: ""
  - id: LF-R4
    category: register
    rule: "Headings: 'X چیست؟', 'چگونه ... کنیم؟', 'تفاوت X و Y', 'N اشتباه رایج' with Persian digits; never sentence-headings"
    applies_to: [headings, blog]
    confidence: high
    source_ids: [TG-01, TG-02, TG-09, TG-11]
    exceptions: ""
  - id: LF-G1
    category: reader_language
    rule: "Students describe situations and deadlines, not services or terms; copy should open from the situation"
    applies_to: [empathy copy, FAQ, blog intros]
    confidence: high
    source_ids: [TG-28, TG-18]
    exceptions: ""
  - id: LF-G2
    category: reader_language
    rule: "Deadline-first framing ('فوری', 'تا شنبه', 'تا آخر مهر') is how students express urgency"
    applies_to: [empathy copy]
    confidence: high
    source_ids: [TG-28]
    exceptions: ""
  - id: LF-G3
    category: reader_language
    rule: "Possessive frame ('پروپوزال شما', 'استاد راهنمای شما') beats institutional address ('متقاضی محترم')"
    applies_to: [service, FAQ]
    confidence: high
    source_ids: [TG-18, TG-28]
    exceptions: ""
  - id: LF-G4
    category: reader_language
    rule: "Politeness bundle in expert-directed questions: greeting + well-wish + gratitude + 'میشه ... بفرمایید' with 'بنده' self-reference"
    applies_to: [FAQ, comment replies]
    confidence: high
    source_ids: [TG-18]
    exceptions: ""
  - id: LF-G5
    category: reader_language
    rule: "Code-switching (English source text inside Persian question) is normal; answers translate the concept"
    applies_to: [FAQ, comment replies]
    confidence: medium
    source_ids: [TG-18, TG-17]
    exceptions: ""
  - id: LF-G6
    category: reader_language
    rule: "Student spelling is error-prone; keep quotes authentic in testimonials, never in site prose"
    applies_to: [testimonials, editorial QA]
    confidence: high
    source_ids: [TG-28, TG-17]
    exceptions: ""
  - id: LF-G7
    category: reader_language
    rule: "Novices use generic verbs ('چکار کرده', 'نمیدونم چجوری'); expert answer restates the need with the precise term"
    applies_to: [FAQ, blog]
    confidence: high
    source_ids: [TG-26, TG-28]
    exceptions: ""
  - id: LF-G8
    category: reader_language
    rule: "'پارتنر' is established student vocabulary for study partner"
    applies_to: [empathy copy, blog]
    confidence: high
    source_ids: [TG-28]
    exceptions: "not in formal service prose"
  - id: LF-A1
    category: anti_ai
    rule: "Ban adjective-stack cluster 'قدرتمند/جامع/یکپارچه/تعاملی/هوشمند' + 'در یک پلتفرم ... گردهم آورده است'"
    applies_to: [all site copy]
    confidence: high
    source_ids: [TG-22, TG-34]
    exceptions: ""
  - id: LF-A2
    category: anti_ai
    rule: "Ban 'در دنیای امروز' / 'در عصر حاضر' openers"
    applies_to: [all site copy]
    confidence: high
    source_ids: [TG-01, TG-34]
    exceptions: ""
  - id: LF-A3
    category: anti_ai
    rule: "Avoid stacked 'می تواند ... کند' chains; alternate with 'اجازه می دهد', 'کمک می کند', direct verbs"
    applies_to: [explanatory, blog]
    confidence: medium
    source_ids: [TG-22, TG-34]
    exceptions: ""
  - id: LF-A4
    category: anti_ai
    rule: "No emoji inflation or mid-sentence '‼️'; restrained structural use only"
    applies_to: [all site copy]
    confidence: high
    source_ids: [TG-09, TG-10, TG-13]
    exceptions: ""
  - id: LF-A5
    category: anti_ai
    rule: "Scarcity/urgency formulas ('ظرفیت محدود', 'از دست نده') erode professional trust; omit on compliance-first sites"
    applies_to: [service]
    confidence: medium
    source_ids: [TG-02, TG-03, TG-24]
    exceptions: "endemic in ecosystem; positioning choice"
  - id: LF-A6
    category: anti_ai
    rule: "Fix technical terms and repeat; no synonym rotation"
    applies_to: [all site copy]
    confidence: medium
    source_ids: [TG-01, TG-02, TG-13]
    exceptions: ""
  - id: LF-A7
    category: anti_ai
    rule: "Vary sentence length and paragraph shape; uniformity is an AI marker"
    applies_to: [explanatory, blog]
    confidence: medium
    source_ids: [TG-31, TG-22]
    exceptions: ""
  - id: LF-A8
    category: anti_ai
    rule: "Register clash inside one sentence ('جهت ... پیام بدهید') is the strongest unnaturalness marker"
    applies_to: [editorial QA]
    confidence: high
    source_ids: [TG-09]
    exceptions: ""
  - id: LF-A9
    category: terminology
    rule: "Never transliterate a term that has a Persian equivalent ('رساله' not 'دیزرتیشن'); English gloss in parentheses is fine"
    applies_to: [all site copy]
    confidence: high
    source_ids: [TG-20]
    exceptions: ""
  - id: LF-O1
    category: register
    rule: "ZWNJ usage is unsettled in the wild; on Teznevise use space-separated compounds consistently (site-specific rule)"
    applies_to: [orthography]
    confidence: high
    source_ids: [TG-09, TG-10, TG-01]
    exceptions: "rule must not be generalised to other Persian sites"
  - id: LF-O2
    category: orthography
    rule: "Use Persian 'ی' and 'ک' only; Arabic 'ي'/'ك' read dated or careless"
    applies_to: [orthography]
    confidence: high
    source_ids: [TG-07, TG-08]
    exceptions: ""
  - id: LF-O3
    category: orthography
    rule: "Use 'مسئله' consistently; fixed collocation 'بیان مسئله'"
    applies_to: [orthography]
    confidence: medium
    source_ids: [TG-01, TG-20]
    exceptions: "both spellings current in the wild"
```

---

*End of report. All quotations are minimal and used solely as linguistic evidence; all constructed examples are original to this report. Private messages and closed-community content were excluded throughout.*