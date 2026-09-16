from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from typing import Any


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def hmac_sign(payload: dict, key: str) -> str:
    if len(key) < 32:
        raise RuntimeError("receipt HMAC key must be at least 32 characters")
    return hmac.new(key.encode(), canonical_json(payload).encode(), hashlib.sha256).hexdigest()


def hmac_verify(payload: dict, signature: str, key: str) -> bool:
    return hmac.compare_digest(hmac_sign(payload, key), signature)


def token() -> str:
    return secrets.token_urlsafe(32)
