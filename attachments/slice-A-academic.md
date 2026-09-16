# Research Slice
- Assigned slice: A — Academic Persian (peer-reviewed articles, theses, university/research-centre material — Iranian Persian only)
- Date: 2026-09-15
- Agent/model: general subagent (Genspark Super Agent), slice-A academic researcher
- Scope boundaries:
  - **Covered:** article abstracts, introductions, methodology sections, discussion/conclusion sections, and author-guideline pages from Iranian علمی پژوهشی journals (وزارت علوم) across humanities and social sciences (sociology, political science, cultural studies, history, education/psychology, linguistics, literary studies, management, methodology), plus meta-articles that critique the structural language of Iranian academic articles (فربهی یا آماس، مقایسه مراحل چکیده، ارزیابی ساختاری مقالات). Also university author-guideline pages (`jss.ut.ac.ir`, `jolr.ut.ac.ir`, `jhss.ut.ac.ir`, `jsli.shirazu.ac.ir`, `method.rihu.ac.ir`, `jicr.ir`, `criticalstudy.ihcs.ac.ir`) as normative evidence of the target register.
  - **Not covered:** popular science, textbook Persian for undergraduates, translated academic prose treated as source Persian, Afghan Dari / Tajik academic prose, hard sciences/medicine outside Iranian humanities journals. Also excluded: student pay-to-write blog posts (`safir-paper`, `iranpaper`, `journalyab`), which are commercial paraphrases of academic norms, not evidence of them.
  - **Orthography rule for THIS file:** Teznevise forbids U+200C ZWNJ. Every Persian example in this document therefore writes compounds either fully joined (میتوان، نمیشود، آنها، میدهد) or with a normal space (می توان، نمی شود، آن ها، می دهد). Where a source's title contains a ZWNJ, we normalise it to a space when quoting it as a linguistic example (metadata rows keep the original for identification only). Follow the same rule in every downstream skill artefact.

# Source Register

| source_id | source_type | url_or_reference | publisher_or_community | date | audience | register | topic | why_this_source_is_useful |
|-----------|-------------|------------------|------------------------|------|----------|----------|-------|---------------------------|
| A-S01 | peer-reviewed article (methodology) | magiran.com/paper/2871277 — «واکاوی روش شناسی واسازی در پژوهش کیفی» | Magiran (indexed علمی پژوهشی) | ~1403 | researchers | high-formal, methodology paper | qualitative deconstruction method | Rich sample of هدف/چکیده verbs and hedged claims in qualitative-methods writing |
| A-S02 | peer-reviewed article | magiran.com/paper/2940761 — «واکاوی روش شناسی تحلیل مضمون» | Magiran | 1403 | researchers | methodology abstract | thematic analysis | Canonical abstract pattern: هدف — روش — یافته ها |
| A-S03 | peer-reviewed article | magiran.com/paper/2676766 — «نگاهی نو به روش شناسی اقدام پژوهی» | Magiran | 1402 | researchers | qualitative-methods review | action research | Uses formal reporting verbs and long ezafe chains |
| A-S04 | article | jsr.ut.ac.ir/article_74236 — «تاریخ همچون حماسه: باستان گرایی در ایران معاصر» | مطالعات جامعه شناختی، دانشگاه تهران | 1398 | sociology researchers | interpretive-sociology article, high-formal | political sociology of Iranshahri thought | Long Persian bibliography and formal argumentative prose |
| A-S05 | article + abstract | jsr.ut.ac.ir/article_104901 — «طبقه مستضعف: اغتشاشی مفهومی…» | مطالعات جامعه شناختی، ATU/UT | 1400 | sociology researchers | conceptual analysis article | class concept in revolutionary discourse | Model of «قصد … را دارد / نشان میدهد» sentence backbone |
| A-S06 | article | jsr.ut.ac.ir/article_56096 — «روایتهای دانش دینی اجتماعی…» | مطالعات جامعه شناختی | 1394 | sociology researchers | theoretical review article | religious knowledge and sociology | Persian+Latin bibliography, argumentation style |
| A-S07 | article | jsr.ut.ac.ir/article_56244 — «زبان و زندگی» | مطالعات جامعه شناختی | 1394 | philosophy/sociology | philosophical-sociological article | language and life (Wittgenstein/Heidegger) | Philosophical register with Farsi + transliterated names |
| A-S08 | article | ensani.ir/fa/article/402240 — «مقایسه مراحل در چکیده های مقالات علوم انسانی و پایه پزشکی» | ensani.ir / applied-linguistics journal | 1398 | applied linguists | genre-analysis meta-article | rhetorical moves in Persian abstracts | Direct evidence of Persian abstract move structure (Dudley-Evans model) |
| A-S09 | corpus paper | lsi-linguistics.ihcs.ac.ir/article_8798 — «پیکره چکیده های ATU» | زبان شناسی و گفتمان (IHCS) | 1400 | corpus linguists | applied linguistics article | 19k-abstract Persian academic corpus | Empirical statement that "زبان علم" has distinctive n-gram/word clusters in Iranian abstracts |
| A-S10 | critical-methodology article | method.rihu.ac.ir/article_178 — اسلامی اردکانی، «فربهی یا آماس» | فصلنامه روش شناسی علوم انسانی، پژوهشگاه حوزه و دانشگاه | 1391 | Iranian academics | critical meta-article | pathology of «pseudo-scientific» Iranian articles | Explicit taxonomy of empty/inflated academic writing patterns — best single anti-pattern source |
| A-S11 | methodology article | method.rihu.ac.ir/article_1148 — دانایی فرد، «روش شناسی دلالت پژوهی» | روش شناسی علوم انسانی | 1400 | methodology researchers | methodology introduction | implication-inquiry method | Long run-on «و … و …» sentences typical of high-formal Iranian humanities |
| A-S12 | article | jicr.ir/article_514 — «تحلیل گفتمان انتقادی چندوجهی» | تحقیقات فرهنگی ایران، پژوهشکده مطالعات فرهنگی | 1401 | cultural studies | article, medium-formal | multimodal CDA in Instagram | Contemporary hybrid style: theoretical terms + digital-era topic |
| A-S13 | article | jicr.ir/article_309 — «انگیزشهای نویافته تحولات هویتی زنان در آموزش عالی» | تحقیقات فرهنگی ایران | 1394 | sociology/education | grounded-theory qualitative article | women's identity in higher education | Standard passive-of-agentless construction «انجام گرفت / تحلیل شد» |
| A-S14 | article | economichistory.ihcs.ac.ir/article_14024 — «سیاستهای حکام قاجاری در کشاورزی کرمان» | تحقیقات تاریخ اقتصادی ایران، IHCS | 1401 | historians | historical article | Qajar agriculture in Kerman | Formal historical prose with «نشان میدهد که …» pattern |
| A-S15 | article | qjss.atu.ac.ir/article_5341 — فرهادی، «گیاه مردم نگاری کمره» | فصلنامه علوم اجتماعی، دانشگاه علامه طباطبائی | 1379/rev. | anthropologists | anthropology review, high-formal | ethnobotany | Longer sentences, generic-plural nominal style |
| A-S16 | article-list evidence | languagestudy.ihcs.ac.ir (زبانشناخت) latest issue | زبانشناخت، IHCS | 1403 | linguists | linguistics articles | Persian coordination, Avestan | Multiple abstract templates in one page |
| A-S17 | journal issue | lrr.modares.ac.ir/issue_2799_2848 — جستارهای زبانی | جستارهای زبانی، تربیت مدرس | 1404 | linguists | linguistics abstracts | grammar, translation, cognitive linguistics | Comparative template of linguistics abstracts |
| A-S18 | article | jep.atu.ac.ir latest issue (شیخ الاسلامی، «بدرفتاری روانشناختی…») | فصلنامه روانشناسی تربیتی، ATU | 1404 | psych researchers | quantitative empirical article | psychology of adolescents | Quantitative-methods register: «الگوی پیشنهادی از برازش مطلوبی برخوردار است» |
| A-S19 | article (psychology) | jep.atu.ac.ir (شریعتمدار، «مقایسه های ذهنی مادر») | روانشناسی تربیتی، ATU | 1404 | psych researchers | qualitative empirical (grounded theory) | mothers of ADHD children | Qualitative-empirical register in psychology |
| A-S20 | article — meta | criticalstudy.ihcs.ac.ir/article_8295 — «ارزیابی ساختاری مقاله های ادب عربی» | پژوهشنامه انتقادی متون، IHCS | 1400 | academics evaluating Persian scholarship | meta-evaluation article | quality of Persian academic abstracts and introductions | Reviews concrete flaws in Iranian abstracts and intros |
| A-S21 | article | jhss.ut.ac.ir issue — «پژوهشهای علوم تاریخی» | UT | 1403 | historians | historical article | Iranian history | Sample of «مقاله حاضر … می پردازد» openings |
| A-S22 | article | jhr.ui.ac.ir/article_16631 — «تعامل و تقابل تصوف و تشیع در عصر صفوی» | پژوهشهای تاریخی، اصفهان | 1394 | historians | historical article | Safavid Sufism–Shi'ism | «هدف مقاله حاضر … است» + waw-headed thesis clause |
| A-S23 | article | jhr.ui.ac.ir/article_16539 — «روابط سیاسی والی نشینان اردلان با حکومت صفویه» | پژوهشهای تاریخی، اصفهان | 1394 | historians | historical article | Ardalan-Safavid politics | Compact abstract; useful for headings |
| A-S24 | article | mri.modares.ac.ir/article_28891 — «چارچوب تحلیل اجتماعات برند مجازی» | پژوهشهای مدیریت در ایران، تربیت مدرس | 1404 | management researchers | systematic review + meta-synthesis | virtual brand communities | Management-register style, dense loanwords |
| A-S25 | article | mri.modares.ac.ir/article_28892 — «مدل سیاستهای ناکارآمد منابع انسانی» | پژوهشهای مدیریت در ایران | 1404 | HR/management researchers | qualitative empirical | isomorphic imitation | Iranian management abstract template |
| A-S26 | author guideline | jolr.ut.ac.ir/journal/about — پژوهشهای زبانی | UT Linguistics | current | prospective authors | norm-setting page | linguistics submission rules | Prescribes register/format |
| A-S27 | author guideline | jhss.ut.ac.ir (About) | UT History | current | authors | norm-setting page | history submission rules | Explicit register/language rules |
| A-S28 | author guideline | jsli.shirazu.ac.ir (About) — مطالعات آموزش و یادگیری | Shiraz University Education | current | authors | norm-setting page | education submission rules | Standardising register descriptors |
| A-S29 | author guideline | criticalstudy.ihcs.ac.ir/journal/authors.note — پژوهشنامه انتقادی متون | IHCS | current | authors | norm-setting page | Persian abstract length + structure | Prescribes 200-word abstract and «چکیده مبسوط» |
| A-S30 | article (methodology) | jpll.ui.ac.ir/article_16251 — احمد رضی، «روش در تحقیقات ادبی ایران» | پژوهش زبان و ادبیات فارسی، اصفهان | 1394 | literary researchers | methodology essay | typology of Iranian literary research | Meta-source with 13-way typology of literary-studies writing |
| A-S31 | article (economics-history abstract) | economichistory.ihcs.ac.ir various | IHCS | 1400+ | historians | history abstracts | Iranian economic history | Repeated conjunction «اما» + waw chains |
| A-S32 | journal home + article list | jsal.ut.ac.ir — جامعه شناسی هنر و ادبیات | UT | current | sociology-of-art researchers | journal norm page + abstracts | sociology of art | Alternative sub-register (art-oriented sociology) |
| A-S33 | article guide | psq.bou.ac.ir (About) — علوم سیاسی | Bāqir al-Ulum University | current | authors | political-science register | article norms | Confirms «چکیده انگلیسی + کلیدواژه ها» norm |
| A-S34 | journal home | ipsajournal.ir — پژوهشنامه علوم سیاسی | Iranian Political Science Association | current | political scientists | research-focus norm page | political science | «مسائل ایران»-focused rhetoric |
| A-S35 | article + issue list | languagestudy.ihcs.ac.ir/article_10100 — «همپایه انفصالی در زبان فارسی» | زبانشناخت | 1404 | linguists | data-driven linguistics article | Persian coordination | Concrete non-medical-humanities empirical linguistics abstract |

