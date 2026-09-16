# fa-IR Product Lexicon — baseline

Version: 1.0
Date: 2026-09-15
Scope: Iran-targeted UI, forms, service pages, landing pages and product microcopy.

This is a **product-language baseline**, not a universal Persian dictionary. Site-approved terminology and user-tested comprehension override it. A word is not “bad Persian” merely because it is common in Dari; the only question here is whether the wording fits the intended Iranian product audience and the specific interface.

The mutable operational copy of this lexicon lives in the Content Factory sheet `fa-IR Product Lexicon`. This file is the versioned source-control baseline.

## Core choices

| Concept | Preferred fa-IR | Allowed/contextual | Avoid or review |
|---|---|---|---|
| User account | حساب کاربری | پروفایل only for the profile/details surface | unfamiliar administrative coinages |
| Email | ایمیل | رایانامه only if an existing product deliberately uses it | novelty for purity alone |
| SMS | پیامک | SMS when the technology name matters | obscure translation in general UI |
| Password | رمز عبور | گذرواژه only if established product-wide | inconsistent rotation |
| One-time code | کد تایید | رمز یک بار مصرف when the security distinction matters | bare `OTP` for general users |
| Mobile number | شماره موبایل | شماره تلفن همراه | unvalidated locale-specific alternatives |
| Sign in | ورود | ورود به حساب | verbose formal labels |
| Sign up | ثبت نام | عضویت when the product truly models membership | mixing both without semantic reason |
| Search | جستجو | an established house spelling | inconsistent spellings |
| Settings | تنظیمات | — | creative labels that hide the destination |
| Notification | اعلان | اطلاع رسانی when describing the broader process | untested obscure equivalents |
| Save | ذخیره تغییرات | ذخیره when the object is obvious | تایید when the real outcome is saving |
| Delete | حذف + object | حذف when the object is obvious | بله as a destructive action label |
| Cancel | لغو | انصراف when leaving a process | random switching for the same action |
| Continue | name the next action | ادامه only when the next state is obvious | generic ادامه where the consequence is unclear |
| Order | سفارش / سفارش ها | — | سفارشات in ordinary product copy |
| Item value | قیمت | — | مبلغ/هزینه when the concept is item price |
| Payable/paid value | مبلغ | — | قیمت when the concept is total payable amount |
| Expense/service cost | هزینه | — | قیمت when the concept is cost of service/expense |
| Support | پشتیبانی | — | opaque creative navigation labels |
| Address | آدرس | نشانی if established by the product/formality level | inconsistent switching |

## CTA rule

On complex or review-gated flows, prefer the actual next action over generic labels.

Examples:
- `ارسال برای بررسی اولیه`
- `بررسی داده و مسیر تحلیل`
- `بررسی پروژه و مسیر کار`
- `ثبت درخواست بررسی آماری`

Use generic `ارسال درخواست`, `تایید`, `ادامه`, or `شروع` only when they accurately describe what happens next.

## Trust-language guard

Prefer operational facts, boundaries and process clarity over unsupported absolutes.

Review or reject unless explicitly supportable and scoped:
- `تضمینی`
- `صددرصد`
- `کاملا امن`
- `بهترین`
- `بدون ریسک`

## House-style avoid list

These are editorial preferences, **not grammar bans**:
- `در دنیای امروز` → usually start with the user problem/situation instead.
- `لازم به ذکر است` → usually state the point directly.
- `می باشد` → in product/service copy usually prefer a natural verb (`است`, `می شود`, etc.).

The corpus evidence behind these preferences is recorded in Art of Writing Bible v1.3/v1.4; do not turn them into universal Persian rules.

## Locale-leakage guard

For Iran-targeted surfaces, mark an unseen term for review when it appears to come from a different locale pack—especially:
- institutional/education terminology;
- calendar/date terminology;
- payment/banking terminology;
- government/administrative terminology;
- product navigation or form vocabulary.

Do **not** auto-replace a term just because it is also used in `fa-AF`/Dari. Shared natural Persian vocabulary is valid. Review is required only when the wording may feel foreign, ambiguous or mismatched for users in Iran.

## Character and orthography policy

General Iran-targeted Persian:
- use Persian `ک` (U+06A9) and `ی` (U+06CC);
- use product-consistent digits/date/currency formatting;
- apply normal Persian orthography unless a site rule overrides it.

Teznevise override:
- Persian user-facing output must contain **0 U+200C ZWNJ**;
- use the site's space-separated form even where general Persian normally uses half-space.

## Precedence

`current user instruction → current site/product policy → tested/approved product terminology → this lexicon baseline → generic model preference`

Unknown locale-sensitive wording should be marked `REVIEW_REQUIRED`, not silently rewritten.
