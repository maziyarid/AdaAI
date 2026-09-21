#!/usr/bin/env python3
import datetime as dt
import hashlib
import hmac
import json
import os
import sqlite3
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from pathlib import Path

HOST=os.environ.get("MSROBOT_BRIDGE_HOST","127.0.0.1")
PORT=int(os.environ.get("MSROBOT_BRIDGE_PORT","9110"))
STATE=Path(os.environ.get("MSROBOT_BRIDGE_STATE","/var/lib/ms-robot-bridge"))
DB=STATE/"events.sqlite3"
ALLOWED_TARGETS={"ada","ms_robot","agiflow","telegram","analytics"}
ALLOWED_SENSITIVITY={"public","internal","confidential","restricted"}
SECRET_KEY_MARKERS=("token","password","secret","api_key","apikey","authorization","private_key","otp")
MAX_PAYLOAD_BYTES=65536
MAX_ATTEMPTS=8
BRIDGE_TOKEN=os.environ.get("MSROBOT_BRIDGE_TOKEN","").strip()

def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def db():
    c=sqlite3.connect(str(DB),timeout=10)
    c.row_factory=sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA synchronous=FULL")
    return c

def init_db():
    STATE.mkdir(parents=True,exist_ok=True)
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS events(
          event_id TEXT PRIMARY KEY,
          schema_version INTEGER NOT NULL,
          idempotency_key TEXT NOT NULL UNIQUE,
          source TEXT NOT NULL,
          target TEXT NOT NULL,
          event_type TEXT NOT NULL,
          correlation_id TEXT,
          site_key TEXT,
          project_key TEXT,
          sensitivity TEXT NOT NULL,
          payload_json TEXT NOT NULL,
          payload_sha256 TEXT NOT NULL,
          state TEXT NOT NULL DEFAULT 'queued',
          attempts INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          delivered_at TEXT,
          acked_at TEXT,
          last_error TEXT
        );
        CREATE INDEX IF NOT EXISTS events_target_state_idx ON events(target,state,created_at);
        CREATE INDEX IF NOT EXISTS events_correlation_idx ON events(correlation_id,created_at);
        """)

def clean_text(v,maxlen=160):
    if v is None: return None
    s=str(v).strip()
    if not s: return None
    return s[:maxlen]

def contains_secret_like_key(value):
    if isinstance(value,dict):
        for k,v in value.items():
            low=str(k).lower()
            if any(marker in low for marker in SECRET_KEY_MARKERS):
                return True
            if contains_secret_like_key(v):
                return True
    elif isinstance(value,list):
        return any(contains_secret_like_key(v) for v in value)
    return False

def validate(envelope):
    if not isinstance(envelope,dict): raise ValueError("event_must_be_object")
    version=envelope.get("schema_version",1)
    if version!=1: raise ValueError("unsupported_schema_version")
    source=clean_text(envelope.get("source"),80)
    target=clean_text(envelope.get("target"),80)
    etype=clean_text(envelope.get("event_type"),160)
    idem=clean_text(envelope.get("idempotency_key"),240)
    sens=clean_text(envelope.get("sensitivity") or "internal",40)
    payload=envelope.get("payload")
    if not source or not target or not etype or not idem: raise ValueError("missing_required_field")
    if target not in ALLOWED_TARGETS: raise ValueError("unsupported_target")
    if sens not in ALLOWED_SENSITIVITY: raise ValueError("unsupported_sensitivity")
    if not isinstance(payload,dict): raise ValueError("payload_must_be_object")
    if contains_secret_like_key(payload): raise ValueError("secret_like_payload_key")
    raw=json.dumps(payload,ensure_ascii=False,separators=(",",":"),sort_keys=True).encode("utf-8")
    if len(raw)>MAX_PAYLOAD_BYTES: raise ValueError("payload_too_large")
    event_id=clean_text(envelope.get("event_id"),80) or str(uuid.uuid4())
    return {
      "event_id":event_id,
      "schema_version":1,
      "idempotency_key":idem,
      "source":source,
      "target":target,
      "event_type":etype,
      "correlation_id":clean_text(envelope.get("correlation_id"),160),
      "site_key":clean_text(envelope.get("site_key"),160),
      "project_key":clean_text(envelope.get("project_key"),160),
      "sensitivity":sens,
      "payload_json":raw.decode("utf-8"),
      "payload_sha256":hashlib.sha256(raw).hexdigest(),
    }

def insert_event(envelope):
    e=validate(envelope); ts=now()
    with db() as c:
        try:
            c.execute("""INSERT INTO events(event_id,schema_version,idempotency_key,source,target,event_type,
              correlation_id,site_key,project_key,sensitivity,payload_json,payload_sha256,state,created_at,updated_at)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?, 'queued',?,?)""",
              (e["event_id"],e["schema_version"],e["idempotency_key"],e["source"],e["target"],e["event_type"],
               e["correlation_id"],e["site_key"],e["project_key"],e["sensitivity"],e["payload_json"],e["payload_sha256"],ts,ts))
            return {"accepted":True,"duplicate":False,"event_id":e["event_id"],"state":"queued"}
        except sqlite3.IntegrityError:
            row=c.execute("SELECT event_id,state,payload_sha256 FROM events WHERE idempotency_key=?",(e["idempotency_key"],)).fetchone()
            if row and row["payload_sha256"]!=e["payload_sha256"]:
                raise ValueError("idempotency_key_payload_conflict")
            return {"accepted":True,"duplicate":True,"event_id":row["event_id"],"state":row["state"]}

def row_to_public(r):
    d=dict(r)
    d["payload"]=json.loads(d.pop("payload_json"))
    d.pop("last_error",None)
    return d

class Handler(BaseHTTPRequestHandler):
    server_version="MsRobotBridge/1.0"
    def log_message(self,fmt,*args):
        print(json.dumps({"ts":now(),"event":"http","remote":self.client_address[0],"message":fmt%args},separators=(",",":")),flush=True)
    def send_json(self,status,obj):
        body=json.dumps(obj,ensure_ascii=False,separators=(",",":")).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def authorised(self):
        if not BRIDGE_TOKEN:
            return False
        header=self.headers.get("Authorization","")
        if not header.startswith("Bearer "):
            return False
        return hmac.compare_digest(header[7:],BRIDGE_TOKEN)
    def require_auth(self):
        if self.authorised():
            return True
        self.send_json(401,{"error":"unauthorised"})
        return False
    def read_json(self):
        n=int(self.headers.get("Content-Length","0") or "0")
        if n<=0 or n>MAX_PAYLOAD_BYTES+16384: raise ValueError("invalid_body_size")
        raw=self.rfile.read(n)
        return json.loads(raw.decode("utf-8"))
    def do_GET(self):
        u=urlparse(self.path)
        if u.path=="/healthz":
            with db() as c:
                q=c.execute("SELECT COUNT(*) FROM events WHERE state='queued'").fetchone()[0]
                dead=c.execute("SELECT COUNT(*) FROM events WHERE state='dead'").fetchone()[0]
            return self.send_json(200,{"ok":True,"version":"1.0","queued":q,"dead":dead})
        if u.path=="/v1/events":
            if not self.require_auth(): return
            qs=parse_qs(u.query)
            target=(qs.get("target") or [None])[0]
            state=(qs.get("state") or ["queued"])[0]
            try: limit=max(1,min(int((qs.get("limit") or ["50"])[0]),200))
            except Exception: limit=50
            if target not in ALLOWED_TARGETS: return self.send_json(400,{"error":"unsupported_target"})
            if state not in {"queued","delivered","acked","dead"}: return self.send_json(400,{"error":"unsupported_state"})
            with db() as c:
                rows=c.execute("SELECT * FROM events WHERE target=? AND state=? ORDER BY created_at,event_id LIMIT ?",(target,state,limit)).fetchall()
            return self.send_json(200,{"events":[row_to_public(r) for r in rows],"count":len(rows)})
        return self.send_json(404,{"error":"not_found"})
    def do_POST(self):
        u=urlparse(self.path)
        try:
            if u.path.startswith("/v1/") and not self.require_auth(): return
            if u.path=="/v1/events":
                result=insert_event(self.read_json())
                return self.send_json(200 if result["duplicate"] else 201,result)
            parts=[p for p in u.path.split("/") if p]
            if len(parts)==4 and parts[:2]==["v1","events"] and parts[3] in {"delivered","ack","fail"}:
                event_id=parts[2]; action=parts[3]; body=self.read_json() if action=="fail" else {}
                with db() as c:
                    row=c.execute("SELECT * FROM events WHERE event_id=?",(event_id,)).fetchone()
                    if not row: return self.send_json(404,{"error":"event_not_found"})
                    ts=now()
                    if action=="delivered":
                        c.execute("UPDATE events SET state='delivered',delivered_at=?,updated_at=? WHERE event_id=?",(ts,ts,event_id))
                        state="delivered"
                    elif action=="ack":
                        c.execute("UPDATE events SET state='acked',acked_at=?,updated_at=? WHERE event_id=?",(ts,ts,event_id))
                        state="acked"
                    else:
                        attempts=int(row["attempts"])+1
                        state="dead" if attempts>=MAX_ATTEMPTS else "queued"
                        err=clean_text(body.get("error"),500) or "consumer_failed"
                        c.execute("UPDATE events SET state=?,attempts=?,last_error=?,updated_at=? WHERE event_id=?",(state,attempts,err,ts,event_id))
                return self.send_json(200,{"ok":True,"event_id":event_id,"state":state})
            return self.send_json(404,{"error":"not_found"})
        except ValueError as e:
            return self.send_json(400,{"error":str(e)})
        except json.JSONDecodeError:
            return self.send_json(400,{"error":"invalid_json"})
        except Exception as e:
            print(json.dumps({"ts":now(),"event":"handler_error","type":type(e).__name__,"detail":str(e)[:240]}),flush=True)
            return self.send_json(500,{"error":"internal_error"})

if __name__=="__main__":
    init_db()
    server=ThreadingHTTPServer((HOST,PORT),Handler)
    print(json.dumps({"ts":now(),"event":"bridge_started","host":HOST,"port":PORT,"version":"1.0"}),flush=True)
    server.serve_forever()
