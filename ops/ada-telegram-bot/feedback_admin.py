#!/usr/bin/env python3
import argparse, hashlib, json, os, sqlite3, sys
from pathlib import Path

STATE=Path(os.environ.get("STATE_DIR","/var/lib/ada-telegram-bot"))
DB=STATE/"state.sqlite3"
DATASETS=STATE/"datasets"

def conn():
    c=sqlite3.connect(str(DB),timeout=10); c.row_factory=sqlite3.Row; return c

def list_rows(status=None):
    with conn() as c:
        if status:
            rows=c.execute("SELECT id,category,status,created_at,qalam_version,fingerprint FROM feedback WHERE status=? ORDER BY id",(status,)).fetchall()
        else:
            rows=c.execute("SELECT id,category,status,created_at,qalam_version,fingerprint FROM feedback ORDER BY id").fetchall()
    for r in rows: print(json.dumps(dict(r),ensure_ascii=False,sort_keys=True))

def show(fid):
    with conn() as c: r=c.execute("SELECT * FROM feedback WHERE id=?",(fid,)).fetchone()
    if not r: raise SystemExit("feedback id not found")
    d=dict(r); d.pop("actor_user_id",None); print(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True))

def set_status(fid,status):
    with conn() as c:
        r=c.execute("SELECT status FROM feedback WHERE id=?",(fid,)).fetchone()
        if not r: raise SystemExit("feedback id not found")
        c.execute("UPDATE feedback SET status=? WHERE id=?",(status,fid))
    print(json.dumps({"id":fid,"status":status}))

def bucket(fp):
    n=int(fp[:2],16)
    if n<204: return "train"
    if n<230: return "dev"
    return "eval"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(65536),b""): h.update(chunk)
    return h.hexdigest()

def export(version):
    version=version.strip()
    if not version or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for ch in version):
        raise SystemExit("invalid version")
    with conn() as c:
        rows=c.execute("SELECT id,category,original,preferred,reason,created_at,qalam_version,fingerprint FROM feedback WHERE status='approved' ORDER BY id").fetchall()
    if not rows: raise SystemExit("no approved feedback to export")
    out=DATASETS/version
    if out.exists(): raise SystemExit("dataset version already exists; exports are immutable")
    out.mkdir(parents=True,mode=0o700)
    groups={"train":[],"dev":[],"eval":[]}
    for r in rows:
        d=dict(r); d["split"]=bucket(d["fingerprint"]); groups[d["split"]].append(d)
    files={}
    for split,items in groups.items():
        p=out/(split+".jsonl")
        with p.open("w",encoding="utf-8") as f:
            for d in items: f.write(json.dumps(d,ensure_ascii=False,sort_keys=True)+"\n")
        os.chmod(p,0o600)
        files[split]={"file":p.name,"count":len(items),"sha256":sha(p)}
    manifest={
      "dataset":"ada-qalam-feedback","version":version,"immutable":True,
      "policy":"explicit-feedback-only; approved-only; deterministic fingerprint split; no automatic promotion",
      "files":files,
      "source_db":str(DB),
      "record_count":len(rows),
      "qalam_versions":sorted(set(r["qalam_version"] for r in rows))
    }
    mp=out/"manifest.json"; mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8"); os.chmod(mp,0o600)
    manifest["manifest_sha256"]=sha(mp)
    print(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True))

def stats():
    with conn() as c: rows=c.execute("SELECT status,COUNT(*) n FROM feedback GROUP BY status").fetchall()
    print(json.dumps({r["status"]:r["n"] for r in rows},sort_keys=True))

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    lp=sub.add_parser("list"); lp.add_argument("--status",choices=["pending_review","approved","rejected"])
    sp=sub.add_parser("show"); sp.add_argument("id",type=int)
    apv=sub.add_parser("approve"); apv.add_argument("id",type=int)
    rej=sub.add_parser("reject"); rej.add_argument("id",type=int)
    ex=sub.add_parser("export"); ex.add_argument("version")
    sub.add_parser("stats")
    a=ap.parse_args()
    if a.cmd=="list": list_rows(a.status)
    elif a.cmd=="show": show(a.id)
    elif a.cmd=="approve": set_status(a.id,"approved")
    elif a.cmd=="reject": set_status(a.id,"rejected")
    elif a.cmd=="export": export(a.version)
    else: stats()
if __name__=="__main__": main()
