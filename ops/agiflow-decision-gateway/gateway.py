#!/usr/bin/env python3
"""Scoped decision producer. The control-core external-sync queue owns delivery."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import socketserver
import stat
import struct
import time
import urllib.parse
import urllib.request

PROJECT_ID = '01M2QCDQ4CDZCHVGT5PKCBVDQM'
PROJECT_SLUG = 'other-projects-infrastructure'
MAX_BYTES = 16384
ANCHORS = {'AAX-26':'01M2ZZYSPQTH6RVF43T5614XEE', 'AAX-31':'01M300NB8TZBQ28X0ANPQRETKV'}


class DecisionError(RuntimeError):
    """Fixed categories only: exceptions can enter the bot's durable error field."""


def strict_json(raw):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result: raise DecisionError('DUPLICATE_JSON_KEY')
            result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs)


def integer(value, minimum=1):
    return type(value) is int and minimum <= value <= 2**53-1


def clean(value):
    if not isinstance(value,str) or not value.strip() or len(value)>2000:
        raise DecisionError('INVALID_DECISION_TEXT')
    if '[sync:' in value.lower() or any(ord(c)<32 and c not in '\n\t' for c in value):
        raise DecisionError('INVALID_DECISION_TEXT')
    value=value.strip()
    patterns=[
        (r'(?is)-----BEGIN [^-]*PRIVATE KEY-----.*?(?:-----END [^-]*PRIVATE KEY-----|$)', '[REDACTED]'),
        (r'(?i)Bearer\s+\S+', 'Bearer [REDACTED]'),
        (r'\b\d{6,12}:[A-Za-z0-9_-]{20,}\b','[REDACTED]'),
        (r'(?i)\b(api[_ -]?key|token|secret|password)\s*[:=]\s*\S+',r'\1=[REDACTED]'),
        (r'(?i)https?://[^\s/@:]+:[^\s/@]+@[^\s]+','[REDACTED]'),
        (r'(?i)\bgithub_pat_[A-Za-z0-9_]+\b','[REDACTED]'),
        (r'(?i)\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{12,})\b','[REDACTED]'),
        (r'(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}','[REDACTED]'),
        (r'(?<!\d)(?:\+?98|0)?9\d{9}(?!\d)','[REDACTED]'),
    ]
    for pattern,replacement in patterns: value=re.sub(pattern,replacement,value)
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): raise DecisionError('UPSTREAM_REDIRECT')


def parse_sse_jsonrpc(raw,expected_id):
    try:
        text=raw.decode('utf-8')
    except UnicodeDecodeError:
        raise DecisionError('UPSTREAM_RESPONSE_INVALID') from None
    matches=[]; events=0
    for block in re.split(r'\r?\n\r?\n',text):
        if not block.strip(): continue
        events+=1
        if events>256: raise DecisionError('UPSTREAM_RESPONSE_INVALID')
        event='message'; data=[]
        for line in block.splitlines():
            if not line or line.startswith(':'): continue
            field,sep,value=line.partition(':')
            if not sep: value=''
            elif value.startswith(' '): value=value[1:]
            if field=='event': event=value
            elif field=='data': data.append(value)
        if not data or event not in ('','message'): continue
        try: payload=strict_json('\n'.join(data))
        except Exception: raise DecisionError('UPSTREAM_RESPONSE_INVALID') from None
        if (isinstance(payload,dict) and payload.get('jsonrpc')=='2.0'
                and payload.get('id')==expected_id):
            matches.append(payload)
            if len(matches)>1: raise DecisionError('UPSTREAM_RESPONSE_INVALID')
    if len(matches)!=1: raise DecisionError('UPSTREAM_RESPONSE_INVALID')
    return matches[0]


def post_json(url,body,headers,*,allow_sse=False,jsonrpc_id=None):
    request=urllib.request.Request(url,data=json.dumps(body,ensure_ascii=False).encode(),
        headers=dict(headers,**{'Content-Type':'application/json'}),method='POST')
    # Never forward credentials through redirects or environment proxy settings.
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
    try:
        with opener.open(request,timeout=8) as response:
            content_type=(response.headers.get('Content-Type') or '').split(';',1)[0].strip().lower()
            raw=response.read(1024*1024+1)
        if len(raw)>1024*1024: raise DecisionError('UPSTREAM_RESPONSE_TOO_LARGE')
        if content_type=='text/event-stream':
            if not allow_sse or jsonrpc_id is None:
                raise DecisionError('UPSTREAM_RESPONSE_INVALID')
            result=parse_sse_jsonrpc(raw,jsonrpc_id)
        else:
            result=strict_json(raw)
        if not isinstance(result,dict): raise DecisionError('UPSTREAM_RESPONSE_INVALID')
        return result
    except DecisionError: raise
    except Exception: raise DecisionError('UPSTREAM_UNAVAILABLE') from None


