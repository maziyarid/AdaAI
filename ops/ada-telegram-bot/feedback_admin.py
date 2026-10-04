#!/usr/bin/env python3
import argparse, fcntl, hashlib, json, os, shutil, sqlite3, sys, tempfile, unicodedata
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

def split_group(original):
    """Keep revisions of the same normalised input out of different splits."""
    normalised=" ".join(unicodedata.normalize("NFKC",original).casefold().split())
    if not normalised:
        raise SystemExit("approved feedback has an empty original")
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()

def write_private(path,content):
    with path.open("x",encoding="utf-8") as f:
        os.fchmod(f.fileno(),0o600)
        f.write(content)
        f.flush()
        os.fsync(f.fileno())

def sync_directory(path):
    descriptor=os.open(str(path),os.O_RDONLY|os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)

def export(version):
    version=version.strip()
    if (not version or len(version)>128 or version.startswith(".") or
            any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for ch in version)):
        raise SystemExit("invalid version")
    with conn() as c:
        rows=c.execute("SELECT id,category,original,preferred,reason,created_at,qalam_version,fingerprint FROM feedback WHERE status='approved' ORDER BY id").fetchall()
    if not rows:
        raise SystemExit("no approved feedback to export")
    groups={"train":[],"dev":[],"eval":[]}
    for r in rows:
        d=dict(r)
        d["split_group"]=split_group(d["original"])
        d["split"]=bucket(d["split_group"])
        groups[d["split"]].append(d)
    DATASETS.mkdir(parents=True,mode=0o700,exist_ok=True)
    os.chmod(DATASETS,0o700)
    # All exporters use this lock; publication occurs only after complete writes.
    lock=os.open(str(DATASETS/".export.lock"),os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    stage=None
    try:
        os.fchmod(lock,0o600)
        fcntl.flock(lock,fcntl.LOCK_EX)
        out=DATASETS/version
        if os.path.lexists(str(out)):
            raise SystemExit("dataset version already exists; exports are immutable")
        stage=Path(tempfile.mkdtemp(prefix=".export-",dir=str(DATASETS)))
        files={}
        for split,items in groups.items():
            p=stage/(split+".jsonl")
            write_private(p,"".join(json.dumps(d,ensure_ascii=False,sort_keys=True)+"\n" for d in items))
            files[split]={"file":p.name,"count":len(items),"sha256":sha(p)}
        manifest={
          "schema":"ada.feedback.dataset/v2",
          "dataset":"ada-qalam-feedback","version":version,"immutable":True,
          "policy":"explicit-feedback-only; approved-only; normalised-original group split; no automatic promotion",
          "split_policy":"sha256-nfkc-casefold-whitespace-original/v1",
          "redaction_policy":"capture-time automated redaction; human approval required",
          "files":files,"source_db":str(DB),"record_count":len(rows),
          "qalam_versions":sorted(set(r["qalam_version"] for r in rows))
        }
        mp=stage/"manifest.json"
        write_private(mp,json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
        manifest["manifest_sha256"]=sha(mp)
        sync_directory(stage)
        os.rename(stage,out)
        try:
            sync_directory(DATASETS)
        except OSError:
            raise SystemExit("dataset is complete but publication durability is unconfirmed; verify its manifest before retry") from None
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)
        os.close(lock)
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
