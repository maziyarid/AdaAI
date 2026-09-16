from __future__ import annotations
import hashlib, hmac, json, os, secrets
from datetime import datetime, timezone
from typing import Any

RECEIPT_KEY = os.environ.get('ADA_RECEIPT_HMAC_KEY','')
RECEIPT_KEY_ID = os.environ.get('ADA_RECEIPT_KEY_ID','internal-hmac')


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, default=str)


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def hmac_sign(payload: dict) -> str:
    if len(RECEIPT_KEY) < 32:
        raise RuntimeError('ADA_RECEIPT_HMAC_KEY must be at least 32 characters')
    return hmac.new(RECEIPT_KEY.encode(), canonical_json(payload).encode(), hashlib.sha256).hexdigest()


def hmac_verify(payload: dict, signature: str) -> bool:
    return hmac.compare_digest(hmac_sign(payload), signature)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def token() -> str:
    return secrets.token_urlsafe(32)
