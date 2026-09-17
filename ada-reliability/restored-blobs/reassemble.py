#!/usr/bin/env python3
"""Reassemble engine.py and test_phase1_contracts.py from chunked base64 blobs."""
from pathlib import Path
import base64
root = Path(__file__).resolve().parent
def assemble(prefix, n):
    data = "".join((root / f"{prefix}.b64.{i:02d}").read_text() for i in range(n))
    return base64.b64decode(data)
eng = assemble("engine", 18)
tst = assemble("tests", 8)
dst_e = root.parent / "src" / "ada_reliability" / "engine.py"
dst_t = root.parent / "tests" / "test_phase1_contracts.py"
dst_e.write_bytes(eng)
dst_t.write_bytes(tst)
print("wrote", dst_e, len(eng), "bytes")
print("wrote", dst_t, len(tst), "bytes")
