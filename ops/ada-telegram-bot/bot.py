#!/usr/bin/env python3
import datetime as dt
import fcntl
import hmac
import hashlib
import json
import re
import os
import shutil
import signal
import socket
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TOKEN=os.environ.get("TELEGRAM_BOT_TOKEN","").strip()
PAIR_CODE=os.environ.get("TELEGRAM_PAIR_CODE","").strip()
STATE_DIR=Path(os.environ.get("STATE_DIR","/var/lib/ada-telegram-bot"))
DB_PATH=STATE_DIR/"state.sqlite3"
IDENTITY_FILE=STATE_DIR/"allowed_identity.json"
LEGACY_CHAT_FILE=STATE_DIR/"allowed_chat_id"
LOCK_FILE=STATE_DIR/"bot.lock"
HEARTBEAT_FILE=STATE_DIR/"heartbeat.json"
READY_FILE=STATE_DIR/"ready.json"
KILL_SWITCH=STATE_DIR/"commands.disabled"
CHAT_URL=os.environ.get("ADA_CHAT_URL","http://127.0.0.1:9102/internal/chat").strip()
AGIFLOW_READ_URL=os.environ.get("ADA_AGIFLOW_READ_URL","http://127.0.0.1:9102/internal/agiflow-read").strip()
SYSTEM_PROMPT_FILE=Path(os.environ.get("ADA_SYSTEM_PROMPT","/opt/ada-telegram-bot/system_prompt.txt"))
QALAM_RELEASE_FILE=Path(os.environ.get("ADA_QALAM_RELEASE","/opt/ada-telegram-bot/qalam-release.json"))
def qalam_release_label():
    try:
        data=json.loads(QALAM_RELEASE_FILE.read_text(encoding="utf-8"))
        c=data.get("components") or {}
        router=(c.get("qalam-router") or {}).get("version")
        bible=(c.get("art-of-writing-bible") or {}).get("version")
        if router and bible:
            return f"router@{router}+bible@{bible}"
    except Exception:
        pass
    return "unresolved"
QALAM_VERSION=qalam_release_label()
CHAT_HISTORY=[]
POLL_TIMEOUT=max(5,min(int(os.environ.get("TELEGRAM_POLL_TIMEOUT","20")),40))
RATE_LIMIT_PER_MIN=max(2,min(int(os.environ.get("TELEGRAM_COMMANDS_PER_MIN","20")),120))
MAX_OUTBOX_ATTEMPTS=max(3,min(int(os.environ.get("TELEGRAM_MAX_OUTBOX_ATTEMPTS","8")),20))
STOP=False
LOCK_HANDLE=None

class TelegramError(RuntimeError):
    def __init__(self,message,retry_after=None):
        super().__init__(message); self.retry_after=retry_after

def utcnow():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def redact_log_value(value):
    if not isinstance(value,str): return value
    x=value
    patterns=[
      (r'(?i)Bearer\s+[A-Za-z0-9._~+/=-]{8,}', 'Bearer [REDACTED]'),
      (r'\b\d{6,12}:[A-Za-z0-9_-]{20,}\b', '[TELEGRAM_TOKEN_REDACTED]'),
      (r'(?i)\b(api[_ -]?key|token|secret|password)\s*[:=]\s*\S+', r'\1=[REDACTED]'),
    ]
    for pat,repl in patterns: x=re.sub(pat,repl,x)
    return x[:2000]

def log(event,level="info",**fields):
    r={"ts":utcnow(),"level":level,"event":event}
    for k,v in fields.items():
        if k.lower() not in {"token","pair_code","password","secret","authorization"}:
            r[k]=redact_log_value(v)
    print(json.dumps(r,ensure_ascii=False,separators=(",",":")),flush=True)

def atomic_json(path,data,mode=0o600):
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True),encoding="utf-8")
    os.chmod(tmp,mode); os.replace(tmp,path)

def db():
    c=sqlite3.connect(str(DB_PATH),timeout=10); c.row_factory=sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA synchronous=FULL")
    try: os.chmod(DB_PATH,0o600)
    except FileNotFoundError: pass
    return c

