"""Resolve the caller's runtime binding; keep standalone loopback development."""
import os


def core_url(path: str) -> str:
    base = os.environ.get('ADA_CORE_URL', '').strip()
    if not base:
        if os.environ.get('VERCEL'):
            raise RuntimeError('ADA_CORE_URL service binding is required on Vercel')
        base = 'http://127.0.0.1:8791'
    return base.rstrip('/') + path
