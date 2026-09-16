#!/usr/bin/env python3
"""Walk the entire public t.me/s/PhilosophyCafe archive (prev pagination)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scrape_philosophycafe import fetch, parse_page  # noqa: E402

OUT = Path("/workspace/artifacts/philosophycafe_posts.jsonl")
META = Path("/workspace/artifacts/philosophycafe_scrape_meta.json")
UA_SLEEP = 0.28
MAX_PAGES = 400


def load_existing() -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            p = json.loads(line)
            pid = str(p.get("id") or "")
            if pid:
                by_id[pid] = p
    return by_id


def save(by_id: dict[str, dict]) -> dict:
    posts = sorted(
        by_id.values(),
        key=lambda p: int(p["id"]) if str(p.get("id", "")).isdigit() else 0,
    )
    with OUT.open("w", encoding="utf-8") as f:
        for p in posts:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    dates = [p["datetime"][:10] for p in posts if p.get("datetime")]
    ids = [int(p["id"]) for p in posts if str(p.get("id", "")).isdigit()]
    meta = {
        "count": len(posts),
        "min_id": min(ids) if ids else None,
        "max_id": max(ids) if ids else None,
        "min_date": min(dates) if dates else None,
        "max_date": max(dates) if dates else None,
        "nonempty": sum(1 for p in posts if (p.get("text") or "").strip()),
        "method": "full_prev_walk",
        "pages_walked": None,
    }
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def main() -> None:
    by_id = load_existing()
    print(f"existing={len(by_id)}")
    url = "https://t.me/s/PhilosophyCafe"
    before = None
    pages = 0
    stagnant = 0
    for i in range(MAX_PAGES):
        try:
            html = fetch(url)
        except Exception as e:
            print(f"FAIL {url}: {e}")
            time.sleep(1.2)
            continue
        posts, next_before = parse_page(html)
        new = 0
        for post in posts:
            pid = str(post.get("id") or "")
            if not pid:
                continue
            if pid not in by_id:
                by_id[pid] = post
                new += 1
            else:
                # fill missing text/datetime if we had a stub
                old = by_id[pid]
                if not old.get("text") and post.get("text"):
                    by_id[pid] = post
                    new += 1
        pages += 1
        print(
            f"page {pages} before={before} on_page={len(posts)} new={new} "
            f"next={next_before} total={len(by_id)}"
        )
        if pages % 25 == 0:
            save(by_id)
            print("checkpoint saved")
        if not next_before:
            print("no next_before — archive start reached")
            break
        if next_before == before:
            stagnant += 1
            if stagnant >= 2:
                print("stagnant pagination — stop")
                break
        else:
            stagnant = 0
        before = next_before
        url = f"https://t.me/s/PhilosophyCafe?before={before}"
        time.sleep(UA_SLEEP)

    meta = save(by_id)
    meta["pages_walked"] = pages
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DONE", meta)


if __name__ == "__main__":
    main()
