# UX Writing & Landing-Page Persian — `fa-IR`

Status: canonical overlay for product UI, forms, dashboards, landing pages, booking/payment flows, tools and conversion surfaces.

## 1. Locale contract

Target **Iranian Persian (`fa-IR`)**, not generic `fa` and not Dari/Afghan Persian (`fa-AF`).

This is a locale requirement, not a judgement about either variety. When a product serves Iran, the copy must sound native to users in Iran.

Hard rules:

- use Iranian product vocabulary actually recognised by Iranian users;
- use Persian `ک` U+06A9 and `ی` U+06CC;
- use Persian digits U+06F0..U+06F9 in ordinary Persian UI unless a technical convention requires Latin;
- use Iranian date/currency/address conventions defined by the product; never silently import `fa-AF` calendar/month conventions;
- if a term is strongly associated with `fa-AF`/Dari and lacks evidence of normal Iranian product usage, reject it or replace it;
- do not over-purify vocabulary. Familiar Iranian terms beat dictionary novelty (`ایمیل`, `حساب کاربری`, `پیامک`, `رمز عبور`).

For Teznevise only, the existing no-U+200C rule still overrides general Persian orthography.

## 2. UX copy is interface design

A UI string has a job. Before writing it, identify:

1. state: what just happened?
2. user goal: what are they trying to do?
3. decision: what must they understand now?
4. action: what can they do next?
5. risk: what can go wrong or cost them money/data/time?

Do not write decorative sentences into the interface.

## 3. Product vocabulary lock (`fa-IR` defaults)

Prefer familiar terms and keep them stable across the product:

- User → `کاربر`
- Account/Profile (general) → `حساب کاربری`
- Sign up → `ثبت نام` / `عضویت` when the product concept is membership
- Log in → `ورود`
- Mobile number → `شماره موبایل` / `شماره تلفن همراه`
- Email → `ایمیل`
- SMS → `پیامک`
- OTP → `کد تایید` (or `رمز یک بار مصرف` only when that distinction matters)
- Password → `رمز عبور`
- Search → `جستجو`
- Settings → `تنظیمات`
- Notification → `اعلان` / `اعلان ها` unless the product vocabulary has a tested alternative
- Save → `ذخیره`
- Edit → `ویرایش`
- Delete → `حذف`
- Cancel → `لغو` / `انصراف` according to the flow; pick one meaning and keep it
- Back → `بازگشت`
- Continue → use the next real action when possible; otherwise `ادامه`
- Order → `سفارش` / plural `سفارش ها`, not `سفارشات`
- Cart → `سبد خرید`
- Price → `قیمت` for item value; `مبلغ` for payable/paid amount; `هزینه` for expense/service cost
- Support → `پشتیبانی`
- Address → `نشانی` or `آدرس` according to observed product language; do not rotate both casually

Do not use unfamiliar “pure Persian” replacements simply to avoid a loanword. Test comprehension.

## 4. Buttons and links

Button text should predict the result.

Prefer action + object when ambiguity exists:

- `ثبت سفارش`
- `ارسال پیام`
- `ذخیره تغییرات`
- `دریافت فایل`
- `پرداخت هزینه ویزیت`
- `رزرو نوبت`

Avoid generic `تایید`, `ارسال`, `ادامه`, `بزنید` when the user cannot predict what happens next.

Destructive action buttons must name the destructive action (`حذف حساب`) rather than `بله`.

Link text must describe the destination; avoid `اینجا کلیک کنید`.

## 5. Forms

- label names the information, not the instruction: `شماره موبایل`, not `شماره موبایل خود را وارد کنید`;
- placeholder is an example or format hint, not the only label;
- helper text explains a constraint before failure when practical;
- required/optional meaning must be explicit and consistent;
- do not expose backend concepts such as UUID, endpoint, CRM field name, API code or raw provider errors;
- for multi-step flows, show meaningful progress and what comes next.

## 6. Errors

Error formula:

**what happened → why (if known/useful) → how to recover**

Good:
`فرمت فایل پشتیبانی نمی شود. فایل JPG یا PNG بارگذاری کنید.`

Bad:
`خطا 403` / `عملیات ناموفق بود` / `شما اطلاعات را اشتباه وارد کرده اید`.

Rules:

- never blame the user;
- place the error where the user can act on it;
- do not hide specific recoverable errors behind `مشکلی پیش آمد`;
- never promise success if the system cannot guarantee it;
- preserve entered data after recoverable failure where technically possible.

## 7. Success, loading, empty and offline states

Success message says what changed and what happens next:
`نوبت شما ثبت شد. جزئیات برایتان پیامک می شود.`

Loading says what is happening only when the wait is perceptible:
`در حال بررسی پرداخت…`

Empty state explains why the area is empty and offers a useful next action:
`هنوز سفارشی ندارید.` + `مشاهده خدمات`

Offline/system failure separates user action from system condition:
`ارتباط با سرور برقرار نشد. اتصال اینترنت را بررسی کنید و دوباره تلاش کنید.`

Do not make jokes in high-stress states (payment failure, medical booking, data loss).

## 8. Confirmation and irreversible actions

