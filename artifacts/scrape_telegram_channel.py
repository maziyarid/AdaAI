#!/usr/bin/env python3
"""Walk a public t.me/s/CHANNEL archive with prev pagination and checkpoints."""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

UA = "Mozilla/5.0 (compatible; research-bot/1.1; +https://example.local)"


class PostParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.posts = []
        self.prev_href = None
        self._in_text = False
        self._in_reply = False
        self._cur = None
        self._text_parts = []
        self._reply_parts = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = d.get("class", "")
        if tag == "link" and d.get("rel") == "prev":
            self.prev_href = d.get("href")
        if tag == "a" and "tgme_widget_message_date" in cls and "before=" in d.get("href", ""):
            if not self.prev_href:
                self.prev_href = d.get("href")
        if tag == "div" and "tgme_widget_message" in cls.split() and "data-post" in d:
            if self._cur and self._cur.get("id"):
                self.posts.append(self._cur)
            pid = d.get("data-post", "").split("/")[-1]
            self._cur = {
                "id": pid,
                "data_post": d.get("data-post", ""),
                "text": "",
                "datetime": "",
                "url": "",
                "media": [],
                "reply_to": "",
                "views": "",
                "forwarded": False,
            }
            return
        if self._cur is None:
            return
        if tag == "div" and "js-message_text" in cls:
            self._in_text = True
            self._text_parts = []
        if tag == "a" and "tgme_widget_message_reply" in cls:
            self._in_reply = True
            self._reply_parts = []
            href = d.get("href", "")
            self._cur["reply_to"] = href
        if tag == "time" and "datetime" in d:
            self._cur["datetime"] = d["datetime"]
        if tag == "a" and "tgme_widget_message_date" in cls:
            self._cur["url"] = d.get("href", "")
        if tag == "br" and self._in_text:
            self._text_parts.append("\n")
        if tag == "video" or (tag == "i" and "tgme_widget_message_video" in cls):
            self._cur["media"].append("video")
        if tag == "a" and "tgme_widget_message_photo" in cls:
            self._cur["media"].append("photo")
        if tag == "a" and "tgme_widget_message_document" in cls:
            self._cur["media"].append("file")
        if "tgme_widget_message_video_thumb" in cls or "tgme_widget_message_videoplayer" in cls:
            if "video" not in self._cur["media"]:
                self._cur["media"].append("video")
        if "tgme_widget_message_forwarded_from" in cls:
            self._cur["forwarded"] = True
        if tag == "span" and "tgme_widget_message_views" in cls:
            self._cur["_cap_views"] = True

    def handle_endtag(self, tag):
        if tag == "div" and self._in_text:
            if self._cur is not None:
                text = "".join(self._text_parts)
                text = re.sub(r"\n{3,}", "\n\n", text).strip()
                self._cur["text"] = text
            self._in_text = False
            self._text_parts = []
        if tag == "a" and self._in_reply:
            self._in_reply = False
            if self._cur is not None:
                self._cur["reply_preview"] = " ".join("".join(self._reply_parts).split())[:280]

    def handle_data(self, data):
        if self._in_text:
            self._text_parts.append(data)
        elif self._in_reply:
            self._reply_parts.append(data)
        elif self._cur is not None and self._cur.pop("_cap_views", False):
            self._cur["views"] = data.strip()

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


def load_existing(path: Path) -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            p = json.loads(line)
            pid = str(p.get("id") or "")
            if pid:
                by_id[pid] = p
    return by_id


def save(path: Path, meta_path: Path, channel: str, by_id: dict[str, dict], pages: int, extra: dict | None = None) -> dict:
    posts = sorted(
        by_id.values(),
        key=lambda p: int(p["id"]) if str(p.get("id", "")).isdigit() else 0,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for p in posts:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    dates = [p["datetime"][:10] for p in posts if p.get("datetime")]
    ids = [int(p["id"]) for p in posts if str(p.get("id", "")).isdigit()]
    videos = sum(1 for p in posts if "video" in (p.get("media") or []))
    nonempty = sum(1 for p in posts if (p.get("text") or "").strip())
    meta = {
        "channel": channel,
        "count": len(posts),
        "min_id": min(ids) if ids else None,
        "max_id": max(ids) if ids else None,
        "min_date": min(dates) if dates else None,
        "max_date": max(dates) if dates else None,
        "nonempty": nonempty,
        "videos": videos,
        "pages_walked": pages,
        "method": "full_prev_walk",
    }
    if extra:
        meta.update(extra)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def walk(channel: str, out: Path, meta_path: Path, max_pages: int = 400, sleep: float = 0.32) -> dict:
    by_id = load_existing(out)
    print(f"{channel} existing={len(by_id)}")
    url = f"https://t.me/s/{channel}"
    before = None
    pages = 0
    stagnant = 0
    last_before = None
    for i in range(max_pages):
        try:
            html = fetch(url)
        except Exception as e:
            print(f"FAIL {url}: {e}")
            time.sleep(1.4)
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
                old = by_id[pid]
                if not (old.get("text") or "").strip() and (post.get("text") or "").strip():
                    by_id[pid] = post
        pages += 1
        print(f"{channel} page={pages} before={before} on_page={len(posts)} new={new} next={next_before} total={len(by_id)}")
        if pages % 10 == 0:
            save(out, meta_path, channel, by_id, pages)
        if not next_before or next_before == before or next_before == last_before:
            stagnant += 1
            if stagnant >= 2 or not next_before:
                break
        else:
            stagnant = 0
        last_before = before
        before = next_before
        url = f"https://t.me/s/{channel}?before={before}"
        time.sleep(sleep)
    extra = {"next_before": before, "finished": stagnant >= 2 or not before}
    meta = save(out, meta_path, channel, by_id, pages, extra)
    print("DONE", json.dumps(meta, ensure_ascii=False))
    return meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("channel")
    ap.add_argument("--max-pages", type=int, default=400)
    args = ap.parse_args()
    channel = args.channel.lstrip("@")
    base = Path("/workspace/artifacts/seo_sources") / channel
    walk(channel, base / "posts.jsonl", base / "meta.json", max_pages=args.max_pages)


if __name__ == "__main__":
    main()