# High-Confidence Language Findings

**FN-A-001 — Abstract move structure follows a fixed هدف→روش→یافته ها→نتیجه skeleton.**
Persian academic abstracts across humanities and social sciences almost always open with a هدف/purpose clause («هدف این مقاله … است»، «پژوهش حاضر با هدف … انجام شد»)، then شرح روش («این پژوهش از نوع … است / با روش … انجام گرفت»)، then یافته ها («یافته ها نشان داد که …»)، then نتیجه/دلالت («بر اساس نتایج …»). Evidence: A-S02, A-S05, A-S12, A-S13, A-S14, A-S18, A-S19, A-S24, A-S25, A-S29; the meta-study A-S08 makes this explicit (Dudley-Evans moves). Register: علمی پژوهشی abstracts in all disciplines. Exception: pure philosophy/interpretive articles (A-S07) may omit روش. Confidence: **high**.

**FN-A-002 — The default writer's self-reference is the third-person nominal «مقاله حاضر / پژوهش حاضر / نویسنده / نگارنده / نگارندگان».**
"من / ما" as authorial pronouns are almost absent from Iranian علمی پژوهشی prose; the writer refers to themselves as «مقاله حاضر»، «پژوهش حاضر»، «نویسنده»، «نگارندگان» (A-S05, A-S13, A-S14, A-S20, A-S22, A-S30). Where a first-person plural does appear, it is «به کار می بریم / مراجعه کرده ایم / تمرکز داشته ایم» — a rhetorical مای علمی that is treated as formal, not personal (A-S05). Exception: reflective essays and some interpretive-sociology pieces do use «ما» (A-S07). Confidence: **high**.

**FN-A-003 — The dominant tense of the METHODS section is agentless past passive.**
«انجام شد / انجام گرفت / گردآوری شد / تحلیل شد / بررسی شد / استفاده شد / انتخاب شدند». Evidence: A-S13 («این مقاله با روش نظریه زمینه ای به بررسی … پرداخته»)، A-S18 («تحلیل داده ها با بهره گیری از نرم افزار … انجام گرفت»)، A-S19 («کدگذاری ها به صورت سه مرحله ای …»)، A-S24, A-S25. Applies to: empirical/quantitative and qualitative-empirical articles. Exception: theoretical/philosophical papers use present tense of description («این مقاله … را بررسی می کند»). Confidence: **high**.

**FN-A-004 — The dominant tense of FINDINGS is present (نشان میدهد / بیانگر آن است / حاکی از … است).**
«نتایج نشان داد که …» (past) is common for empirical results, but general statements of what a study "demonstrates" use present indicative («تحلیل ما نشان میدهد که …»، «یافته ها بیانگر آن است»، «نتایج حاکی از …»). Evidence: A-S05, A-S09, A-S12, A-S14, A-S18. Confidence: **high**.

**FN-A-005 — Reporting verbs cluster into a small stable set.**
The recurrent reporting-verb inventory of Iranian academic Persian: نشان می دهد، اشاره می کند، بیان می کند، مطرح می سازد، تبیین می کند، تصریح می کند، معتقد است، استدلال می کند، به این نتیجه رسید که، بر آن است که، تأکید می کند بر، به نقل از (author) …، به باور (author). Rare in academic register: می گوید، حرف می زند، اذعان دارد, and the journalistic "به گفته X". Evidence across A-S05, A-S06, A-S10, A-S20, A-S30. Confidence: **high**.

**FN-A-006 — Ezafe chains of 3–5 nouns are normal and expected.**
Chains such as «بازخوانی مفهومی طبقه ی مستضعف در ادبیات انقلاب 1357» (A-S05)، «تحلیل ساختاری مقالات علمی پژوهشی حوزه علوم انسانی» (A-S20)، «مطالعه ی موردی چکیده ها و مقدمه های مجله ادب عربی» (A-S20) are typical. Chains longer than five are frowned upon by editors (A-S10, A-S20 both flag them as آماس/inflation). Confidence: **high**.

**FN-A-007 — Nominalisation dominates verbal style.**
Where an editorial or professional text would say «بررسی می کنیم که چطور …»، an academic paper uses «به بررسی چگونگی … می پردازد» or «تبیین چگونگی … مورد نظر است». The «به + مصدر/اسم مصدر» + «پرداختن / اقدام کردن / مبادرت ورزیدن» pattern is a signature move (A-S02, A-S05, A-S14, A-S22). Confidence: **high**.

**FN-A-008 — «مورد + مصدر + قرار گرفت» is the workhorse passive.**
«مورد بررسی قرار گرفت / مورد مطالعه قرار میگیرد / مورد توجه قرار داده شد». Native of Iranian academic Persian; considered normal by most editors even though ویراستاران (A-S10, editorial-purism sources) argue it is a translation calque and prefer «بررسی شد». Evidence: A-S07, A-S14, A-S15, A-S22, A-S30. Confidence: **high**. Contradiction: the ویرایش-purism tradition (Ahmad Samii-Gīlānī school, «virastaran.net»/A-S10 anti-pattern list) calls this weak; but it is factually pervasive in current Iranian academic prose. Do not treat it as an anti-pattern by default.

**FN-A-009 — Passive of agency is agentless.**
Persian academic prose almost never says «X توسط Y بررسی شد»; when authorship is stated, it is nominalised («این پژوهش به وسیله نگارندگان صورت گرفته است») or the agent is dropped entirely. «توسط» is tolerated but the standard editorial preference is «به وسیله / از سوی / به دست» (A-S22 uses «به وسیله»). Confidence: **high**.

**FN-A-010 — Hedging is dense and formulaic.**
Hedges: «به نظر می رسد که»، «می توان گفت که»، «احتمالاً»، «ظاهراً»، «چه بسا»، «شاید بتوان»، «تا حدی»، «به گونه ای که»، «تا آنجا که». Boosters: «بی تردید»، «بدون شک»، «قطعاً»، «به روشنی»، «بی گمان»، «به وضوح». Empirical papers hedge more; theoretical/argumentative papers use boosters more freely. Evidence: A-S05, A-S07, A-S10, A-S22. Confidence: **high**.

**FN-A-011 — Discourse connectives form a rigid inventory.**
Additive: افزون بر این، علاوه بر این، همچنین، نیز، به علاوه. Contrastive: اما، ولی، در حالی که، بر خلاف، بر عکس، از سوی دیگر. Consequential: بنابراین، از این رو، در نتیجه، لذا، پس. Causal: زیرا، چرا که، چون، به این دلیل که، از آن جهت که. Reformulative: به عبارت دیگر، به بیان دیگر، به دیگر سخن، یعنی. Concessive: با این حال، با وجود این، هرچند، اگرچه. Sequence: نخست، سپس، آنگاه، در پایان، در نهایت. Evidence across A-S02, A-S05, A-S07, A-S10, A-S11, A-S12, A-S14, A-S15, A-S22, A-S30. Confidence: **high**.

**FN-A-012 — «لذا» is the marked variant of «بنابراین/از این رو».**
«لذا» carries a stronger institutional/formal color (common in law, management, government-adjacent research; A-S15 uses «لذا مردم نگاران و مردم شناسان را به عنایت به این حوزه ترغیب میکند»). Prestige-neutral connective in humanities: «از این رو» / «بنابراین». Confidence: **medium**.

**FN-A-013 — Terminology: Persian coinage vs Arabic-technical vs loanword.**
Three concurrent lexical layers coexist: (a) Persian coinages (فرهنگستان-adjacent): برساخت، هم پایگی، کنشگر، خرده روایت، بازنمایی، درون داد؛ (b) Arabic technical loans (traditional humanities): استنتاج، استقرا، دلالت، تفسیر، تأویل، تبیین، تقریر، مفصل بندی؛ (c) direct loanwords (management, computing, methodology): پارادایم، متاآنالیز، فراترکیب، دیسکورس (rare — usually replaced by گفتمان)، اپیستمولوژی. Convention: philosophy/sociology of knowledge tolerates (b); management and empirical social sciences use (c); linguistics leans on (a) (A-S16, A-S17, A-S35). Confidence: **high**.