def init_db():
    STATE_DIR.mkdir(parents=True,exist_ok=True); os.chmod(STATE_DIR,0o750)
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS inbound(
          update_id INTEGER PRIMARY KEY,payload_json TEXT NOT NULL,state TEXT NOT NULL DEFAULT 'pending',
          attempts INTEGER NOT NULL DEFAULT 0,received_at TEXT NOT NULL,done_at TEXT,last_error TEXT);
        CREATE TABLE IF NOT EXISTS outbox(
          id INTEGER PRIMARY KEY AUTOINCREMENT,idem_key TEXT UNIQUE,fingerprint TEXT,alert_state TEXT,
          severity TEXT NOT NULL DEFAULT 'info',source TEXT NOT NULL DEFAULT 'manual',text TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'queued',attempts INTEGER NOT NULL DEFAULT 0,next_attempt_at INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,sent_at TEXT,telegram_message_id INTEGER,last_error TEXT);
        CREATE INDEX IF NOT EXISTS outbox_due_idx ON outbox(status,next_attempt_at,id);
        CREATE TABLE IF NOT EXISTS alert_state(fingerprint TEXT PRIMARY KEY,last_state TEXT NOT NULL,updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS rate_events(user_id TEXT NOT NULL,ts INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS rate_events_idx ON rate_events(user_id,ts);
        CREATE TABLE IF NOT EXISTS feedback(
          id INTEGER PRIMARY KEY AUTOINCREMENT,category TEXT NOT NULL,original TEXT NOT NULL,preferred TEXT NOT NULL,
          reason TEXT,status TEXT NOT NULL DEFAULT 'pending_review',created_at TEXT NOT NULL,actor_user_id TEXT NOT NULL,
          source_update_id INTEGER,qalam_version TEXT NOT NULL,fingerprint TEXT UNIQUE);
        CREATE INDEX IF NOT EXISTS feedback_status_idx ON feedback(status,id);
        """)
        c.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('next_update_id','0')")
    os.chmod(DB_PATH,0o600)

def acquire_singleton():
    global LOCK_HANDLE
    LOCK_FILE.touch(mode=0o600,exist_ok=True); LOCK_HANDLE=LOCK_FILE.open("r+")
    try: fcntl.flock(LOCK_HANDLE.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: raise SystemExit("another AdaLLMbot poller already holds the singleton lock")
    LOCK_HANDLE.seek(0); LOCK_HANDLE.truncate(); LOCK_HANDLE.write(str(os.getpid())); LOCK_HANDLE.flush()

def api(method,payload=None,timeout=45):
    if not TOKEN: raise TelegramError("bot token is not configured")
    req=urllib.request.Request("https://api.telegram.org/bot"+TOKEN+"/"+method,
        data=urllib.parse.urlencode(payload).encode() if payload is not None else None,
        headers={"User-Agent":"AdaLLMbot/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as resp: body=json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        retry_after=None; msg="Telegram HTTP %s"%exc.code
        try:
            body=json.loads(exc.read().decode("utf-8")); msg=body.get("description") or msg
            retry_after=(body.get("parameters") or {}).get("retry_after")
        except Exception: pass
        raise TelegramError(msg,retry_after)
    except urllib.error.URLError as exc:
        raise TelegramError("Telegram network error: %s"%getattr(exc,"reason","unknown"))
    if not body.get("ok"):
        p=body.get("parameters") or {}; raise TelegramError(body.get("description","Telegram API error"),p.get("retry_after"))
    return body.get("result")

def api_retry(method,payload=None,timeout=45,attempts=4):
    delay=1; last=None
    for _ in range(attempts):
        try: return api(method,payload,timeout)
        except TelegramError as exc:
            last=exc; wait=exc.retry_after if exc.retry_after else delay
            time.sleep(max(1,min(int(wait),30))); delay=min(delay*2,16)
    raise last if last else TelegramError("Telegram call failed")

def send(chat_id,text):
    results=[]; text=str(text)
    for i in range(0,len(text),3900):
        results.append(api_retry("sendMessage",{"chat_id":str(chat_id),"text":text[i:i+3900]},20) or {})
    return results

def identity():
    try:
        d=json.loads(IDENTITY_FILE.read_text(encoding="utf-8"))
        return d if d.get("chat_id") is not None and d.get("user_id") is not None else None
    except (FileNotFoundError,ValueError,TypeError): return None

def migrate_legacy_identity():
    if IDENTITY_FILE.exists() or not LEGACY_CHAT_FILE.exists(): return
    try: chat_id=LEGACY_CHAT_FILE.read_text(encoding="utf-8").strip()
    except Exception: return
    if chat_id: atomic_json(STATE_DIR/"legacy_pairing.json",{"legacy_chat_id":chat_id,"migrated_at":utcnow(),"requires_repair":True})
    try: LEGACY_CHAT_FILE.unlink()
    except FileNotFoundError: pass

def save_identity(chat_id,user):
    d={"chat_id":int(chat_id),"user_id":int(user.get("id")),"username":user.get("username") or None,"paired_at":utcnow(),"version":2}
    atomic_json(IDENTITY_FILE,d); return d

def is_forwarded(m):
    return any(k in m for k in ("forward_origin","forward_date","forward_from","forward_sender_name","forward_from_chat")) or bool(m.get("is_automatic_forward"))

def rate_allowed(user_id):
    now=int(time.time()); floor=now-60
    with db() as c:
        c.execute("DELETE FROM rate_events WHERE ts<?",(floor,))
        n=c.execute("SELECT COUNT(*) FROM rate_events WHERE user_id=? AND ts>=?",(str(user_id),floor)).fetchone()[0]
        if n>=RATE_LIMIT_PER_MIN: return False
        c.execute("INSERT INTO rate_events(user_id,ts) VALUES(?,?)",(str(user_id),now))
    return True

def queue_stats():
    with db() as c:
        return (c.execute("SELECT COUNT(*) FROM outbox WHERE status='queued'").fetchone()[0],
                c.execute("SELECT COUNT(*) FROM outbox WHERE status='dead'").fetchone()[0],
                c.execute("SELECT COUNT(*) FROM inbound WHERE state='pending'").fetchone()[0])

def uptime_text():
    try:
        sec=int(float(Path("/proc/uptime").read_text().split()[0])); days,rem=divmod(sec,86400); hours,rem=divmod(rem,3600); mins,_=divmod(rem,60)
        return f"{days}d {hours}h {mins}m"
    except Exception: return "unknown"

def memory_text():
    try:
        vals={}
        for line in Path("/proc/meminfo").read_text().splitlines():
            k,v=line.split(":",1); vals[k]=int(v.strip().split()[0])
        total=vals["MemTotal"]; avail=vals.get("MemAvailable",vals.get("MemFree",0))
        return f"{(total-avail)/1048576:.1f}/{total/1048576:.1f} GiB"
    except Exception: return "unknown"

def status_text():
    disk=shutil.disk_usage("/")
    try: load=", ".join(f"{x:.2f}" for x in os.getloadavg())
    except Exception: load="unknown"
    q,d,p=queue_stats()
    return ("Ada Telegram bridge: online\\n"
      f"Host: {socket.gethostname()}\\nUptime: {uptime_text()}\\nLoad: {load}\\nMemory: {memory_text()}\\n"
      f"Disk /: {disk.used/disk.total*100:.1f}% used\\nOutbox queued/dead: {q}/{d}\\nInbound pending: {p}\\n"
      f"Command kill-switch: {'ON' if KILL_SWITCH.exists() else 'off'}")

def redact_feedback(text):
    x=str(text)
    patterns=[
      (r'(?i)Bearer\s+[A-Za-z0-9._~+/=-]{12,}', 'Bearer [REDACTED]'),
      (r'\b\d{6,12}:[A-Za-z0-9_-]{20,}\b', '[TELEGRAM_TOKEN_REDACTED]'),
      (r'(?i)\b(api[_ -]?key|token|secret|password)\s*[:=]\s*\S+', r'\1=[REDACTED]'),
      (r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', '[EMAIL_REDACTED]'),
      (r'(?<!\d)(?:\+?98|0)?9\d{9}(?!\d)', '[PHONE_REDACTED]')
    ]
    for pat,repl in patterns: x=re.sub(pat,repl,x)
    return x[:6000]

def store_feedback(category,original,preferred,reason,user_id,update_id):
    category=(category or "naturalness").strip().lower()
    allowed={"naturalness","formal","terminology","tone","rtl","wording","domain"}
    if category not in allowed: category="naturalness"
    original=redact_feedback(original.strip()); preferred=redact_feedback(preferred.strip()); reason=redact_feedback((reason or "").strip())
    if not original or not preferred: return None
    material="|".join([category,original,preferred,reason,QALAM_VERSION])
    fp=hashlib.sha256(material.encode("utf-8")).hexdigest()
    with db() as c:
        try:
            cur=c.execute("INSERT INTO feedback(category,original,preferred,reason,status,created_at,actor_user_id,source_update_id,qalam_version,fingerprint) VALUES(?,?,?,?, 'pending_review',?,?,?,?,?)",
              (category,original,preferred,reason,utcnow(),str(user_id),int(update_id) if update_id is not None else None,QALAM_VERSION,fp))
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

def feedback_stats():
    with db() as c:
        rows=c.execute("SELECT status,COUNT(*) n FROM feedback GROUP BY status").fetchall()
    return {r["status"]:r["n"] for r in rows}

def system_prompt():
    try: return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
    except Exception: return "You are Ada. Reply naturally and do not invent live operational state."

def agiflow_snapshot(kind):
    if kind not in ("active","blocked"): raise ValueError("unsupported_agiflow_read_kind")
    payload=json.dumps({"kind":kind},separators=(",",":")).encode("utf-8")
    req=urllib.request.Request(AGIFLOW_READ_URL,data=payload,headers={"Content-Type":"application/json","User-Agent":"AdaLLMbot/1.1"})
    with urllib.request.urlopen(req,timeout=25) as resp:
        body=json.loads(resp.read().decode("utf-8"))
    tasks=body.get("tasks") if isinstance(body,dict) else None
    if not isinstance(tasks,list): raise RuntimeError("invalid_agiflow_read_response")
    return {"kind":kind,"total":int(body.get("total") or len(tasks)),"tasks":tasks[:20]}

def format_task_snapshot(data):
    tasks=data.get("tasks") or []
    if not tasks:
        return "هیچ موردی پیدا نشد."
    lines=[]
    for t in tasks:
        slug=str(t.get("slug") or "?")
        title=str(t.get("title") or "").strip()
        status=str(t.get("status") or "").strip()
        priority=str(t.get("priority") or "").strip()
        suffix=" · ".join(x for x in (status,priority) if x)
        lines.append(f"{slug} — {title}" + (f" ({suffix})" if suffix else ""))
    total=int(data.get("total") or len(tasks))
    if total>len(tasks): lines.append(f"… و {total-len(tasks)} مورد دیگر")
    return "\n".join(lines)

def chat_with_ada(text):
    if len(text)>8000: raise ValueError("message_too_long")
    history="\n".join(f"{role}: {content}" for role,content in CHAT_HISTORY[-8:])
    prompt=(("Recent non-authoritative chat context:\n"+history+"\n\n") if history else "")+"User: "+text
    payload=json.dumps({"prompt":prompt,"system":system_prompt(),"temperature":0.35,"max_tokens":1200},ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(CHAT_URL,data=payload,headers={"Content-Type":"application/json","User-Agent":"AdaLLMbot/1.0"})
    with urllib.request.urlopen(req,timeout=75) as resp: body=json.loads(resp.read().decode("utf-8"))
    answer=((body.get("choices") or [{}])[0].get("message") or {}).get("content","").strip()
    if not answer: raise RuntimeError("empty_chat_response")
    CHAT_HISTORY.extend([("User",text),("Ada",answer)])
    del CHAT_HISTORY[:-8]
    return answer

HELP=(
    "دستورهای AdaLLMbot:\n"
    "/ping — بررسی ارتباط\n"
    "/status — خلاصه وضعیت VPS و پل تلگرام\n"
    "/health — وضعیت صف‌ها و آمادگی سرویس\n"
    "/tasks — کارهای فعال پروژه Ada/زیرساخت\n"
    "/blocked — کارهای مسدودشده پروژه Ada/زیرساخت\n"
    "/alerttest — تست مسیر هشدار\n"
    "/feedback — ثبت اصلاح زبانی برای بررسی بعدی\n"
    "/feedbackstatus — تعداد بازخوردهای ثبت‌شده\n"
    "/id — نمایش شناسه‌های عددی مجاز\n"
    "/help — راهنما\n\n"
    "برای گفت‌وگوی معمولی لازم نیست دستور بزنید؛ پیام عادی برای Ada فرستاده می‌شود. "
    "گفت‌وگو به‌خودی‌خود داده آموزشی محسوب نمی‌شود."
)

def enqueue_alert(text,idem_key=None,fingerprint=None,alert_state=None,severity="info",source="bot"):
    now=utcnow()
    with db() as c:
        if fingerprint and alert_state:
            row=c.execute("SELECT last_state FROM alert_state WHERE fingerprint=?",(fingerprint,)).fetchone()
            if row and row["last_state"]==alert_state: return None
            c.execute("INSERT INTO alert_state(fingerprint,last_state,updated_at) VALUES(?,?,?) ON CONFLICT(fingerprint) DO UPDATE SET last_state=excluded.last_state,updated_at=excluded.updated_at",(fingerprint,alert_state,now))
        try:
            cur=c.execute("INSERT INTO outbox(idem_key,fingerprint,alert_state,severity,source,text,status,next_attempt_at,created_at) VALUES(?,?,?,?,?,?,'queued',0,?)",(idem_key,fingerprint,alert_state,severity,source,text,now))
            return cur.lastrowid
        except sqlite3.IntegrityError: return None

def flush_outbox(chat_id,limit=10):
    now=int(time.time())
    with db() as c: rows=c.execute("SELECT * FROM outbox WHERE status='queued' AND next_attempt_at<=? ORDER BY id LIMIT ?",(now,limit)).fetchall()
    for row in rows:
        try:
            prefix=f"[{row['severity'].upper()}] {row['source']}\\n"
            results=send(chat_id,prefix+row["text"]); mid=results[-1].get("message_id") if results else None
            with db() as c: c.execute("UPDATE outbox SET status='sent',sent_at=?,telegram_message_id=?,last_error=NULL WHERE id=?",(utcnow(),mid,row["id"]))
            log("outbox_sent",outbox_id=row["id"],message_id=mid)
        except Exception as exc:
            attempts=int(row["attempts"])+1; state="dead" if attempts>=MAX_OUTBOX_ATTEMPTS else "queued"; retry=min(300,2**min(attempts,8))
            with db() as c: c.execute("UPDATE outbox SET status=?,attempts=?,next_attempt_at=?,last_error=? WHERE id=?",(state,attempts,int(time.time())+retry,f"{type(exc).__name__}: {str(exc)[:240]}",row["id"]))
            log("outbox_send_failed",level="warning",outbox_id=row["id"],attempts=attempts,state=state)

def health_text():
    q,d,p=queue_stats()
    return f"Ada health\\nready: {'yes' if READY_FILE.exists() else 'no'}\\noutbox queued: {q}\\noutbox dead-letter: {d}\\ninbound pending: {p}\\nkill-switch: {'ON' if KILL_SWITCH.exists() else 'off'}"

def handle(update):
    m=update.get("message")
    if not isinstance(m,dict): return
    chat=m.get("chat") or {}; user=m.get("from") or {}
    chat_id=chat.get("id"); user_id=user.get("id"); chat_type=chat.get("type"); text=(m.get("text") or "").strip()
    if chat_id is None or user_id is None: return
    if chat_type!="private":
        log("group_message_denied",level="warning",chat_id=chat_id,user_id=user_id); return
    if is_forwarded(m):
        log("forwarded_message_denied",level="warning",chat_id=chat_id,user_id=user_id); return
    ident=identity()
    if ident is None:
        if text.startswith("/pair "):
            supplied=text.split(None,1)[1].strip()
            if PAIR_CODE and hmac.compare_digest(supplied,PAIR_CODE):
                save_identity(chat_id,user); send(chat_id,"اتصال انجام شد. این گفت‌وگوی خصوصی و شناسه عددی شما مجاز شد.\n\n"+HELP)
                log("pairing_completed",chat_id=chat_id,user_id=user_id)
            else:
                send(chat_id,"کد اتصال درست نیست."); log("pairing_failed",level="warning",chat_id=chat_id,user_id=user_id)
        elif text in ("/start","/help"): send(chat_id,"AdaLLMbot هنوز به کاربر اصلی متصل نشده.")
        return
    if int(chat_id)!=int(ident["chat_id"]) or int(user_id)!=int(ident["user_id"]):
        log("unauthorised_message_denied",level="warning",chat_id=chat_id,user_id=user_id); return
    if not rate_allowed(user_id):
        send(chat_id,"تعداد درخواست‌ها در این دقیقه زیاد شده. کمی بعد دوباره امتحان کنید."); log("rate_limited",level="warning",chat_id=chat_id,user_id=user_id); return

    command=text.split()[0].split("@")[0].lower() if text else ""
    if KILL_SWITCH.exists() and command not in ("/ping","/health","/help","/start"):
        send(chat_id,"دستورهای ورودی موقتاً غیرفعال شده‌اند."); return

    if command in ("/start","/help"): send(chat_id,HELP)
    elif command=="/ping": send(chat_id,"pong")
    elif command=="/status": send(chat_id,status_text())
    elif command=="/health": send(chat_id,health_text())
    elif command in ("/tasks","/blocked"):
        try:
            kind="blocked" if command=="/blocked" else "active"
            data=agiflow_snapshot(kind)
            heading="کارهای مسدودشده:" if kind=="blocked" else "کارهای فعال:"
            send(chat_id,heading+"\n"+format_task_snapshot(data))
        except Exception as exc:
            log("agiflow_read_failed",level="warning",error_type=type(exc).__name__,detail=str(exc)[:160])
            send(chat_id,"فعلاً خواندن وضعیت Agiflow ممکن نیست؛ کمی بعد دوباره امتحان کنید.")
    elif command=="/id": send(chat_id,f"chat ID: {chat_id}\nuser ID: {user_id}")
    elif command=="/alerttest":
        qid=enqueue_alert("End-to-end AdaLLMbot alert path test.",idem_key=f"alerttest:{update.get('update_id')}",severity="info",source="AdaLLMbot")
        send(chat_id,"تست هشدار در صف قرار گرفت." if qid else "این تست قبلاً در صف ثبت شده.")
    elif command=="/feedbackstatus":
        st=feedback_stats(); send(chat_id,f"بازخورد زبانی — در انتظار بررسی: {st.get('pending_review',0)} | تأییدشده: {st.get('approved',0)} | ردشده: {st.get('rejected',0)}")
    elif command=="/feedback":
        rest=text[len(text.split()[0]):].strip() if text else ""
        reply=m.get("reply_to_message") or {}
        original=(reply.get("text") or "").strip()
        preferred=""; reason=""; category="naturalness"
        if original and rest:
            preferred=rest
        else:
            parts=[x.strip() for x in rest.split("|") if x.strip()]
            allowed={"naturalness","formal","terminology","tone","rtl","wording","domain"}
            if len(parts)>=3 and parts[0].lower() in allowed:
                category=parts[0].lower(); original=parts[1]; preferred=parts[2]; reason=parts[3] if len(parts)>3 else ""
            elif len(parts)>=2:
                original=parts[0]; preferred=parts[1]; reason=parts[2] if len(parts)>2 else ""
        if not original or not preferred:
            send(chat_id,"برای ثبت بازخورد، روی پیام Ada ریپلای کنید و بنویسید /feedback متن بهتر\nیا: /feedback متن قبلی | متن پیشنهادی")
        else:
            fid=store_feedback(category,original,preferred,reason,user_id,update.get("update_id"))
            send(chat_id,f"بازخورد ثبت شد؛ شناسه: {fid}" if fid else "این بازخورد قبلاً ثبت شده.")
    elif command:
        send(chat_id,"این دستور شناخته نشد. /help را بزنید.")
    elif text:
        try:
            send(chat_id,chat_with_ada(text))
        except Exception as exc:
            log("chat_backend_failed",level="warning",error_type=type(exc).__name__,detail=str(exc)[:160])
            send(chat_id,"فعلاً ارتباط با هسته گفت‌وگو برقرار نیست. کمی بعد دوباره امتحان کنید.")

    log("command_handled",command=command or "chat",chat_id=chat_id,user_id=user_id,update_id=update.get("update_id"))

def store_updates(updates):
    if not updates: return
    max_id=None; now=utcnow()
    with db() as c:
        for u in updates:
            uid=int(u["update_id"])
            c.execute("INSERT OR IGNORE INTO inbound(update_id,payload_json,state,received_at) VALUES(?,?,'pending',?)",(uid,json.dumps(u,ensure_ascii=False,separators=(",",":")),now))
            max_id=uid if max_id is None else max(max_id,uid)
        if max_id is not None:
            c.execute("INSERT INTO meta(key,value) VALUES('next_update_id',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(str(max_id+1),))
            c.execute("INSERT INTO meta(key,value) VALUES('last_inbound_at',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(now,))

def next_update_id():
    with db() as c: row=c.execute("SELECT value FROM meta WHERE key='next_update_id'").fetchone()
    return int(row["value"]) if row else 0

def process_pending(limit=50):
    processed=0
    while processed<limit:
        with db() as c: row=c.execute("SELECT update_id,payload_json,attempts FROM inbound WHERE state='pending' ORDER BY update_id LIMIT 1").fetchone()
        if not row: break
        try:
            handle(json.loads(row["payload_json"]))
            with db() as c: c.execute("UPDATE inbound SET state='done',done_at=?,last_error=NULL WHERE update_id=?",(utcnow(),row["update_id"]))
            processed+=1
        except Exception as exc:
            attempts=int(row["attempts"])+1; state="dead" if attempts>=5 else "pending"
            with db() as c: c.execute("UPDATE inbound SET state=?,attempts=?,last_error=? WHERE update_id=?",(state,attempts,f"{type(exc).__name__}: {str(exc)[:240]}",row["update_id"]))
            log("inbound_processing_failed" if state=="pending" else "inbound_dead_letter",level="warning" if state=="pending" else "error",update_id=row["update_id"],attempts=attempts)
            if state=="pending": break
            processed+=1
    return processed

def prune_history():
    with db() as c:
        c.execute("DELETE FROM inbound WHERE state='done' AND update_id NOT IN (SELECT update_id FROM inbound WHERE state='done' ORDER BY update_id DESC LIMIT 1000)")
        c.execute("DELETE FROM rate_events WHERE ts<?",(int(time.time())-3600,))

def heartbeat(bot_username=None,state="running"):
    q,d,p=queue_stats()
    atomic_json(HEARTBEAT_FILE,{"ts":utcnow(),"epoch":int(time.time()),"pid":os.getpid(),"state":state,"bot_username":bot_username,"next_update_id":next_update_id(),"outbox_queued":q,"outbox_dead":d,"inbound_pending":p,"paired":bool(identity())})

def on_signal(signum,frame):
    global STOP; STOP=True

def main():
    if not TOKEN: raise SystemExit("TELEGRAM_BOT_TOKEN is missing")
    init_db(); migrate_legacy_identity(); acquire_singleton()
    signal.signal(signal.SIGTERM,on_signal); signal.signal(signal.SIGINT,on_signal)
    me=api_retry("getMe",timeout=20); username=me.get("username","unknown")
    atomic_json(READY_FILE,{"ready_at":utcnow(),"pid":os.getpid(),"bot_username":username})
    log("telegram_connected",bot_username=username,paired=bool(identity()))
    process_pending(100)
    ident=identity()
    if ident: enqueue_alert(f"AdaLLMbot bridge is online on {socket.gethostname()}.",idem_key=f"startup:{os.getpid()}:{int(time.time())}",severity="info",source="AdaLLMbot")
    backoff=1; last_prune=0
    try:
        while not STOP:
            ident=identity()
            if ident: flush_outbox(ident["chat_id"],10)
            process_pending(50); heartbeat(username)
            if time.time()-last_prune>3600: prune_history(); last_prune=time.time()
            try:
                updates=api("getUpdates",{"timeout":POLL_TIMEOUT,"allowed_updates":json.dumps(["message"]),"offset":next_update_id()},POLL_TIMEOUT+10)
                store_updates(updates or []); process_pending(50); backoff=1
            except TelegramError as exc:
                log("poll_failed",level="warning",detail=str(exc)[:240],backoff=backoff)
                heartbeat(username,"degraded"); wait=exc.retry_after if exc.retry_after else backoff
                time.sleep(max(1,min(int(wait),30))); backoff=min(backoff*2,30)
    finally:
        try: READY_FILE.unlink()
        except FileNotFoundError: pass
        heartbeat(username,"stopped"); log("bot_stopped")

if __name__=="__main__": main()
