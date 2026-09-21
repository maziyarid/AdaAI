#!/usr/bin/env python3
import json, sqlite3, time
from pathlib import Path
S=Path("/var/lib/ada-telegram-bot"); H=S/"heartbeat.json"; R=S/"ready.json"; D=S/"state.sqlite3"
x={"ok":False,"ready":R.exists(),"heartbeat_age":None,"outbox_queued":0,"outbox_dead":0,"inbound_pending":0}
try:
    h=json.loads(H.read_text()); x["heartbeat_age"]=max(0,int(time.time())-int(h.get("epoch",0))); x["state"]=h.get("state")
except Exception: x["state"]="unknown"
try:
    c=sqlite3.connect(str(D),timeout=5)
    x["outbox_queued"]=c.execute("select count(*) from outbox where status='queued'").fetchone()[0]
    x["outbox_dead"]=c.execute("select count(*) from outbox where status='dead'").fetchone()[0]
    x["inbound_pending"]=c.execute("select count(*) from inbound where state='pending'").fetchone()[0]; c.close()
except Exception: pass
x["ok"]=bool(x["ready"] and x["heartbeat_age"] is not None and x["heartbeat_age"]<=90 and x["state"] in ("running","degraded"))
print(json.dumps(x,sort_keys=True)); raise SystemExit(0 if x["ok"] else 2)