**FN-A-014 — گفتمان has fully displaced discourse/discours as the technical term.**
Not a single article in the corpus uses «دیسکورس» as the primary term; «تحلیل گفتمان» is universal (A-S06, A-S07, A-S12, A-S17). Confidence: **high**.

**FN-A-015 — Titles are noun-phrase-plus-colon structures, not questions.**
Standard title patterns: «X: Y با تأکید بر Z»؛ «بررسی/تحلیل/واکاوی/مطالعه X در Y»؛ «X: مطالعه ای موردی از Y»؛ «X در Y: از منظر Z». Interrogative titles («چرا X روی می دهد؟») exist but remain a minority — evidence: A-S05 uses «طبقه مستضعف: اغتشاشی مفهومی یا تلفیق گر سرمایه های نمادین» (a rhetorical binary). Confidence: **high**.

**FN-A-016 — «مطالعه ی موردی» / «موردکاوی» is the marked term of choice for case studies; «کیس استادی» is unacceptable.**
Evidence: A-S01, A-S12, A-S15, A-S30. Confidence: **high**.

**FN-A-017 — Persian abstracts are between 150 and 300 words; چکیده مبسوط between 500 and 1000 words.**
Explicit rule in A-S28 (Shiraz), A-S29 (IHCS), and A-S26 (UT Linguistics). Iranian journals distinguish «چکیده معمولی» (~200 کلمه) from «چکیده مبسوط» (Extended Abstract, 500–1000 کلمه). A-S09's corpus confirms 175–250 words is the empirical mean. Confidence: **high**.

**FN-A-018 — Keywords (کلیدواژه ها) are noun phrases 5–7 items long.**
Verbs and adjectives are almost never keywords; multiword phrases with ezafe are standard. Evidence: A-S05, A-S12, A-S13, A-S22, A-S29 (rule: 5–7 keywords). Confidence: **high**.

**FN-A-019 — In-text citation follows one of two Iranianised APA variants: (نام، سال: صفحه) or (نام سال، صفحه).**
Format is a house choice; the two commonest are «(طباطبایی، 1396: 127)» and «(Foucault, 2002, p. 45)». Full titles italicised in bibliographies (A-S06, A-S07). Direct-quote-by-page-number is rare in humanities papers, more common in فقه/philosophy. Confidence: **high**.

**FN-A-020 — Bibliographies mix Persian and Latin sections under separate headings.**
Standard structure: منابع فارسی، منابع لاتین (or "کتاب نامه ی لاتین"). Evidence: A-S04, A-S06, A-S07. Confidence: **high**.

**FN-A-021 — Long, semicolon-and-comma stitched sentences are the norm.**
30–60-word single sentences with «و … و … که …» are typical in high-formal articles. A-S11 opens with a single sentence spanning ~90 words. Editors (A-S10) criticise this but concede it is register-marked. Confidence: **high**.

**FN-A-022 — «که» clauses stack; up to 3 levels of complementisers in one sentence.**
E.g. «نتایج شاخصهای برازش مدل نشان داد که الگوی پیشنهادی از برازش مطلوبی با داده ها برخوردار است و … به طوری که … رابطه ای منفی و معنادار … دارد» (A-S18). Confidence: **high**.

**FN-A-023 — Second-person address is absent.**
No «شما / تو» in academic prose. Reader is not addressed. Even when the writer performs a rhetorical gesture, they use «خواننده» or an impersonal construction («می توان دریافت که …»). Evidence: entire corpus. Confidence: **high**.

**FN-A-024 — The rhetorical question is used sparingly and marked-formally.**
When used, it opens sub-sections: «چه رابطه ای میان X و Y وجود دارد؟»، «آیا میتوان از X سخن گفت؟». It is not a page-title device (contra popular blogs/service-page Persian). Evidence: A-S05, A-S07, A-S11 (single rhetorical opening question). Confidence: **medium**.

**FN-A-025 — Research questions (پرسش های پژوهش) are numbered, indirect, and start with an interrogative particle plus «آیا/چه/چگونه/چرا».**
E.g. «پرسش اصلی این پژوهش عبارت است از این که: چگونه X در Y بازنمایی می شود؟». Evidence: A-S24, A-S25, A-S18. Confidence: **high**.

**FN-A-026 — Limitations (محدودیت های پژوهش) get a formulaic paragraph near the end.**
Standard openers: «این پژوهش با محدودیت هایی نیز مواجه بوده است، از جمله …»، «از جمله محدودیتهای پژوهش حاضر می توان به … اشاره کرد». Confidence: **high**.

**FN-A-027 — Suggestions (پیشنهادها) close the article, using «پیشنهاد می شود که …» (subjunctive).**
Evidence: A-S18, A-S24. Confidence: **high**.

