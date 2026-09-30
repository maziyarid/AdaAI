#!/usr/bin/env python3
"""Prepare (never install) a hash-bound Agiflow lease-fencing patch."""
from __future__ import annotations

import argparse
import ast
import hashlib
from pathlib import Path

BASELINE_SHA256 = "aec6639acf761dfb01a72feb670b4d841c25fb1e8000abdea41bca0dcf4a94f3"

HEADER = "def ack_external_sync(target, outcome, observed_external_version=None, error=None):"
NEW_HEADER = "def ack_external_sync(target, outcome, observed_external_version=None, error=None, *, worker_id=None, claim_attempt=None):"

ANCHOR = '''            if not row:
                raise KeyError("external sync item not found")
            if row["status"] in ("succeeded", "conflict", "quarantined"):'''
REPLACEMENT = '''            if not row:
                raise KeyError("external sync item not found")
            if row["target_service"] == "agiflow":
                # Attempt generation fences older invocations, even if the
                # same worker ID obtains a replacement lease after restart.
                if not isinstance(worker_id, str) or not worker_id.strip():
                    raise RuntimeError("external sync owner required")
                if type(claim_attempt) is not int or claim_attempt < 1:
                    raise RuntimeError("external sync claim attempt required")
                if claim_attempt != int(row["attempts"]):
                    raise RuntimeError("external sync claim attempt lost")
                if row["status"] == "in_progress":
                    if row["locked_by"] != worker_id:
                        raise RuntimeError("external sync owner lost")
                    if row["lease_until"] is None or row["lease_until"] <= now():
                        raise RuntimeError("external sync lease expired")
            if row["status"] in ("succeeded", "conflict", "quarantined"):'''

UPDATE = '''                       completed_at=%s,last_error=%s WHERE id=%s""",
                (final_outcome, available, observed_external_version, completed, error, row["id"]),
            )
            audit(cur, "external_sync.ack"'''
FENCED_UPDATE = '''                       completed_at=%s,last_error=%s WHERE id=%s
                       AND status='in_progress' AND locked_by=%s AND attempts=%s AND lease_until>%s""",
                (final_outcome, available, observed_external_version, completed, error, row["id"],
                 row["locked_by"], row["attempts"], now()),
            )
            if cur.rowcount != 1:
                raise RuntimeError("external sync lease ownership lost")
            audit(cur, "external_sync.ack"'''

HTTP = '''ack_external_sync(parts[2],a["outcome"],a.get("observed_external_version"),a.get("error"))'''
FENCED_HTTP = '''ack_external_sync(parts[2],a["outcome"],a.get("observed_external_version"),a.get("error"),worker_id=a.get("worker_id"),claim_attempt=a.get("claim_attempt"))'''


def transform(source: str) -> str:
    for old, new in ((HEADER, NEW_HEADER), (ANCHOR, REPLACEMENT),
                     (UPDATE, FENCED_UPDATE), (HTTP, FENCED_HTTP)):
        if source.count(old) != 1:
            raise ValueError("SOURCE_ANCHOR_MISMATCH")
        source = source.replace(old, new, 1)
    ast.parse(source)
    return source


def prepare(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != BASELINE_SHA256:
        raise ValueError("LIVE_BASELINE_CHANGED")
    return transform(source.decode("utf-8")).encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    target = args.destination.parent.resolve() / args.destination.name
    # Do not install or overwrite a deployed source or an earlier candidate.
    if str(target).startswith(("/opt/", "/etc/", "/srv/maziyar-wp-mcp/deploy/")) or target == source:
        parser.error("destination must be a new staged candidate outside runtime paths")
    candidate = prepare(source.read_bytes())
    with target.open("xb") as f:
        f.write(candidate)
    print("STAGED_SHA256=" + hashlib.sha256(candidate).hexdigest())


if __name__ == "__main__":
    main()
