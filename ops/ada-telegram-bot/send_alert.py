#!/usr/bin/env python3
import argparse, datetime as dt, json, os, sqlite3, sys, uuid
from pathlib import Path
STATE_DIR=Path(os.environ.get("STATE_DIR","/var/lib/ada-telegram-bot"))
DB_PATH=STATE_DIR/"state.sqlite3"
def utcnow(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
def db():
    c=sqlite3.connect(str(DB_PATH),timeout=10); c.row_factory=sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA synchronous=FULL")
    try: os.chmod(DB_PATH,0o600)
    except FileNotFoundError: pass
    return c
def init(c):
    c.executescript("""
    CREATE TABLE IF NOT EXISTS outbox(
      id INTEGER PRIMARY KEY AUTOINCREMENT,idem_key TEXT UNIQUE,fingerprint TEXT,alert_state TEXT,
      severity TEXT NOT NULL DEFAULT 'info',source TEXT NOT NULL DEFAULT 'manual',text TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'queued',attempts INTEGER NOT NULL DEFAULT 0,next_attempt_at INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL,sent_at TEXT,telegram_message_id INTEGER,last_error TEXT);
    CREATE TABLE IF NOT EXISTS alert_state(fingerprint TEXT PRIMARY KEY,last_state TEXT NOT NULL,updated_at TEXT NOT NULL);
    """)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--key",dest="idem_key"); ap.add_argument("--fingerprint"); ap.add_argument("--state",dest="alert_state")
    ap.add_argument("--severity",choices=["info","warning","critical"],default="info"); ap.add_argument("--source",default="manual")
    ap.add_argument("message",nargs="*"); a=ap.parse_args()
    msg=" ".join(a.message).strip() if a.message else sys.stdin.read().strip()
    if not msg: raise SystemExit("No alert text provided")
    if (a.fingerprint is None)!=(a.alert_state is None): raise SystemExit("--fingerprint and --state must be provided together")
    if len(msg)>12000: raise SystemExit("Alert text too long")
    STATE_DIR.mkdir(parents=True,exist_ok=True); key=a.idem_key or "manual:"+str(uuid.uuid4()); now=utcnow()
    with db() as c:
        init(c)
        if a.fingerprint:
            row=c.execute("SELECT last_state FROM alert_state WHERE fingerprint=?",(a.fingerprint,)).fetchone()
            if row and row["last_state"]==a.alert_state:
                print(json.dumps({"queued":False,"suppressed":True,"reason":"unchanged_state"})); return
            c.execute("INSERT INTO alert_state(fingerprint,last_state,updated_at) VALUES(?,?,?) ON CONFLICT(fingerprint) DO UPDATE SET last_state=excluded.last_state,updated_at=excluded.updated_at",(a.fingerprint,a.alert_state,now))
        try:
            cur=c.execute("INSERT INTO outbox(idem_key,fingerprint,alert_state,severity,source,text,status,next_attempt_at,created_at) VALUES(?,?,?,?,?,?,'queued',0,?)",(key,a.fingerprint,a.alert_state,a.severity,a.source,msg,now))
            print(json.dumps({"queued":True,"id":cur.lastrowid,"key":key}))
        except sqlite3.IntegrityError:
            print(json.dumps({"queued":False,"suppressed":True,"reason":"duplicate_key","key":key}))
if __name__=="__main__": main()
