import os
os.environ.setdefault('ADA_RECEIPT_HMAC_KEY','x'*64)
os.environ.setdefault('ADA_RECEIPT_KEY_ID','test-key')
from app.core import hmac_sign,hmac_verify,sha256_obj

def test_hmac_roundtrip():
    p={'a':1,'b':'two'}; s=hmac_sign(p); assert hmac_verify(p,s)

def test_hmac_detects_change():
    p={'a':1}; s=hmac_sign(p); assert not hmac_verify({'a':2},s)

def test_hash_deterministic_dict_order():
    assert sha256_obj({'b':2,'a':1}) == sha256_obj({'a':1,'b':2})
