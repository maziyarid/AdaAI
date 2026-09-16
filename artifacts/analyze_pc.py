#!/usr/bin/env python3
"""Classify PhilosophyCafe posts and extract analysis samples."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

IN = Path("/workspace/artifacts/philosophycafe_posts.jsonl")
OUT_DIR = Path("/workspace/artifacts/pc_analysis")
OUT_DIR.mkdir(parents=True, exist_ok=True)

posts = [json.loads(l) for l in IN.read_text(encoding="utf-8").splitlines() if l.strip()]

# ---------- helpers ----------
CONTRIB_SIGS = {
    "omid_naderi": [
        r"#امید_نادری",
        r"امید نادری",
        r"@NaderiOmid66",
        r"Omid Naderi",
    ],
    "ali_soltanzadeh": [
        r"#علی_سلطان‌?زاده",
        r"علی سلطان‌?زاده",
        r"@Ali_soltanzadeh",
        r"علی سلطان زاده",
        r"نقد و نظر",
    ],
    "arman_khademi": [
        r"#آرمان_خادمی",
        r"آرمان خادمی",
        r"@khadem_ar",
        r"Arman Khademi",
        r"خادم",
    ],
    "tavassoli": [
        r"#توسلی",
        r"@M_H_Tavassoli",
        r"توسلی",
    ],
    "amirali": [
        r"@AmiraliEbrahimzadeh",
        r"امیرعلی ابراهیم",
        r"#امیرعلی",
    ],
    "amin": [
        r"@Amin_sbu",
        r"#امین",
    ],
}

QUOTE_MARKERS = [
    r"^«",
    r"چنین گفت",
    r"می‌گوید:",
    r"گفت:",
    r"— ",
    r"― ",
    r"―",
    r"Nietzsche",
    r"نیچه",
    r"#جملات_قصار",
    r"#نقل_قول",
    r"#quote",
    r"Wittgenstein,",
    r"Heidegger",
    r"هایدگر",
]

PROMO = [
    r"ثبت.?نام",
    r"برای عضویت",
    r"کانال",
    r"لینک گروه",
    r"کلاس ",
    r"کارگاه",
    r"تخفیف",
]

HASHTAG_RE = re.compile(r"#[\w\u0600-\u06FF_]+")
LATIN_RE = re.compile(r"[A-Za-z]{3,}")
QUESTION_RE = re.compile(r"[؟?]")
COLLOQ_RE = re.compile(r"(می‌کنه|می کنه|می‌شه|می شه|دیگه|چطور|اینه|اون|رو |نمی‌دونم|نمی دونم|یه |چی |چرا؟|خب |حالا )")
FIRST_PERSON = re.compile(r"(^|\s)(من |به نظرم|فکر می‌کنم|فکر میکنم|برای من|منظورم|احساس می‌کنم|اگر بخواهم|ما )")
HEDGE = re.compile(r"(به نظر می‌رسد|به نظرم|شاید|احتمالاً|ممکن است|تا حدی|ظاهراً|چه بسا|گویی|بعید)")
CONTRAST = re.compile(r"(اما |ولی |با این حال|از سوی دیگر|در حالی که)")
REFORM = re.compile(r"(به عبارت دیگر|به بیان دیگر|یعنی |منظور این است|به‌بیان ساده‌تر|به بیان ساده‌تر)")
ANALOGY = re.compile(r"(مثل |مانند |فرض کنید|تصور کنید|شبیه |انگار )")


def classify(p: dict) -> str:
    t = p.get("text") or ""
    tl = t.strip()
    if not tl:
        return "MEDIA_ONLY"
    if re.search(r"^https?://\S+$", tl):
        return "LINK_ONLY"
    if any(re.search(x, tl) for x in PROMO) and len(tl) < 280:
        return "PROMOTIONAL"
    # quotations / translations
    if re.search(r"#جملات_قصار|#نقل_قول|#شعر|#بیت", tl):
        return "PERSIAN_BOOK_QUOTATION" if re.search(r"[آ-ی]", tl) else "TRANSLATED_QUOTATION"
    if re.search(r"مترجم|ترجمه[:：]|ترجمه از", tl) and len(tl) > 80:
        if re.search(r"(تحلیل|توضیح|نقد|به نظر|می‌توان گفت)", tl):
            return "ORIGINAL_REVIEW"
        return "TRANSLATED_QUOTATION"
    # short quote-like
    if len(tl) < 180 and (tl.startswith("«") or "―" in tl or "—" in tl) and not re.search(r"(اما|یعنی|به نظر)", tl):
        return "TRANSLATED_QUOTATION"
    # classical
    if re.search(r"(سعدی|حافظ|مولانا|عطار|ابن عربی|ابن‌عربی|بیدل)", tl) and len(tl) < 400 and not re.search(r"(توضیح|یعنی|اما مسئله)", tl):
        return "CLASSICAL_PERSIAN"
    # questions
    if QUESTION_RE.search(tl) and len(tl) < 220 and tl.count("\n") < 4:
        return "ORIGINAL_QUESTION"
    # original long explanatory
    if len(tl) > 350:
        if re.search(r"(اما|یعنی|به بیان|مسئله این|پرسش این|فرض کنید|مثال)", tl):
            return "ORIGINAL_EXPLANATORY"
        if re.search(r"(استدلال|نقد|مخالف|بر خلاف|می‌توان نشان)", tl):
            return "ORIGINAL_ARGUMENTATIVE"
        return "ORIGINAL_EXPLANATORY"
    if len(tl) > 120:
        if re.search(r"(به نظرم|فکر می‌کنم|برای من)", tl):
            return "ORIGINAL_REFLECTIVE"
        if COLLOQ_RE.search(tl):
            return "ORIGINAL_CONVERSATIONAL"
        return "ORIGINAL_EXPLANATORY"
    if COLLOQ_RE.search(tl):
        return "ORIGINAL_CONVERSATIONAL"
    return "UNKNOWN_PROVENANCE"


def contributor(p: dict) -> str:
    t = p.get("text") or ""
    for name, pats in CONTRIB_SIGS.items():
        for pat in pats:
            if re.search(pat, t, re.I):
                return name
    return "unsigned"


def year(p: dict) -> str:
    d = p.get("datetime") or ""
    return d[:4] if d else "unk"


# classify
for p in posts:
    p["provenance"] = classify(p)
    p["contributor"] = contributor(p)
    p["year"] = year(p)
    p["chars"] = len(p.get("text") or "")
    p["questions"] = len(QUESTION_RE.findall(p.get("text") or ""))
    t = p.get("text") or ""
    p["has_colloq"] = bool(COLLOQ_RE.search(t))
    p["has_hedge"] = bool(HEDGE.search(t))
    p["has_contrast"] = bool(CONTRAST.search(t))
    p["has_reform"] = bool(REFORM.search(t))
    p["has_analogy"] = bool(ANALOGY.search(t))
    p["has_first"] = bool(FIRST_PERSON.search(t))
    p["hashtags"] = HASHTAG_RE.findall(t)

prov = Counter(p["provenance"] for p in posts)
years = Counter(p["year"] for p in posts)
contrib = Counter(p["contributor"] for p in posts)

original_kinds = {
    "ORIGINAL_EXPLANATORY",
    "ORIGINAL_ARGUMENTATIVE",
    "ORIGINAL_CONVERSATIONAL",
    "ORIGINAL_REFLECTIVE",
    "ORIGINAL_REVIEW",
    "ORIGINAL_QUESTION",
}
originals = [p for p in posts if p["provenance"] in original_kinds and p["chars"] > 80]

# high value: long original, not just quotes
high = sorted(
    [p for p in originals if p["chars"] > 280],
    key=lambda x: -x["chars"],
)

# save samples per year
by_year = defaultdict(list)
for p in high:
    by_year[p["year"]].append(p)

samples = []
for y in sorted(by_year):
    # take up to 12 longest original per year
    samples.extend(by_year[y][:12])

# also add conversational/register-mixed shorter ones
conv = [p for p in originals if p["has_colloq"] and p["chars"] > 150]
samples.extend(conv[:40])

# unique
seen = set()
uniq_samples = []
for p in samples:
    if p["id"] in seen:
        continue
    seen.add(p["id"])
    uniq_samples.append(p)

# save
(OUT_DIR / "summary.json").write_text(
    json.dumps(
        {
            "total": len(posts),
            "original_count": len(originals),
            "high_value_count": len(high),
            "provenance": dict(prov),
            "years": dict(sorted(years.items())),
            "contributors": dict(contrib),
            "pct_original": round(100 * len(originals) / max(1, len(posts)), 1),
            "hedge_in_original": sum(p["has_hedge"] for p in originals),
            "contrast_in_original": sum(p["has_contrast"] for p in originals),
            "reform_in_original": sum(p["has_reform"] for p in originals),
            "analogy_in_original": sum(p["has_analogy"] for p in originals),
            "first_person_in_original": sum(p["has_first"] for p in originals),
            "colloq_in_original": sum(p["has_colloq"] for p in originals),
            "questions_in_original": sum(p["questions"] > 0 for p in originals),
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)

with (OUT_DIR / "high_value_originals.jsonl").open("w", encoding="utf-8") as f:
    for p in high[:250]:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

with (OUT_DIR / "samples_for_close_read.jsonl").open("w", encoding="utf-8") as f:
    for p in uniq_samples:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

# also dump a readable markdown of ~80 close-read candidates
md = ["# Close-read candidates\n"]
for p in uniq_samples[:90]:
    md.append(f"\n## id={p['id']} {p['datetime'][:10]} {p['provenance']} {p['contributor']} chars={p['chars']}\n")
    md.append(p["text"][:1800])
    md.append("\n")
(OUT_DIR / "close_read.md").write_text("\n".join(md), encoding="utf-8")

print("summary", (OUT_DIR / "summary.json").read_text()[:2000])
print("high", len(high), "samples", len(uniq_samples))
print("close_read chars", (OUT_DIR / "close_read.md").stat().st_size)
