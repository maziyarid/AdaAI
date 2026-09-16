#!/usr/bin/env python3
"""Stratified scrape of t.me/s/PhilosophyCafe public preview."""
from __future__ import annotations

import json
import re
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

UA = "Mozilla/5.0 (compatible; research-bot/1.0; +https://example.local)"
OUT = Path("/workspace/artifacts/philosophycafe_posts.jsonl")
META = Path("/workspace/artifacts/philosophycafe_scrape_meta.json")


class PostParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.posts = []
        self.prev_href = None
        self._in_text = False
        self._in_time = False
        self._in_author = False
        self._cur = None
        self._text_parts = []
        self._time = ""
        self._attrs = {}

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "link" and d.get("rel") == "prev":
            self.prev_href = d.get("href")
        if tag == "div" and d.get("class", "").startswith("tgme_widget_message ") and "data-post" in d:
            if self._cur and self._cur.get("id"):
                self.posts.append(self._cur)
            self._cur = {
                "id": d.get("data-post", "").split("/")[-1],
                "text": "",
                "datetime": "",
                "url": "",
            }
        if self._cur is None:
            return
        cls = d.get("class", "")
        if tag == "div" and "js-message_text" in cls:
            self._in_text = True
            self._text_parts = []
        if tag == "time" and "datetime" in d:
            self._cur["datetime"] = d["datetime"]
        if tag == "a" and "tgme_widget_message_date" in cls:
            self._cur["url"] = d.get("href", "")
        if tag == "br" and self._in_text:
            self._text_parts.append("\n")
        if tag == "i" and self._in_text and "emoji" in cls:
            # skip emoji image, keep inner b text via handle_data
            pass

    def handle_endtag(self, tag):
        if tag == "div" and self._in_text:
            if self._cur is not None:
                text = "".join(self._text_parts)
                text = re.sub(r"\n{3,}", "\n\n", text).strip()
                self._cur["text"] = text
            self._in_text = False
            self._text_parts = []

    def handle_data(self, data):
        if self._in_text:
            self._text_parts.append(data)

    def close_last(self):
        if self._cur and self._cur.get("id"):
            self.posts.append(self._cur)
            self._cur = None


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fa,en"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_page(html: str):
    p = PostParser()
    p.feed(html)
    p.close_last()
    before = None
    if p.prev_href:
        m = re.search(r"before=(\d+)", p.prev_href)
        if m:
            before = int(m.group(1))
    return p.posts, before


def scrape_from(before: int | None, max_pages: int, seen: set[str]):
    collected = []
    url = "https://t.me/s/PhilosophyCafe" if before is None else f"https://t.me/s/PhilosophyCafe?before={before}"
    for i in range(max_pages):
        try:
            html = fetch(url)
        except Exception as e:
            print(f"FAIL {url}: {e}")
            break
        posts, next_before = parse_page(html)
        new = 0
        for post in posts:
            pid = post.get("id")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            collected.append(post)
            new += 1
        print(f"page before={before} posts_on_page={len(posts)} new={new} next={next_before}")
        if not next_before or next_before == before:
            break
        before = next_before
        url = f"https://t.me/s/PhilosophyCafe?before={before}"
        time.sleep(0.35)
    return collected, before


def main():
    seen: set[str] = set()
    all_posts = []

    # Stratified jumps across ~13500 ids / ~6 years
    # Recent (2026), then jumps backward.
    starts = [
        None,  # latest
        13400,
        13200,  # ~Jan 2026
        12800,
        12400,
        12000,
        11500,
        11000,
        10500,
        10000,
        9500,
        9000,
        8500,
        8000,
        7500,
        7000,
        6500,
        6000,
        5500,
        5000,
        4500,
        4000,
        3500,
        3000,
        2500,
        2000,
        1500,
        1000,
        500,
        200,
    ]

    for start in starts:
        print(f"\n=== START {start} ===")
        chunk, _ = scrape_from(start, max_pages=3, seen=seen)
        all_posts.extend(chunk)
        print(f"total so far: {len(all_posts)}")
        time.sleep(0.4)

    # Dedup by id, keep order
    uniq = []
    seen2 = set()
    for p in all_posts:
        if p["id"] in seen2:
            continue
        seen2.add(p["id"])
        uniq.append(p)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for p in uniq:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    dates = [p["datetime"][:10] for p in uniq if p.get("datetime")]
    meta = {
        "count": len(uniq),
        "min_id": min((int(p["id"]) for p in uniq if p["id"].isdigit()), default=None),
        "max_id": max((int(p["id"]) for p in uniq if p["id"].isdigit()), default=None),
        "min_date": min(dates) if dates else None,
        "max_date": max(dates) if dates else None,
        "nonempty": sum(1 for p in uniq if p.get("text")),
    }
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DONE", meta)


if __name__ == "__main__":
    main()