**FN-A-028 — «پژوهش/تحقیق» is the primary lexical anchor.**
«پژوهش» outnumbers «تحقیق» in current humanities and social sciences journals (A-S09's corpus data confirms it), but «تحقیق» dominates law, some management journals, and older sources. «مطالعه» is used in psychology/health and A-S18-style empirical articles. Confidence: **high**.

**FN-A-029 — «باشد» as a copular filler is a known anti-pattern but persistent.**
Purists (A-S10, ویرایش-purism sources) reject «X شامل … می باشد» in favour of «X شامل … است». It still appears in ~30–40% of management/HR abstracts (A-S24 uses «رایج ترین آن … می باشد») and less in philosophy/history. Confidence: **medium**.

**FN-A-030 — «انجام گرفت / انجام شد / صورت گرفت / صورت پذیرفت» are near-synonymous method-verbs, ordered by formality.**
«صورت پذیرفت» is most formal, «انجام گرفت» is next, «انجام شد» is neutral, «صورت گرفت» is common in psychology. Evidence: A-S13, A-S15, A-S18, A-S19, A-S24. Confidence: **medium**.

**FN-A-031 — Author-guideline pages themselves use a highly formal register that leaks into papers.**
Verbs like «الزامی است»، «موظف است»، «ملزم است»، «مجاز نیست»، «باید ارسال شود / قرار داده شود / بارگذاری گردد». This governmental-formal tone is separate from the prose register and should not colonise the article body (A-S26, A-S27, A-S28, A-S29). Confidence: **high**.

**FN-A-032 — «گردیدن» is used as a formal alternative to «شدن», especially in guideline/method language.**
E.g. «بارگذاری گردد»، «تدوین گردید». It is stylistically formal-heavy; overuse in a research article is flagged by editors (A-S10). Evidence: A-S18, A-S26. Confidence: **medium**.

**FN-A-033 — Direct short quotations are placed inside «» (guillemet-style Persian quotes), not English "quotes".**
E.g. «مفهوم "برساخت" یا «برساختن هویت» به معنای …». Evidence: A-S05, A-S07, A-S12. Confidence: **high**.

**FN-A-034 — Two orthographic norms coexist: (a) full ZWNJ-based (میتوان با نیم فاصله written as می‌توان)، (b) space-separated (می توان).**
Iranian journals overwhelmingly use ZWNJ-based writing; the "solid" form (میتوان) is rare and looks colloquial to academic readers. The Teznevise site enforces a policy that departs from the academic norm — writers producing academic-flavoured content for that site must be told this explicitly so they don't fall back to defaults. Evidence: all article sources. Confidence: **high**. (This is the LANGUAGE_FINDING that dictates the file-level orthography rule at the top.)

**FN-A-035 — Numbers appear in Persian digits (۰-۹) inside the body; in-text citations and DOIs use Latin digits.**
Evidence: A-S18 uses «۲۲۰ نفر» in the body but 2004, 2014, 1988 for citation years. Confidence: **high**.

**FN-A-036 — Two systems of quotation of foreign author names: (a) Persian transliteration + Latin in parentheses, (b) direct Latin in-line.**
Standard: «فوکو (Foucault, 2002) معتقد است …». Some journals keep the whole citation Persianised; Latin transliteration is the default in linguistics/philosophy. Evidence: A-S04, A-S06, A-S07, A-S30. Confidence: **high**.

**FN-A-037 — «رویکرد X-محور» / «X-گرا» / «X-مدار» are highly productive coinage patterns.**
Examples in corpus: مسأله محور، متن محور، پژوهش محور، نظریه محور، دولت محور. And -گرا: صورت گرا، نقش گرا، ساخت گرا، کنش گرا. Evidence: A-S07, A-S09, A-S16, A-S30. Confidence: **high**.

**FN-A-038 — «شبه X»، «فرا X»، «پسا X»، «پیشا X»، «ضد X»، «هم X» are productive academic prefixes.**
E.g. شبه اسطوره ای (A-S16), فراترکیب (A-S24), پسا مدرن، پیشا اسلامی، ضد استعماری، هم عرض. These are treated as one graphic unit with ZWNJ in native journals — under the no-ZWNJ rule they must be written joined (فراترکیب) or with a hyphen never; a space is acceptable but visually weaker. Confidence: **high**.

**FN-A-039 — Anti-pattern: «آماس» — inflated pseudo-scientific structure.**
A-S10 (اسلامی اردکانی) identifies specific inflation moves: (1) کولاژ (copy-pasting from many sources without stitching argument); (2) تکثیر ناموجه منابع (padding bibliography); (3) تکه نویسی (headed sub-sub-sections with no argumentative connection); (4) «حاشیه پردازی» / «مقدمه چینی افراطی» — long introductions that never state the problem clearly; (5) claiming a "gap" without demonstrating it. A-S20 identifies further flaws in Iranian abstracts and intros: (6) absent research problem, (7) mere topic-declaration in place of thesis, (8) restating title as if it were a claim. Confidence: **high**.

**FN-A-040 — Anti-pattern: translationese calques.**
Persistent translationese in Iranian academic prose: «بازی کردن نقش» (calque of "play a role") — natural Persian is «نقش داشتن / ایفا کردن»; «در تلاش برای X بودن» — natural is «برای X می کوشد»; «به نوبه ی خود» — natural is «به سهم خود» or omit; «داشتن یک X» — Persian rarely uses indefinite article «یک»; «توسط» — often better replaced by «به دست / از سوی / به وسیله»؛ «مورد استفاده قرار گرفت» — often replaceable by «به کار گرفته شد / به کار رفت». Evidence: A-S10, A-S20 and general ویرایش literature. Confidence: **high**. Note: the current usage norm of Iranian journals accepts many of these; the rule for a writer aiming at high-quality academic prose is not to eliminate them entirely but to avoid stacking them.

**FN-A-041 — Anti-pattern: AI-style generic openings.**
Openings the corpus never uses: «در دنیای امروز که هر روز شاهد پیشرفتهای شگرف هستیم …»، «بی تردید یکی از مهمترین موضوعات …»، «در این مقاله به بررسی جامعی می پردازیم …». Real Iranian abstracts open with the thesis: «هدف این مقاله … است». Evidence: negative — none of A-S02, A-S05, A-S12, A-S13, A-S14, A-S18, A-S24 begin with sweeping generic sentences. Confidence: **high**.

**FN-A-042 — Anti-pattern: rule-of-three noun stacks («انسجام، هماهنگی و یکپارچگی»).**
Iranian academic prose has its own version of the "rule of three" — noun triplets that pad but don't inform. Editors (A-S10) call this «سه گانه پردازی توخالی». Genuine coordinations of three are fine («مقدمه، بحث و نتیجه»)؛ synonym-stacking is not. Confidence: **medium**.

**FN-A-043 — Anti-pattern: the empty methodology paragraph.**
Instances such as «روش این پژوهش کیفی و از نوع توصیفی تحلیلی است و داده ها از منابع کتابخانه ای گردآوری شده اند» — flagged by A-S10 and A-S20 as a template that says almost nothing. Real methodology paragraphs specify data source, sampling logic, and analytic technique (e.g. A-S18 lists five instruments; A-S24 lists systematic-review protocol; A-S19 names Strauss-Corbin coding). Confidence: **high**.

**FN-A-044 — Reader-language: the reader is «خواننده / پژوهشگر / مخاطب علمی», never «دوستان / کاربران / شما»**.
Confidence: **high**. Applies to every register within academic Persian.

**FN-A-045 — Modality: «باید / بایستی / لازم است / ضرورت دارد» expresses academic obligation.**
Not «مجبوریم»، not «باید حتماً». «به نظر می رسد که باید …» is the hedged norm for a methodological recommendation. Confidence: **high**.

**FN-A-046 — Verb ordering: subject–object–verb is strictly maintained; fronting is rare.**
Iranian academic Persian tolerates topicalisation («این مقاله را با هدف … نگاشته ایم») but keeps the verb in final position. Journalistic/professional Persian allows more verb-early sentences («نگارش شد این مقاله با هدف …») — this is unacceptable in academic register. Confidence: **high**.

**FN-A-047 — Anti-pattern: overuse of «می باشد» in place of «است».**
Purism (A-S10) rejects it as translationese; empirical corpus (A-S24 abstract uses «رایج ترین آن … می باشد») shows management writing still uses it. Rule for a stylist: prefer «است» unless disambiguating tense or aspect. Confidence: **medium**.

**FN-A-048 — The article-final sentence pattern is one of: (a) «به این ترتیب / بدین سان …»؛ (b) «در نهایت …»؛ (c) «نتایج این پژوهش می تواند …».**
Evidence: A-S13, A-S14, A-S18, A-S24. Confidence: **high**.

**FN-A-049 — Hedged prediction of usefulness: «می تواند … راهگشا باشد / سودمند باشد / یاری رسان باشد».**
The value-claim clause at the end of the abstract. Evidence: A-S24 («نتایج این پژوهش می تواند در شناخت ماهیت اجتماعات برند، بررسی چالش ها، تدوین راهبردهای مدیریتی … راهگشا باشد»)، A-S18. Confidence: **high**.

**FN-A-050 — The «بحث و نتیجه گیری» section combines discussion and conclusion in a single labeled section.**
Iranian journals rarely separate «Discussion» from «Conclusion» in the Anglo-American way. Section heading in almost every empirical article: «بحث و نتیجه گیری» (A-S13, A-S18, A-S19, A-S24, A-S25). Confidence: **high**.

# Register Map

**Academic Persian vs professional-explanatory (site-copy / editorial explainer) Persian:**
- Academic uses «مقاله حاضر / پژوهش حاضر» as author self-reference; professional-explanatory uses «در این مقاله / در این نوشتار» and sometimes «ما» inclusively.
- Academic favors ezafe-heavy noun phrases; explanatory favors verb-driven short clauses («این کار را انجام میدهیم که …»).
- Academic hedges systematically («به نظر میرسد که …»)؛ explanatory omits hedges or uses direct promises.
- Academic never addresses «شما»؛ professional-explanatory routinely does.
- Academic never opens with a rhetorical question as page-title; explanatory does.
- Academic keywords are nominal phrases; explanatory has none.

**Academic Persian vs student/community Persian (blogs, پرسش و پاسخ):**
- Student writing over-uses «می باشد»، «مورد بررسی قرار گرفت» and struggles with ezafe chains it can't resolve.
- Community Persian permits «هست/نیست», «-ه» ending on verbs («انجام شده»), and non-standard punctuation.
- Academic controls the reporting-verb inventory; student writing collapses into «گفت / بیان کرد» pairs.
- Community writing mixes English words unmarked («روش X رو با data collection انجام دادیم»)؛ academic Persian either fully Persianises or clearly marks Latin in parentheses.
- Academic never uses colloquial subjunctive «بره / بشه / بگه»؛ student informal does.

**Academic Persian vs service-page / marketing Persian:**
- Service-page opens with a benefit («خدمات ما به شما کمک میکند تا …»)؛ academic opens with a هدف statement.
- Service-page uses lists of features; academic uses paragraphs of argument.
- Service-page uses «شما» explicitly; academic never.
- Service-page favors simple verbs and boosters; academic favors nominalised structures and hedges.
- Service-page uses call-to-action verbs («تماس بگیرید»، «همین حالا سفارش دهید»)؛ academic has no equivalent.

**Sub-registers WITHIN academic Persian:**
- **Philosophy/theoretical humanities** (A-S07, A-S11) — long sentences, boosters preferred, Arabic-technical lexicon, «معتقد است / بر آن است».
- **Empirical qualitative** (A-S13, A-S19) — grounded-theory vocabulary («مقوله محوری، کدگذاری باز، اشباع نظری»)، ~450 word abstracts.
- **Empirical quantitative** (A-S18, A-S24) — «معناداری، برازش مطلوب، رابطه معنادار»، heavy tool-naming.
- **Historical article** (A-S14, A-S22, A-S23) — narrative-past tense («تصرف نمودند / احداث کرد»)، sources over methodology.
- **Linguistics** (A-S16, A-S17, A-S35) — data-driven mini-abstracts, high loanword tolerance.
- **Management** (A-S24, A-S25) — most translation-calque-heavy, highest «می باشد» use.

# Vocabulary and Collocation Map

**High-frequency academic verbs (in order of frequency, approximate):**
بررسی کردن، نشان دادن، پرداختن به، مطرح کردن، تبیین کردن، ارائه دادن، مورد بررسی قرار دادن، به کار بردن، توصیف کردن، تحلیل کردن، شناسایی کردن، مقایسه کردن، ارزیابی کردن، تأکید کردن، اشاره کردن، بیان کردن، به دست آوردن، دستیابی به، واکاوی کردن، تدوین کردن.

**High-frequency academic nouns:**
پژوهش، تحقیق، مطالعه، مقاله، بررسی، تحلیل، رویکرد، روش، نظریه، مفهوم، چارچوب، الگو، مدل، یافته، نتیجه، داده، شاخص، متغیر، فرضیه، سؤال، مسأله، پرسش، هدف، ضرورت، اهمیت، جامعه ی آماری، نمونه، پیشینه، ادبیات نظری، مبانی نظری، محدودیت، پیشنهاد.

**Signature academic collocations:**
- «پژوهش حاضر با هدف … انجام شده است»
- «هدف مقاله حاضر … است»
- «این پژوهش از نوع … و به روش … انجام گرفت»
- «داده ها با استفاده از … گردآوری شد»
- «برای تحلیل داده ها از … بهره گرفته شد»
- «یافته ها نشان داد که …»
- «نتایج حاکی از آن است که …»
- «تحلیل ما نشان میدهد که …»
- «بر اساس یافته های پژوهش، می توان نتیجه گرفت که …»
- «نتایج این پژوهش می تواند در … راهگشا باشد»
- «از جمله محدودیتهای این پژوهش می توان به … اشاره کرد»
- «پیشنهاد می شود که در پژوهشهای آتی …»
- «چارچوب نظری این پژوهش برگرفته از دیدگاه X است»
- «در ادامه به X پرداخته می شود»
- «X، به تعبیر Y عبارت است از …»

**Loanword handling policy (observed):**
- Fully Persianised: گفتمان، بازنمایی، برساخت، هم پایگی، ساخت گرا، نقش گرا.
- Persian-loanword doublets (both live): پارادایم / سرمشق (پارادایم dominant)، متد / روش (روش dominant)، منابع / رفرنس (منابع dominant)، اپیستمولوژی / معرفت شناسی (معرفت شناسی dominant).
- Loanword-only: آنتولوژی/هستی شناسی (both used, هستی شناسی preferred by philosophers; آنتولوژی by IT/management), فراترکیب (from meta-synthesis; no Persian substitute), گرندد تئوری / نظریه ی زمینه ای (both live).
- Never Persianise: proper names, statistical procedure names in short form (SPSS، SmartPLS، fMRI), analytic software names.

# Syntax and Rhythm Rules

1. Prefer nominalised heads for headline sentences: «هدف مقاله حاضر بررسی X است» beats «این مقاله میخواهد X را بررسی کند».
2. Reserve verb-final long sentences for argument sentences; keep methods sentences shorter (12–20 words) so the reader can extract facts.
3. Use one connective per sentence-boundary. Do not stack «بنابراین از این رو …» — pick one.
4. Ezafe chains up to five nouns are natural. At six, break with a comma or a «که»-clause. At seven+, the sentence has failed.
5. In an abstract, the first sentence carries the هدف, the second carries the روش, the third the یافته, the fourth the نتیجه. Longer abstracts elaborate but do not depart from this order.
6. Avoid the double-passive: «مورد بررسی قرار داده شد» — one passivisation is enough («بررسی شد»).
7. Prefer «نشان میدهد که …» over «به این نتیجه رسیده است که …» when reporting an article's own claim; the latter for reporting a cited author.
8. When reporting cited authors, use present-indicative reporting verbs: «معتقد است، مطرح می کند، تصریح می کند» — not past.
9. Use «آنها» (or «آن ها» without ZWNJ under this file's orthography) for anaphoric plural reference, not «ایشان» (which flags respect and is rare in academic prose except for religious-studies traditions).
10. Do not open a paragraph with «و» or with a demonstrative pronoun with no clear antecedent («این نشان میدهد …» — say what «این» is).
11. Avoid empty temporal adverbials in the intro: «امروزه، در عصر حاضر، در دنیای امروز» read as filler; use them only if the argument turns on the temporal claim.
12. Break the «مصدر مرکب پیاپی» chain — «به بررسی و ارزیابی و تحلیل و بازخوانی …» stacks four مصادر مرکب; two is the informal ceiling.

# Heading and Question Patterns

**Standard section headings (present in ≥90% of empirical articles):**
1. مقدمه
2. مبانی نظری / چارچوب نظری / پیشینه ی پژوهش
3. روش پژوهش / روش شناسی
4. یافته ها / یافته های پژوهش
5. بحث و نتیجه گیری
6. محدودیتها و پیشنهادها (some journals only)
7. منابع / کتابنامه

**Alternate structures used in humanities:**
- مقدمه — طرح مسأله — چارچوب مفهومی — تحلیل — نتیجه گیری
- مقدمه — بیان مسأله — سؤالات پژوهش — روش — یافته ها — تحلیل — نتیجه گیری

**Question patterns in "بیان مسأله":**
- «پرسش اصلی این پژوهش عبارت است از این که: چگونه X بر Y تأثیر میگذارد؟»
- «آیا میتوان X را Y نامید؟»
- «چرا X در Y روی داده است؟»
- «چه رابطه ای میان X و Y وجود دارد؟»
- «این پژوهش در پی پاسخ به این پرسش است که …»

**Sub-headings in linguistic/textual analysis:**
- «تحلیل داده ها»
- «مطالعه ی موردی»
- «جمع بندی»

# Anti-AI / Translationese Findings

**AI-tell #1 — Sweeping temporal opener.** "در دنیای امروز، با پیشرفت سریع فناوری …". Not seen in the corpus; a red flag.

**AI-tell #2 — Explicit meta-navigation.** "در این مقاله ابتدا به X، سپس به Y، و در نهایت به Z خواهیم پرداخت." Real Iranian abstracts state هدف and روش directly; only the introduction (not the abstract) uses "ساختار مقاله بدین شرح است". Overuse in abstracts is AI-flavored.

**AI-tell #3 — Symmetric triplets.** "این پژوهش نشان میدهد که X، Y و Z در توسعه ی A، B و C نقش دارند." Real Iranian abstracts have asymmetric noun phrases.

**AI-tell #4 — Universalising boosters.** "قطعاً، بی تردید، بدون شک، یکی از مهمترین ..." — Iranian academic writers hedge more than an LLM's default.

**AI-tell #5 — «کلیدی» adjective spam.** "این مفهوم کلیدی، این عامل کلیدی، این نکته ی کلیدی …" — in real articles, «کلیدی» is reserved for actual keywords and «مفهوم بنیادین / عامل تعیین کننده / نقطه ی محوری» carry the weight.

**Translationese-tell #1 — «توسط X، Y انجام شد».** Iranian editors (A-S10) prefer «به وسیله ی X» or, better, drop the agent and rephrase.

**Translationese-tell #2 — «داشتن یک نقش کلیدی» (calquing "playing a key role").** Natural Persian: «نقش تعیین کننده ای دارد / ایفا میکند».

**Translationese-tell #3 — «به عبارت دیگر، ما نیاز داریم به …».** «ما نیاز داریم» is calqued. Persian: «نیازمند X هستیم» or nominalise: «نیاز به X …».

**Translationese-tell #4 — «در حقیقت / در واقع» over-inserted.** Sparingly used in real academic Persian; every second sentence is a translation tell.

**Translationese-tell #5 — «این واقعیت که» (the fact that).** Persian rarely nominalises "the fact"; drop it and start with «که X …» or restate.

**Empty-formal-tell #1 — «انجام گرفت» + «صورت پذیرفت» in the same paragraph.** One "action of doing" verb is enough.

**Empty-formal-tell #2 — «مورد بحث و بررسی قرار گرفت».** Two nouns of the same category do the work of one; pick «بررسی شد» or «تحلیل شد».

**Empty-formal-tell #3 — Passive stacking with anonymous agent.** "بررسیها انجام شد، تحلیلها صورت پذیرفت، ارزیابیها به عمل آمد." Rephrase actively where possible.

# Constructed Before/After Examples

*(All Persian written without ZWNJ, per this file's rule.)*

**EX-1 — Opening a research problem**
- UNNATURAL_OR_WEAK: در این مقاله می خواهیم راجع به تأثیر شبکه های اجتماعی روی هویت جوانان یک بررسی کاملی انجام دهیم.
- BETTER_PERSIAN: پژوهش حاضر با هدف تحلیل تأثیر شبکه های اجتماعی بر برساخت هویت جوانان ایرانی انجام شده است.
- WHY: هدف روشن، فعل نهایی جمع و جور، «بررسی کاملی» و «راجع به» جای خود را به «تحلیل» و «بر» می دهد؛ «برساخت هویت» یک اصطلاح فنی است و خواننده ی متخصص را جلب میکند.

**EX-2 — Reporting a finding**
- UNNATURAL_OR_WEAK: نتایج ما ثابت کرد که این مسأله خیلی روی رفتار مشتری تأثیرگذار است.
- BETTER_PERSIAN: یافته های پژوهش نشان میدهد که X رابطه ای معنادار و مستقیم با رفتار خرید مشتریان دارد.
- WHY: «ثابت کرد» ادعای مطلق دارد؛ «نشان میدهد که» با شواهد سازگارتر است. «خیلی» گفتاری است؛ «معنادار» اصطلاح فنی است و مقدار را قابل بازبینی می کند.

**EX-3 — Nominalisation of the method**
- UNNATURAL_OR_WEAK: ما با ۲۰ نفر مصاحبه کردیم و بعدش داده ها را کد گذاری کردیم و آنالیز کردیم.
- BETTER_PERSIAN: داده ها از راه مصاحبه های نیمه ساختاریافته با ۲۰ مشارکت کننده گردآوری، و با روش کدگذاری موضوعی تحلیل شدند.
- WHY: زمان فعل به گذشته ی مجهول و بی فاعل، «بعدش» حذف، «آنالیز» به «تحلیل» — سبک متن پژوهشی می شود.

**EX-4 — Passive of «مورد» — when to keep, when to drop**
- UNNATURAL_OR_WEAK: این مسأله مورد بحث و بررسی و تحلیل قرار داده شد.
- BETTER_PERSIAN: این مسأله در پژوهش حاضر تحلیل شد.
- WHY: زنجیره ی مصدر مرکب «بحث و بررسی و تحلیل» توخالی است؛ یک فعل «تحلیل شد» کافی است. «قرار داده شد» به «شد» ساده کاسته می شود.

**EX-5 — Ezafe chain that has failed**
- UNNATURAL_OR_WEAK: بررسی ابعاد گوناگون رابطه ی میان مؤلفه های نظام آموزش عالی و شاخصهای توسعه ی پایدار در استانهای مرزی جنوب شرق کشور در دوره ی پس از انقلاب اسلامی.
- BETTER_PERSIAN: بررسی رابطه ی مؤلفه های آموزش عالی با شاخصهای توسعه ی پایدار؛ مطالعه ی موردی استانهای جنوب شرق کشور در دوران پس از انقلاب.
- WHY: زنجیره ی نه گانه ی اضافه به دو بند شکسته شد؛ «مطالعه ی موردی» جای «در استانها …» را می گیرد و بار معنایی را در ذهن خواننده مرتب می کند.

**EX-6 — Reporting-verb inventory**
- UNNATURAL_OR_WEAK: فوکو حرف میزند از این که قدرت همه جا هست و ما نمیتوانیم فرار کنیم از آن.
- BETTER_PERSIAN: فوکو (Foucault, 2002) استدلال میکند که قدرت در سراسر شبکه ی روابط اجتماعی جاری است و گریز از آن ممکن نیست.
- WHY: «حرف میزند» گفتاری است؛ «استدلال میکند» فعل گزارشی رسمی است. ارجاع درون متنی به سبک آکادمیک اضافه شد؛ «فرار کردن» به «گریز از آن» تغییر یافت.

**EX-7 — Hedge on a strong claim**
- UNNATURAL_OR_WEAK: قطعاً این مدل بهترین راه برای تحلیل داده هاست.
- BETTER_PERSIAN: به نظر می رسد این مدل با ماهیت داده های پژوهش حاضر بیشترین سازگاری را دارد.
- WHY: «قطعاً … بهترین» ادعای منحصر به فرد است؛ نویسنده ی حرفه ای مدعی سازگاری نسبی می شود و «به نظر می رسد» را می افزاید تا مرز فرضیه/تعیین را نگه دارد.

**EX-8 — Citation attribution**
- UNNATURAL_OR_WEAK: به گفته ی یکی از نظریه پردازان معروف، جامعه ی امروزی خیلی پیچیده است.
- BETTER_PERSIAN: به باور گیدنز (Giddens, 1990) جامعه ی مدرن متأخر با درجه ی بی سابقه ای از پیچیدگی روبروست.
- WHY: نام و مأخذ به جای «یکی از نظریه پردازان معروف»؛ اصطلاح فنی «مدرن متأخر» جایگزین «امروزی» می شود.

**EX-9 — Transitions**
- UNNATURAL_OR_WEAK: و در آخر، ما میخواهیم بگیم که خیلی مسائل مانده که باید در آینده کار شود.
- BETTER_PERSIAN: در نهایت، جنبه های متعددی از این موضوع همچنان نیازمند پژوهشهای مستقل و تکمیلی است.
- WHY: «و در آخر … ما میخواهیم بگیم» به «در نهایت» رسمی رسید؛ فعل نهایی به مصدر نیاز نداشت اما «نیازمند … است» ساخت رسمی است.

**EX-10 — Limitations paragraph**
- UNNATURAL_OR_WEAK: پژوهش ما یک سری محدودیت هایی داشت که مثلا نمونه اش کم بود و توی یک شهر انجام شد.
- BETTER_PERSIAN: از جمله محدودیتهای پژوهش حاضر می توان به کوچک بودن حجم نمونه و محدود بودن آن به یک شهر خاص اشاره کرد؛ از این رو تعمیم یافته ها باید با احتیاط انجام شود.
- WHY: قالب رایج «از جمله محدودیت ها می توان به … اشاره کرد» جایگزین گفتاری شد. هشدار تعمیم پذیری — عناصر ثابت این بند در متن آکادمیک ایرانی — اضافه شد.

**EX-11 — Question phrasing**
- UNNATURAL_OR_WEAK: می خواستیم بفهمیم آیا رابطه ای هست بین این دو چیز یا نه.
- BETTER_PERSIAN: پرسش اصلی پژوهش عبارت است از این که آیا میان X و Y رابطه ی معناداری وجود دارد.
- WHY: قالب «پرسش اصلی … عبارت است از این که» ساخت آکادمیک متعارف است؛ «معنادار» بار روش شناختی می افزاید.

**EX-12 — Persian equivalent vs loanword**
- UNNATURAL_OR_WEAK: در این پیپر ما یک متد کیفی با اپروچ کانستراکتیویست انتخاب کرده ایم برای انلایز دیتای اینترویو.
- BETTER_PERSIAN: در این مقاله روشی کیفی با رویکرد برساخت گرا برای تحلیل داده های حاصل از مصاحبه به کار گرفته شده است.
- WHY: چهار وامواژه بی جهت به معادلهای پذیرفته شده در پیکره ی مقالات ایرانی بر می گردند: پیپر→مقاله، متد→روش، اپروچ→رویکرد، انلایز→تحلیل، دیتا→داده، اینترویو→مصاحبه، کانستراکتیویست→برساخت گرا.

**EX-13 — Rule-of-three noun stacking**
- UNNATURAL_OR_WEAK: این پژوهش با هدف بررسی، تحلیل، ارزیابی، کاوش و مطالعه ی مؤلفه های X انجام شد.
- BETTER_PERSIAN: این پژوهش با هدف تحلیل مؤلفه های X انجام شد.
- WHY: پنج مصدر پیاپی حشو است؛ همه در عمل یک کار می کنند. یک فعل کاملاً کافی است.

**EX-14 — Anaphora**
- UNNATURAL_OR_WEAK: این خیلی مهم است و ما باید روی این بیشتر کار کنیم چون این نتایج ما را تغییر میدهد.
- BETTER_PERSIAN: این یافته دلالت مهمی برای پژوهشهای بعدی دارد، زیرا خط سیر تحلیل نتایج را دگرگون میکند.
- WHY: سه «این» بی مرجع به «این یافته» / «خط سیر تحلیل نتایج» تبدیل شد؛ «باید بیشتر کار کنیم» ← «دلالت مهمی برای پژوهشهای بعدی دارد».

**EX-15 — Second person elimination**
- UNNATURAL_OR_WEAK: اگر شما می خواهید این روش را استفاده کنید، باید اول نمونه ی خودتان را بزرگ کنید.
- BETTER_PERSIAN: به کارگیری این روش، مستلزم انتخاب نمونه ی نسبتاً بزرگ است.
- WHY: خطاب دوم شخص در نثر آکادمیک وجود ندارد؛ ساخت مصدری «به کارگیری … مستلزم …» جایگزین می شود.

**EX-16 — «می باشد» reduction**
- UNNATURAL_OR_WEAK: این متغیر شامل چهار مؤلفه می باشد که هر کدام دارای شاخصهای خاص خود می باشند.
- BETTER_PERSIAN: این متغیر چهار مؤلفه دارد و هر مؤلفه با شاخصهای معینی سنجیده می شود.
- WHY: دو «می باشد» و یک «دارای» به دو فعل تمیز و متفاوت («دارد»، «سنجیده می شود») تبدیل شدند.

**EX-17 — Anti-AI opener**
- UNNATURAL_OR_WEAK: در دنیای پرشتاب امروز، بی تردید یکی از مهمترین موضوعاتی که همواره مورد توجه پژوهشگران قرار داشته است، مسأله ی X می باشد.
- BETTER_PERSIAN: پژوهش حاضر مسأله ی X را از منظر Y بررسی می کند.
- WHY: بند «در دنیای پرشتاب امروز … می باشد» چهار نشانه ی نگارش هوش مصنوعی را در یک جمله جمع میکند: افتتاحیه ی زمانی سرتاسری، شمول ساز مطلق، «مورد … قرار داشته است»، «می باشد». همه حذف و جای خود را به یک جمله ی اصیل هدف می دهند.

**EX-18 — Discussion opener**
- UNNATURAL_OR_WEAK: نتایج ما با نتایج بعضی از تحقیقات قبلی یکی است و با بعضی هایشان نه.
- BETTER_PERSIAN: یافته های پژوهش حاضر با نتایج مطالعه ی X (نویسنده، سال) همسو، اما با یافته های Y (نویسنده، سال) ناهمسو است؛ این ناهمسویی را می توان به تفاوت زمینه ی نمونه گیری نسبت داد.
- WHY: بحث آکادمیک همراه با ارجاع مشخص و تفسیر تفاوت انجام می شود، نه اشاره ی مبهم به «تحقیقات قبلی».

**EX-19 — Overly literal translation of a technical claim**
- UNNATURAL_OR_WEAK: این مدل «بازی میکند یک نقش کلیدی» در پیش بینی رفتار.
- BETTER_PERSIAN: این مدل در پیش بینی رفتار نقشی تعیین کننده دارد.
- WHY: کالک انگلیسی «play a key role» به فارسی طبیعی «نقش تعیین کننده دارد / ایفا میکند» تبدیل می شود.

**EX-20 — Suggestion sentence**
- UNNATURAL_OR_WEAK: ما پیشنهاد میدهیم که در آینده کارهای بیشتری روی این موضوع بشود و شاید نمونه های بیشتری هم استفاده کنند.
- BETTER_PERSIAN: پیشنهاد می شود در پژوهشهای آتی، این موضوع در نمونه های بزرگتر و در بافتهای فرهنگی متفاوت بازآزمایی شود.
- WHY: قالب متعارف «پیشنهاد می شود که …» جایگزین «ما پیشنهاد میدهیم» شد؛ «کارهای بیشتری بشود» ← «بازآزمایی شود» با بار مفهومی روشن.

**EX-21 — Introducing a theoretical framework**
- UNNATURAL_OR_WEAK: چارچوب نظری این پژوهش بر اساس دیدگاه فوکوست که خیلی روی قدرت و دانش تأکید داشت.
- BETTER_PERSIAN: چارچوب نظری این پژوهش بر مفهوم قدرت/دانش در اندیشه ی میشل فوکو (Foucault, 1980) استوار است.
- WHY: «مفهوم قدرت/دانش» اصطلاح فنی است؛ ارجاع درون متنی به شیوه ی مرسوم آکادمیک ایرانی؛ «خیلی تأکید داشت» به «استوار است» رسمی می شود.

**EX-22 — Closing the abstract**
- UNNATURAL_OR_WEAK: در آخر، امیدواریم این کار به دیگران کمک کند.
- BETTER_PERSIAN: نتایج این پژوهش می تواند در تدوین سیاستهای فرهنگی هدفمند و طراحی پژوهشهای بعدی راهگشا باشد.
- WHY: «امیدواریم» جای خود را به قالب متعارف «نتایج این پژوهش می تواند … راهگشا باشد» می دهد؛ زمینه ی کاربرد نتایج نیز باید مشخص شود.

# Disagreements and Uncertainty

1. **«مورد + مصدر + قرار گرفت» — anti-pattern or norm?**
   The ویرایش-purism tradition (کتاب ابوالحسن نجفی، «غلط ننویسیم»؛ روش شناسی A-S10; general editing literature) treats «مورد بررسی قرار گرفت» as a Franco-Arabic calque and prescribes «بررسی شد». The empirical corpus, however, uses it constantly (A-S07, A-S15, A-S22, A-S30). Guidance: allow it, but flag its stacked form (EX-4). Do not eliminate; do not endorse.

2. **Loanword thresholds.**
   Editors at UT/IHCS journals still prefer Persian equivalents (معرفت شناسی over اپیستمولوژی, ارجاع over رفرنس). Management journals accept loanwords (فراترکیب, پارادایم) freely. There is no single Iranian norm; the writer's sub-register decides. Guidance: default to the Persian equivalent, add the Latin term in parentheses on first use.

3. **«می باشد» — always a defect?**
   Purists say yes; the empirical management corpus (A-S24) shows it is still normal. Guidance: prefer «است»؛ tolerate «می باشد» only where it disambiguates modality.

4. **Interrogative titles.**
   Rare (~5%) but attested (A-S05 uses a rhetorical dichotomy in the title). Guidance: prefer nominal titles; interrogative titles are acceptable when the article's central move is truly to answer a specific question.

5. **Sub-register variance in reporting-verb formality.**
   Historical writing accepts «تصریح میکند / اذعان دارد» more than psychology writing; psychology writing prefers «نشان داد که». Do not blend registers.

6. **Extended abstract (چکیده مبسوط).**
   Some journals require it; others require only the standard 200-word abstract. The bilingual English-Persian pairing has become a fixed norm since ~1395 in all وزارت علوم journals (evidence: A-S26–A-S29). Guidance: if writing content that mimics an Iranian journal artefact, include both forms; if writing web-facing academic-flavoured prose, mimic the standard abstract only.

7. **The ZWNJ question.**
   Every Iranian journal uses ZWNJ («می‌تواند»)؛ Teznevise forbids it. This is an artificial constraint imposed by the target site — it is NOT how academic Persian is written in the wild. When quoting or citing real Iranian titles, we normalise for our target; downstream skills must know that the ZWNJ-free rendering is a stylistic transformation, not a linguistic feature of academic Persian itself.

# Recommendations for the Master SKILL

The following are specific, machine-actionable rules a downstream writing agent should follow when producing academic-flavoured Persian for Teznevise:

**R-A-01 (structure)** — For any article that presents a specific finding or study, open with a single sentence stating هدف: «هدف [این مقاله / این نوشتار / این بررسی] X است» یا «این نوشتار به بررسی X می پردازد». No sweeping temporal opener, no rhetorical question as opener.

**R-A-02 (self-reference)** — Refer to the piece as «این مقاله»، «این نوشتار»، «این بررسی»، «پژوهش حاضر»، «نگارنده»، «نگارندگان». Never use «من / ما / شما / تو / ایشان». For an inclusive rhetorical move, use impersonal «می توان گفت که …».

**R-A-03 (verb tense discipline)** — Present indicative for general claims («نشان میدهد که»)؛ past passive for reports of specific studies («انجام گرفت»، «تحلیل شد»)؛ subjunctive for suggestions («پیشنهاد میشود که …»).

**R-A-04 (reporting-verb inventory)** — Draw from this whitelist: نشان میدهد، بیان میکند، مطرح میکند، تصریح میکند، تبیین میکند، استدلال میکند، معتقد است، بر آن است، به این نتیجه رسید، تأکید میکند، اشاره میکند، به باور … . Blacklist for academic register: میگه، حرف میزنه، اذعان کرد (except religious-studies).

**R-A-05 (hedge discipline)** — Every strong-claim clause with «قطعاً / بی تردید / بدون شک / همیشه / هرگز» must be re-checked. Prefer «به نظر می رسد که»، «می توان گفت که»، «تا حدی»، «چه بسا». Two hedges per short abstract is normal.

**R-A-06 (ezafe control)** — Break any ezafe chain at length 5. Prefer «مطالعه ی موردی X» over «پژوهشی درباره ی مسأله ی X در بافت Y در استان Z».

**R-A-07 (passive discipline)** — In methodology sentences use agentless past passive. Do not use «توسط + agent»؛ prefer «به دست», «از سوی», «به وسیله ی», or drop the agent.

**R-A-08 (nominalisation vs verbal style)** — Prefer nominalised abstract headers («تحلیل تأثیر X»)؛ prefer verbal style («X را تحلیل کرد») for methodology narration and result narration.

**R-A-09 (loanword handling)** — Default to established Persian equivalents. Allow loanwords in three cases: (a) proper nouns; (b) statistical/technical software names; (c) sub-register conventions (فراترکیب, پارادایم) — with Persian gloss on first mention.

**R-A-10 (connective inventory)** — Additive: افزون بر این / علاوه بر این / همچنین. Contrast: اما / با این حال / از سوی دیگر / بر خلاف. Consequence: بنابراین / از این رو / در نتیجه / لذا (formal-heavy). Reformulate: به عبارت دیگر / به بیان دیگر / یعنی. No stacking; one connective per sentence boundary.

**R-A-11 (numeric convention)** — Persian digits in body («۲۲۰ نفر»)؛ Latin digits for citation years and page numbers («Foucault, 2002, p. 45»).

**R-A-12 (citation format)** — In-text: (نام خانوادگی، سال: صفحه) for Persian sources, (Surname, year, p. X) for Latin. First mention of a foreign author: «فوکو (Foucault, 2002)».

**R-A-13 (quotation)** — Direct short quotations in «Persian guillemets»؛ never in "English straight quotes".

**R-A-14 (limitations)** — Include a محدودیت paragraph opened with «از جمله محدودیتهای این پژوهش می توان به … اشاره کرد».

**R-A-15 (suggestions)** — Close with «پیشنهاد می شود که …» — subjunctive, never «باید حتماً …».

**R-A-16 (empty-methods paragraph)** — Reject any methodology paragraph that reduces to «روش این پژوهش کیفی و از نوع توصیفی تحلیلی است». Force the writer to specify: (a) data source, (b) sampling logic, (c) analytic technique, (d) tool/software.

**R-A-17 (anti-inflation)** — Cap synonym stacks at 2 («بررسی و تحلیل» ok; «بررسی و تحلیل و ارزیابی و کاوش» rejected).

**R-A-18 (abstract-length rule)** — Standard: 175–250 words. If the container requires an extended abstract: 500–1000 words with sub-headings «هدف — روش — یافته ها — نتیجه». Below 100 or above 300 words for a standard abstract is off-register.

**R-A-19 (keywords)** — 5–7 noun-phrase keywords, ezafe-permitted, no adjectives-alone, no verbs. Order by conceptual importance, not alphabetically.

**R-A-20 (no ZWNJ)** — Because of the Teznevise constraint, all Persian compounds are rendered either fully-joined (میتوان، آنها، هم پایگی written as هم پایگی) or space-separated (می توان، آن ها). Follow one convention consistently within one artefact. The academic norm is ZWNJ, so downstream skills must know that our rendering is a lossy stylistic transformation, not a linguistic feature of academic Persian itself.

**R-A-21 (headings)** — For an empirical article, use: مقدمه — چارچوب نظری — روش پژوهش — یافته ها — بحث و نتیجه گیری — منابع. For a conceptual/humanities piece: مقدمه — طرح مسأله — تحلیل — نتیجه گیری. Do not invent Anglo-style separate "Discussion" and "Conclusion" sections.

**R-A-22 (reader address)** — Zero. The reader is not addressed; if addressed, only as «خواننده».

**R-A-23 (title patterns)** — Prefer «X: Y در Z» or «بررسی/تحلیل/واکاوی/مطالعه ی X». Question titles are a minority option; keep them for genuinely dichotomous claims.

**R-A-24 (anti-AI check)** — Before publishing, sweep the draft for: (i) sweeping temporal openers, (ii) symmetric noun triplets, (iii) «کلیدی» spam, (iv) «قطعاً / بی تردید» clusters, (v) «در دنیای امروز» / «در عصر حاضر»، (vi) meta-navigation clauses in an abstract («در ادامه به X، سپس Y، در نهایت Z»).

**R-A-25 (register-mixing check)** — If a piece is academic-facing, do not permit «شما»، «هست»، «-ه» endings, colloquial subjunctive, or bare English words. If any of these slips in, downgrade the register or rewrite the sentence.

# Machine-Readable Findings

```yaml
findings:
  - id: A-001
    category: rhythm
    rule: "Abstracts follow هدف→روش→یافته ها→نتیجه move order; opening sentence states purpose"
    applies_to: academic Persian, all disciplines
    confidence: high
    source_ids: [A-S02, A-S05, A-S08, A-S12, A-S13, A-S14, A-S18, A-S19, A-S24, A-S25]
    exceptions: pure-theory / interpretive philosophy may skip explicit روش

  - id: A-002
    category: reader_language
    rule: "Author self-reference is nominal (مقاله حاضر / پژوهش حاضر / نگارنده); no first-person singular; first-person plural rare"
    applies_to: all Iranian academic Persian
    confidence: high
    source_ids: [A-S05, A-S13, A-S14, A-S20, A-S22, A-S30]
    exceptions: reflective essays and some interpretive-sociology articles use ما

  - id: A-003
    category: syntax
    rule: "Methods section uses agentless past passive (انجام شد / تحلیل شد / گردآوری شد)"
    applies_to: empirical articles (qualitative and quantitative)
    confidence: high
    source_ids: [A-S13, A-S18, A-S19, A-S24, A-S25]
    exceptions: purely theoretical papers use present descriptive

  - id: A-004
    category: syntax
    rule: "Findings section uses present indicative for generalised claims (نشان میدهد / حاکی از … است)"
    applies_to: all disciplines
    confidence: high
    source_ids: [A-S05, A-S09, A-S12, A-S14, A-S18]
    exceptions: none

  - id: A-005
    category: lexicon
    rule: "Reporting-verb whitelist: نشان میدهد، بیان میکند، مطرح میکند، تصریح میکند، تبیین میکند، استدلال میکند، معتقد است، اشاره میکند، بر آن است، به این نتیجه رسید، به باور X"
    applies_to: all academic sub-registers
    confidence: high
    source_ids: [A-S05, A-S06, A-S10, A-S20, A-S30]
    exceptions: religious-studies articles use اذعان دارد / تصریح می فرماید

  - id: A-006
    category: syntax
    rule: "Ezafe chains of length 3-5 are natural; break at 5"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S05, A-S10, A-S20]
    exceptions: title conventions occasionally push to 6 with a break-colon

  - id: A-007
    category: syntax
    rule: "Prefer nominalised main clauses (به بررسی X می پردازد) over verbal (X را بررسی می کند) in headline sentences"
    applies_to: humanities and social sciences
    confidence: high
    source_ids: [A-S02, A-S05, A-S14, A-S22]
    exceptions: none

  - id: A-008
    category: syntax
    rule: "«مورد + N + قرار گرفت» passive is normal in current usage but should not stack; one passivisation per verb"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S07, A-S14, A-S15, A-S22, A-S30]
    exceptions: editorial-purism tradition rejects this construction — surface as a soft anti-pattern only

  - id: A-009
    category: syntax
    rule: "Passive is agentless; if agent named, use «به وسیله ی / از سوی / به دست» not «توسط»"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S10, A-S22]
    exceptions: legal writing tolerates توسط

  - id: A-010
    category: register
    rule: "Hedging is dense (به نظر میرسد / احتمالاً / می توان گفت / تا حدی)"
    applies_to: empirical articles, weaker in polemical/philosophical
    confidence: high
    source_ids: [A-S05, A-S07, A-S10, A-S22]
    exceptions: religious-doctrinal and strong-thesis philosophy tolerate boosters

  - id: A-011
    category: rhythm
    rule: "Discourse-connective inventory is fixed; no stacking of two consequence markers"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S02, A-S05, A-S10, A-S11, A-S12, A-S14, A-S15, A-S22, A-S30]
    exceptions: none

  - id: A-012
    category: register
    rule: "«لذا» is register-formal-heavy; default consequence marker is «بنابراین / از این رو»"
    applies_to: humanities articles
    confidence: medium
    source_ids: [A-S15, A-S10]
    exceptions: legal and management writing use لذا freely

  - id: A-013
    category: terminology
    rule: "Loanwords admissible only in three cases: proper nouns, tool/software names, sub-register-conventional terms (فراترکیب, پارادایم) with Persian gloss on first mention"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S13, A-S16, A-S17, A-S24, A-S25, A-S30]
    exceptions: linguistics is more tolerant of Latin transliterations

  - id: A-014
    category: terminology
    rule: "«گفتمان» has fully displaced discourse/discours; do not use دیسکورس"
    applies_to: all academic Persian since ~1380
    confidence: high
    source_ids: [A-S06, A-S07, A-S12]
    exceptions: none

  - id: A-015
    category: rhythm
    rule: "Titles are noun-phrase-plus-colon; interrogative titles are a minority"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S02, A-S05, A-S12, A-S20]
    exceptions: rhetorical-binary titles (A-S05) are attested

  - id: A-016
    category: terminology
    rule: "Case study is «مطالعه ی موردی» or «موردکاوی»; never «کیس استادی»"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S01, A-S12, A-S15, A-S30]
    exceptions: none

  - id: A-017
    category: rhythm
    rule: "Persian standard abstract: 175-250 words; extended abstract: 500-1000 words"
    applies_to: journal articles conforming to وزارت علوم norms
    confidence: high
    source_ids: [A-S26, A-S28, A-S29, A-S09]
    exceptions: some journals cap at 150

  - id: A-018
    category: terminology
    rule: "Keywords are 5-7 noun-phrase items, no adjectives-alone, no verbs"
    applies_to: all academic Persian articles
    confidence: high
    source_ids: [A-S05, A-S12, A-S13, A-S22, A-S29]
    exceptions: none

  - id: A-019
    category: syntax
    rule: "In-text citation is (نام، سال: صفحه) for Persian, (Surname, year, p.X) for Latin"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S06, A-S07, A-S30]
    exceptions: house-style variants exist

  - id: A-020
    category: rhythm
    rule: "Bibliographies split منابع فارسی / منابع لاتین"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S04, A-S06, A-S07]
    exceptions: single-language journals

  - id: A-021
    category: rhythm
    rule: "Sentence length in academic Persian is 30-60 words; extreme sentences up to 90 words attested"
    applies_to: humanities and social sciences
    confidence: high
    source_ids: [A-S11, A-S14, A-S22]
    exceptions: methodology sentences shorten to 12-20 words

  - id: A-022
    category: syntax
    rule: "«که»-clause stacking (up to three levels) is normal but not decorative; each که must carry information"
    applies_to: high-formal humanities and empirical psychology
    confidence: high
    source_ids: [A-S05, A-S18]
    exceptions: none

  - id: A-023
    category: reader_language
    rule: "No second-person address (شما/تو); reader referred to as «خواننده» when at all"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S05, A-S13, A-S18, A-S24]
    exceptions: none

  - id: A-024
    category: rhythm
    rule: "Rhetorical question is sparingly used and only as sub-section opener, not page-title"
    applies_to: all academic Persian
    confidence: medium
    source_ids: [A-S05, A-S07, A-S11]
    exceptions: philosophy essays open with the question

  - id: A-025
    category: rhythm
    rule: "Research questions numbered, indirect, opened with آیا/چه/چگونه/چرا"
    applies_to: empirical articles
    confidence: high
    source_ids: [A-S18, A-S24, A-S25]
    exceptions: none

  - id: A-026
    category: rhythm
    rule: "Limitations paragraph formulaic: «از جمله محدودیتهای پژوهش حاضر می توان به …»"
    applies_to: empirical articles
    confidence: high
    source_ids: [A-S18, A-S24, A-S25]
    exceptions: humanities/history articles skip this section

  - id: A-027
    category: rhythm
    rule: "Suggestions closing paragraph: «پیشنهاد می شود که …»"
    applies_to: empirical articles
    confidence: high
    source_ids: [A-S18, A-S24, A-S25]
    exceptions: none

  - id: A-028
    category: lexicon
    rule: "«پژوهش» outnumbers «تحقیق» in current humanities/social sciences; «مطالعه» in psychology/health"
    applies_to: post-1390 Iranian academic Persian
    confidence: high
    source_ids: [A-S09, A-S13, A-S18]
    exceptions: law and older articles retain تحقیق

  - id: A-029
    category: anti_ai
    rule: "«می باشد» in place of «است» flagged as translationese by editors but still frequent in management writing"
    applies_to: all academic Persian; especially watch management sub-register
    confidence: medium
    source_ids: [A-S10, A-S24]
    exceptions: none

  - id: A-030
    category: lexicon
    rule: "Action-verbs for methods, ranked by formality: صورت پذیرفت > انجام گرفت > انجام شد > صورت گرفت"
    applies_to: methodology sections
    confidence: medium
    source_ids: [A-S13, A-S15, A-S18, A-S19, A-S24]
    exceptions: none

  - id: A-031
    category: register
    rule: "Author-guideline language (باید / الزامی است / موظف است) is a distinct register; do not import into article prose"
    applies_to: prose composition
    confidence: high
    source_ids: [A-S26, A-S27, A-S28, A-S29]
    exceptions: none

  - id: A-032
    category: syntax
    rule: "«گردیدن» is a formal alternative to «شدن»; overuse is a stylistic warning"
    applies_to: academic Persian
    confidence: medium
    source_ids: [A-S18, A-S26, A-S10]
    exceptions: guidelines and normative texts use it freely

  - id: A-033
    category: syntax
    rule: "Direct quotes in «Persian guillemets»; not straight quotes"
    applies_to: all Persian academic writing
    confidence: high
    source_ids: [A-S05, A-S07, A-S12]
    exceptions: none

  - id: A-034
    category: syntax
    rule: "Native academic norm uses ZWNJ; a downstream artefact forbidden from using ZWNJ must render compounds joined or space-separated consistently"
    applies_to: this project only
    confidence: high
    source_ids: [all source articles in corpus]
    exceptions: this is a target-site convention, not a Persian feature

  - id: A-035
    category: syntax
    rule: "Persian digits in body prose; Latin digits for citation years and DOIs"
    applies_to: all Iranian academic Persian
    confidence: high
    source_ids: [A-S18, A-S24]
    exceptions: journal-specific house styles

  - id: A-036
    category: reader_language
    rule: "Foreign author names: Persian transliteration first, Latin in parentheses on first mention"
    applies_to: humanities and social sciences
    confidence: high
    source_ids: [A-S04, A-S06, A-S07, A-S30]
    exceptions: linguistics may keep Latin inline

  - id: A-037
    category: terminology
    rule: "«X-محور / X-گرا / X-مدار» are productive academic modifiers; free to coin"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S07, A-S09, A-S16, A-S30]
    exceptions: none

  - id: A-038
    category: terminology
    rule: "Prefixes شبه / فرا / پسا / پیشا / ضد / هم productive; write joined when no ZWNJ available"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S16, A-S24]
    exceptions: none

  - id: A-039
    category: anti_ai
    rule: "«فربهی/آماس» anti-patterns: کولاژ, تکثیر ناموجه منابع, تکه نویسی, مقدمه چینی افراطی, gap-claim without demonstration, absent research problem, mere topic declaration"
    applies_to: any academic Persian draft
    confidence: high
    source_ids: [A-S10, A-S20]
    exceptions: none

  - id: A-040
    category: anti_ai
    rule: "Translationese calques to avoid or minimise: بازی کردن نقش، در تلاش برای X بودن، به نوبه ی خود، داشتن یک X، توسط, «مورد استفاده قرار گرفت» stacking"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S10, A-S20]
    exceptions: some have been fully naturalised (e.g. «به نوبه ی خود») but keep them rare

  - id: A-041
    category: anti_ai
    rule: "AI-tell: sweeping temporal opener (در دنیای امروز / در عصر حاضر / بی تردید) is never present in Iranian abstracts"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S02, A-S05, A-S12, A-S13, A-S14, A-S18, A-S24 — negative evidence]
    exceptions: some popular-science pieces open this way; academic articles do not

  - id: A-042
    category: anti_ai
    rule: "Rule-of-three synonym stacking (بررسی، تحلیل، ارزیابی، کاوش…) is inflated writing"
    applies_to: all academic Persian
    confidence: medium
    source_ids: [A-S10]
    exceptions: coordinations of three DIFFERENT things (مقدمه، بحث، نتیجه) are fine

  - id: A-043
    category: anti_ai
    rule: "Empty methodology paragraph (بدون data source, sampling, tool) is a canonical defect"
    applies_to: empirical articles
    confidence: high
    source_ids: [A-S10, A-S20]
    exceptions: none

  - id: A-044
    category: reader_language
    rule: "The reader is خواننده / پژوهشگر / مخاطب علمی; never شما / کاربران / دوستان"
    applies_to: all academic Persian
    confidence: high
    source_ids: [all corpus articles]
    exceptions: none

  - id: A-045
    category: syntax
    rule: "Modality of obligation: باید / بایستی / لازم است / ضرورت دارد; hedged: «به نظر می رسد که باید …»"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S10, A-S20, A-S30]
    exceptions: none

  - id: A-046
    category: syntax
    rule: "Verb-final SOV order strictly maintained in academic register; no journalistic verb-fronting"
    applies_to: all academic Persian
    confidence: high
    source_ids: [all corpus articles]
    exceptions: rare topicalisation for emphasis

  - id: A-047
    category: anti_ai
    rule: "Prefer «است» over «می باشد» unless disambiguating tense/aspect"
    applies_to: all academic Persian
    confidence: medium
    source_ids: [A-S10, A-S24]
    exceptions: management/HR articles still frequently use می باشد

  - id: A-048
    category: rhythm
    rule: "Article-final sentence pattern: (a) به این ترتیب / بدین سان …; (b) در نهایت …; (c) نتایج این پژوهش می تواند … راهگشا باشد"
    applies_to: all academic Persian
    confidence: high
    source_ids: [A-S13, A-S14, A-S18, A-S24]
    exceptions: none

  - id: A-049
    category: rhythm
    rule: "Hedged value claim closes the abstract: «نتایج … می تواند در … راهگشا / سودمند / یاری رسان باشد»"
    applies_to: empirical articles
    confidence: high
    source_ids: [A-S18, A-S24]
    exceptions: theoretical articles omit this

  - id: A-050
    category: rhythm
    rule: "Iranian journals combine Discussion and Conclusion in a single «بحث و نتیجه گیری» section"
    applies_to: empirical articles
    confidence: high
    source_ids: [A-S13, A-S18, A-S19, A-S24, A-S25]
    exceptions: rare exceptions in linguistics and philosophy
```