class AgiflowReader:
    def __init__(self,url,key,*,allow_test_http=False):
        parsed=urllib.parse.urlsplit(url)
        test=allow_test_http and parsed.scheme=='http' and parsed.hostname=='127.0.0.1'
        if (parsed.scheme!='https' and not test) or not parsed.hostname or parsed.username or parsed.password or parsed.fragment or not key:
            raise DecisionError('AGIFLOW_CONFIG_INVALID')
        self.url,self.key=url,key

    def get_task(self,slug):
        body=post_json(self.url,{'jsonrpc':'2.0','id':1,'method':'tools/call','params':{
            'name':'get_task','arguments':{'id':slug,'projectId':PROJECT_SLUG}}},
            {'x-api-key':self.key,'Accept':'application/json, text/event-stream'},
            allow_sse=True,jsonrpc_id=1)
        if body.get('error') or body.get('id')!=1: raise DecisionError('AGIFLOW_READ_INVALID')
        result=body.get('result')
        if not isinstance(result,dict) or result.get('isError'): raise DecisionError('AGIFLOW_READ_INVALID')
        if 'structuredContent' in result:
            payload=result['structuredContent']
        else:
            blocks=result.get('content')
            if not isinstance(blocks,list): raise DecisionError('AGIFLOW_READ_INVALID')
            texts=[b['text'] for b in blocks if isinstance(b,dict) and b.get('type')=='text' and isinstance(b.get('text'),str)]
            if len(texts)!=1: raise DecisionError('AGIFLOW_READ_INVALID')
            try: payload=strict_json(texts[0])
            except Exception: raise DecisionError('AGIFLOW_READ_INVALID') from None
        if not isinstance(payload,dict) or not isinstance(payload.get('task'),dict):
            raise DecisionError('AGIFLOW_READ_INVALID')
        return payload['task']


class ControlCore:
    def __init__(self,url,token):
        parsed=urllib.parse.urlsplit(url)
        if parsed.scheme!='http' or parsed.hostname!='127.0.0.1' or parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment or not token:
            raise DecisionError('CORE_CONFIG_INVALID')
        self.url,self.token=url.rstrip('/'),token

    def enqueue(self,body):
        return post_json(self.url+'/external-sync',body,
            {'Authorization':'Bearer '+self.token,'Accept':'application/json'})


class Gateway:
    def __init__(self,*,provider,core,enabled=False,bot_uid,user_id,chat_id,bot_id,actor,clock=time.time):
        if not all(integer(x) for x in (bot_uid,user_id,chat_id,bot_id)) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9 ._-]{0,63}',actor):
            raise DecisionError('IDENTITY_CONFIG_INVALID')
        self.provider,self.core,self.enabled=provider,core,enabled
        self.bot_uid,self.user_id,self.chat_id,self.bot_id,self.actor=bot_uid,user_id,chat_id,bot_id,actor
        self.clock=clock

    def submit(self,request,peer_uid):
        if self.enabled is not True: raise DecisionError('DISABLED')
        if type(peer_uid) is not int or peer_uid!=self.bot_uid: raise DecisionError('PEER_DENIED')
        expected={'update_id','date','user_id','chat_id','task','decision','rationale'}
        if not isinstance(request,dict) or set(request)!=expected: raise DecisionError('INVALID_REQUEST')
        if not all(integer(request[k],0 if k=='update_id' else 1) for k in ('update_id','date','user_id','chat_id')):
            raise DecisionError('INVALID_IDENTITY')
        if request['user_id']!=self.user_id or request['chat_id']!=self.chat_id: raise DecisionError('IDENTITY_DENIED')
        if not -60 <= self.clock()-request['date'] <= 86400: raise DecisionError('REQUEST_EXPIRED')
        slug=request['task']
        if not isinstance(slug,str) or not re.fullmatch(r'AAX-[1-9][0-9]{0,7}',slug): raise DecisionError('INVALID_TASK')
        decision,rationale=clean(request['decision']),clean(request['rationale'])
        try:
            contexts={}
            for reference in dict.fromkeys([*ANCHORS,slug]):
                task=self.provider.get_task(reference)
                if (not isinstance(task,dict) or task.get('projectId')!=PROJECT_ID or task.get('slug')!=reference
                    or not isinstance(task.get('id'),str) or not re.fullmatch(r'[0-9A-HJKMNP-TV-Z]{26}',task['id'])
                    or not integer(task.get('revision')) or (reference in ANCHORS and task['id']!=ANCHORS[reference])):
                    raise DecisionError('TASK_CONTEXT_INVALID')
                contexts[reference]=task
            task=contexts[slug]
            # Mutable revision/title never enter the retry payload. This is an append-only
            # operator note, not authorisation or a task status/description mutation.
            material=f"ada-decision-v1:{self.bot_id}:{self.user_id}:{self.chat_id}:{request['update_id']}"
            idem='ada-decision:'+hashlib.sha256(material.encode()).hexdigest()
            timestamp=dt.datetime.fromtimestamp(request['date'],dt.timezone.utc).isoformat()
            content=(f'Operator decision — {slug}\nActor: {self.actor}\nChannel: Telegram private command\n'
                f'Time: {timestamp}\n\nDecision:\n{decision}\n\nRationale:\n{rationale}\n\n[sync:{idem}]')
            payload={'task_ref':task['id'],'content':content,'idempotency_key':idem}
            body={'target_service':'agiflow','entity_type':'task_comment','entity_id':task['id'],
                'operation':'create_task_comment','payload':payload,'idempotency_key':idem,
                'stable_id':'sync:'+idem,'max_attempts':5}
            receipt=self.core.enqueue(body)
            if not isinstance(receipt,dict): raise DecisionError('RECEIPT_MISMATCH')
            if any(receipt.get(k)!=v for k,v in body.items() if k not in ('payload','max_attempts')):
                raise DecisionError('RECEIPT_MISMATCH')
            try: observed=strict_json(receipt.get('payload_json',''))
            except Exception: raise DecisionError('RECEIPT_MISMATCH') from None
            if observed!=payload or not isinstance(receipt.get('id'),str) or not receipt['id']:
                raise DecisionError('RECEIPT_MISMATCH')
            if receipt.get('status') not in ('pending','in_progress','succeeded'):
                raise DecisionError('QUEUE_REQUIRES_REVIEW')
            # A producer receipt alone is never independent provider delivery proof.
            return {'status':'QUEUED','reference':idem,'task':slug}
        except DecisionError: raise
        except Exception: raise DecisionError('UPSTREAM_UNAVAILABLE') from None


class DecisionHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(20)
        try:
            _,uid,_=struct.unpack('3i',self.request.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
            if uid!=self.server.gateway.bot_uid: raise DecisionError('PEER_DENIED')
            deadline=time.monotonic()+3
            raw=b''
            while b'\n' not in raw and len(raw)<=MAX_BYTES:
                remaining=deadline-time.monotonic()
                if remaining<=0: raise DecisionError('INVALID_REQUEST')
                self.request.settimeout(remaining)
                chunk=self.request.recv(min(4096,MAX_BYTES+1-len(raw)))
                if not chunk: break
                raw+=chunk
            if len(raw)>MAX_BYTES or not raw.endswith(b'\n'): raise DecisionError('INVALID_REQUEST')
            try: request=strict_json(raw)
            except Exception: raise DecisionError('INVALID_REQUEST') from None
            result=self.server.gateway.submit(request,uid)
        except DecisionError as error: result={'status':'REJECTED','error':str(error)}
        except Exception: result={'status':'REJECTED','error':'REQUEST_FAILED'}
        try: self.wfile.write(json.dumps(result).encode()+b'\n')
        except OSError: pass


class DecisionServer(socketserver.UnixStreamServer):
    # Serial, bounded requests; the only durable obligation is in control core.
    def __init__(self,path,gateway):
        self.gateway=gateway
        super().__init__(path,DecisionHandler)
        os.chmod(path,0o660)


def main():
    if os.environ.get('ADA_DECISIONS_ENABLED')!='true':
        print('{"status":"DISABLED"}')
        return 0
    try:
        gateway=Gateway(provider=AgiflowReader(os.environ['AGIFLOW_MCP_URL'],os.environ['AGIFLOW_API_KEY']),
            core=ControlCore(os.environ.get('CONTROL_CORE_URL','http://127.0.0.1:8770'),os.environ['CONTROL_API_TOKEN']),
            enabled=True,bot_uid=int(os.environ['ADA_BOT_UID']),user_id=int(os.environ['ADA_OPERATOR_USER_ID']),
            chat_id=int(os.environ['ADA_OPERATOR_CHAT_ID']),bot_id=int(os.environ['ADA_TELEGRAM_BOT_ID']),
            actor=os.environ['ADA_OPERATOR_LABEL'])
        path=Path('/run/ada-decision-gateway/decision.sock')
        # systemd owns the private runtime directory. Never remove arbitrary paths.
        if path.exists():
            if not stat.S_ISSOCK(path.lstat().st_mode) or path.stat().st_uid!=os.getuid():
                raise DecisionError('SOCKET_PATH_UNSAFE')
            path.unlink()
        with DecisionServer(str(path),gateway) as server: server.serve_forever()
    except Exception:
        print('{"status":"ERROR","error":"GATEWAY_START_FAILED"}')
        return 1
    return 0


if __name__=='__main__': raise SystemExit(main())