Confirmation dialogs are for meaningful risk, not every click.

They should state consequence, not merely ask “مطمئن هستید؟”.

Pattern:

- Title: `این فایل حذف شود؟`
- Body: `بعد از حذف، امکان بازیابی این فایل وجود ندارد.`
- Primary destructive action: `حذف فایل`
- Safe action: `انصراف`

## 9. Trust microcopy

Trust comes from precise operational information:

- what will happen;
- what will be charged;
- what data is required and why;
- whether an action is reversible;
- when the next update arrives;
- what the service does **not** guarantee.

Avoid trust theatre:
`کاملا امن`, `صددرصد محرمانه`, `بهترین`, `بدون ریسک` unless the claim is literally supportable and scoped.

## 10. Landing pages

A landing page is neither an academic article nor a wall of sales adjectives.

Default above-the-fold sequence:

1. **Situation/outcome headline** — what useful change is offered?
2. **Mechanism/scope subhead** — what exactly happens, for whom, and under what boundary?
3. **Primary CTA** — next real action.
4. **Proof/trust cue** — concrete evidence, process, case/data, or constraint; never fabricated social proof.

Then resolve objections in the order users encounter them:

- Is this for me?
- What exactly do I get?
- How does it work?
- What do you need from me?
- How long / how much / what constraints?
- What evidence supports this?
- What can go wrong / what is not promised?
- What should I do next?

Do not force `ویژگی ها → مزایا → چرا ما → نظرات → سوالات متداول` on every page.

### Headline rules

Prefer specific outcome/problem language.

Avoid:

- `راهکاری نوین برای…`
- `تجربه ای متفاوت از…`
- `قدرت هوش مصنوعی در دستان شما`
- `آینده همین امروز است`
- `جامع، هوشمند و یکپارچه`

A headline should still make sense when the brand logo is hidden.

### Benefits and features

Feature = what the product/service has.
Benefit = what changes for the user.
Mechanism = why that change is plausible.

Strong landing copy often needs all three, not feature-to-benefit synonym replacement.

### CTA rhythm

Use one primary action per decision zone. Secondary CTA is allowed when it answers a different readiness state (`نمونه را ببینید`, `ابتدا شرایط را بررسی کنید`).

Do not repeat `همین حالا شروع کنید` after every section.

## 11. Navigation and information architecture language

Use nouns for destinations and verbs for actions.

- destination: `خدمات`, `مقالات`, `دانلودها`, `حساب کاربری`
- action: `رزرو نوبت`, `ارسال درخواست`, `دریافت فایل`

Do not invent creative menu labels that make the user guess.

## 12. Tone by state

- normal browsing: calm, direct, warm if brand allows;
- onboarding: encouraging, low-pressure, one decision at a time;
- payment/security: precise and restrained;
- error: non-blaming and actionable;
- medical/legal/high-stakes: factual, calm, no jokes;
- success: concise, confirm state, next step;
- destructive action: explicit consequence, no euphemism.

## 13. Accessibility and scanning

- put the distinguishing word early;
- do not rely on colour or icon alone to convey meaning;
- buttons/links need meaningful text;
- avoid double negatives;
- keep critical instructions visible, not only in placeholders/tooltips;
- expose status text to assistive technologies in implementation;
- use progressive disclosure for secondary detail, not for essential constraints.

## 14. UX QA metrics

Where data exists, judge copy with behaviour, not preference:

- form completion rate;
- field error rate;
- CTA completion, not click alone;
- abandonment by step;
- support contacts for the same confusion;
- recovery after error;
- time to complete task;
- search refinements / zero-result searches;
- usability-test hesitation or misinterpretation.

A/B testing is useful only when both variants are ethically and factually acceptable.

## 15. `fa-IR` locale QA

Before shipping Persian product copy:

- [ ] Locale explicitly targets Iran (`fa-IR`) when architecture supports locale tags.
- [ ] Vocabulary matches contemporary Iranian product language.
- [ ] No unreviewed Dari/fa-AF-localised labels, calendar terms or institutional words leaked in through translation.
- [ ] Persian `ک`/`ی` are correct.
- [ ] Digit, date, currency and phone formats match the product's Iranian convention.
- [ ] Terminology is consistent across navigation, form, error, success and help surfaces.
- [ ] Copy was reviewed inside the actual UI, not only in a document.

## 16. Sources and evidence level

Primary/standards:
- Unicode CLDR Persian style guide; locale data distinguishes `fa`/Iranian Persian and `fa_AF`/Dari and specifies Iranian Persian characters/digits/locale conventions.
- Persian Computing community / FarsiWeb lineage for `fa-IR` computing conventions.

Iranian practitioner evidence:
- Persian-vocabulary-in-UXwriting (community/practitioner vocabulary; useful as observed product-language evidence, not linguistic law).
- Iranian UX-writing articles (Faradars, Deer Agency, Rasam and others) converge on clarity, concision, consistency, actionability, non-blaming error copy, form guidance and testing.

Rules derived from practitioner sources are product-writing conventions, not universal grammar rules. Where a product's tested vocabulary conflicts with a glossary, tested user comprehension wins.
