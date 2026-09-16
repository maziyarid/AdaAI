#!/usr/bin/env python3
"""Reclassify high-value PhilosophyCafe items and emit studio/skill stats."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

SRC_A = Path("/workspace/artifacts/pc_analysis/high_value_originals.jsonl")
SRC_B = Path("/workspace/artifacts/pc_analysis/samples_for_close_read.jsonl")
FULL = Path("/workspace/artifacts/philosophycafe_posts.jsonl")
OUT = Path("/workspace/artifacts/pc_analysis/v2")
OUT.mkdir(parents=True, exist_ok=True)

INTERVIEW_MARKERS = re.compile(
    r"(مصاحبه|آقای دکتر|با تشکر از اینکه وقت|پرسشگر|گفت‌وگو با|این مصاحبه|"
    r"روزنامه|هفته گذشته انجام شده|خطابه ی ریاست|در این نوشتار نگارنده)",
    re.I,
)
FORWARD_MARKERS = re.compile(
    r"(مترجم فارسی|ترجمه‌ی |ترجمه از|📚 مقاله|غرایز و فرازونشیب|"
    r"#جملات_قصار|#نقل_قول|چنین گفت زرتشت)",
    re.I,
)
SIGNED_NADERI = re.compile(r"(#امید_نادری|@NaderiOmid66|امید نادری)")
SIGNED_ALI = re.compile(r"(#علی_سلطان|@Ali_soltanzadeh|علی سلطان.?زاده|نقد و نظر)")
SIGNED_ARMAN = re.compile(r"(#آرمان_خادمی|@khadem_ar|آرمان خادمی)")
COLLOQ = re.compile(
    r"(می ?کنه|می ?شه|می ?تونه|دیگه|یه |رو |نمی ?دونم|چیکار|بابا|"
    r"خب |حالا |اینه|اون )"
)
AMA = re.compile(r"\bاما\b")
QUESTION = re.compile(r"[؟?]")
FIRST = re.compile(r"(به نظرم|من می ?خواهم|فکر می ?کنم|منظورم|دقیق تر بگویم|یا قوی تر)")
REFORM = re.compile(r"(به بیان ساده|به عبارت دیگر|یعنی |یا اینطوری بگم)")
ANALOGY = re.compile(r"(فرض کنید|نجار|تعمیر|مثل |مانند |شبیه )")
TEMPORAL_FLUFF = re.compile(r"(در دنیای امروز|در عصر حاضر|بر کسی پوشیده نیست|قصد داریم)")
MIBASHAD = re.compile(r"می ?باشد")
TAVASSOT = re.compile(r"توسط")


def year_of(p: dict) -> int:
    d = p.get("datetime") or ""
    try:
        return int(d[:4])
    except Exception:
        return 0


def contributor(text: str) -> str:
    if SIGNED_NADERI.search(text):
        return "naderi"
    if SIGNED_ALI.search(text):
        return "ali"
    if SIGNED_ARMAN.search(text):
        return "arman"
    return "unsigned"


def provenance(p: dict) -> str:
    t = (p.get("text") or "").strip()
    y = year_of(p)
    if not t:
        return "MEDIA_ONLY"
    if FORWARD_MARKERS.search(t) and not FIRST.search(t):
        return "TRANSLATED_OR_EXCERPT"
    if y <= 2018 and INTERVIEW_MARKERS.search(t):
        return "EXTERNAL_EXCERPT"
    if y <= 2018 and len(t) > 2500 and "هایدگر" in t:
        return "EXTERNAL_EXCERPT"
    if t.startswith("«") and len(t) < 220 and "اما" not in t:
        return "QUOTATION"
    if y >= 2022 and len(t) > 280:
        if FIRST.search(t) or COLLOQ.search(t) or AMA.search(t):
            return "ORIGINAL_CONTEMPORARY"
        return "LIKELY_ORIGINAL"
    if y >= 2022:
        return "SHORT_CONTEMPORARY"
    return "OLDER_MIXED"


def load() -> list[dict]:
    items = []
    seen = set()
    paths = [SRC_A, SRC_B]
    if FULL.exists() and FULL.stat().st_size > 1000:
        paths.append(FULL)
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                p = json.loads(line)
            except json.JSONDecodeError:
                continue
            pid = str(p.get("id") or "")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            items.append(p)
    return items


def main() -> None:
    items = load()
    print("loaded", len(items))
    rows = []
    for p in items:
        t = p.get("text") or ""
        row = {
            "id": p.get("id"),
            "datetime": p.get("datetime"),
            "year": year_of(p),
            "chars": len(t),
            "contributor": contributor(t),
            "provenance": provenance(p),
            "has_ama": bool(AMA.search(t)),
            "has_question": bool(QUESTION.search(t)),
            "has_first": bool(FIRST.search(t)),
            "has_reform": bool(REFORM.search(t)),
            "has_analogy": bool(ANALOGY.search(t)),
            "has_colloq": bool(COLLOQ.search(t)),
            "has_fluff": bool(TEMPORAL_FLUFF.search(t)),
            "has_mibashad": bool(MIBASHAD.search(t)),
            "has_tavassot": bool(TAVASSOT.search(t)),
            "text": t,
        }
        rows.append(row)

    orig = [r for r in rows if r["provenance"] in {"ORIGINAL_CONTEMPORARY", "LIKELY_ORIGINAL"}]
    orig_2022 = [r for r in orig if r["year"] >= 2022]
    naderi = [r for r in orig_2022 if r["contributor"] == "naderi"]
    ali = [r for r in orig_2022 if r["contributor"] == "ali"]

    def rate(key: str, subset: list[dict]) -> float:
        if not subset:
            return 0.0
        return round(100 * sum(1 for r in subset if r[key]) / len(subset), 1)

    summary = {
        "loaded": len(items),
        "original_contemporary": len(orig),
        "original_2022plus": len(orig_2022),
        "naderi_2022plus": len(naderi),
        "ali_2022plus": len(ali),
        "years": dict(Counter(r["year"] for r in orig_2022)),
        "provenance": dict(Counter(r["provenance"] for r in rows)),
        "rates_2022plus_original": {
            "ama": rate("has_ama", orig_2022),
            "question": rate("has_question", orig_2022),
            "first_person_epistemic": rate("has_first", orig_2022),
            "reformulation": rate("has_reform", orig_2022),
            "analogy": rate("has_analogy", orig_2022),
            "colloquial": rate("has_colloq", orig_2022),
            "temporal_fluff": rate("has_fluff", orig_2022),
            "mibashad": rate("has_mibashad", orig_2022),
            "tavassot": rate("has_tavassot", orig_2022),
        },
        "negative_evidence": {
            "temporal_fluff_in_original_2022": sum(1 for r in orig_2022 if r["has_fluff"]),
            "mibashad_in_original_2022": sum(1 for r in orig_2022 if r["has_mibashad"]),
            "tavassot_in_original_2022": sum(1 for r in orig_2022 if r["has_tavassot"]),
        },
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Export compact originals for the app (no full dumps of distinctive long essays)
    compact = []
    for r in sorted(orig_2022, key=lambda x: int(str(x["id"])), reverse=True)[:80]:
        compact.append(
            {
                "id": r["id"],
                "year": r["year"],
                "contributor": r["contributor"],
                "chars": r["chars"],
                "flags": [k[4:] for k in ("has_ama", "has_question", "has_first", "has_reform", "has_analogy", "has_colloq") if r[k]],
            }
        )
    (OUT / "originals_index.json").write_text(
        json.dumps(compact, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
