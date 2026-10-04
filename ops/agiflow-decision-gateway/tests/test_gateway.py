import importlib.util
import json
import os
from pathlib import Path
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import pytest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('decision_gateway', HERE / 'gateway.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

NOW = 1791072000
TASK = {'id': '01M301DZR8YYC491KW6PX96530', 'slug': 'AAX-36', 'projectId': '01M2QCDQ4CDZCHVGT5PKCBVDQM', 'revision': 1}

def command(**changes):
    value = dict(update_id=99, date=NOW, user_id=200, chat_id=100, task='AAX-36', decision='Use the existing queue', rationale='Preserve one durable owner')
    value.update(changes)
    return value

class Provider:
    def __init__(self): self.calls=[]; self.task=dict(TASK)
    def get_task(self, slug):
        self.calls.append(slug)
        return dict(TASK,slug=slug,id=g.ANCHORS[slug]) if slug in g.ANCHORS else dict(self.task)

class Core:
    def __init__(self): self.rows={}; self.calls=[]
    def enqueue(self, body):
        self.calls.append(body)
        row=dict(body, id='queue-id', status='pending', payload_json=json.dumps(body['payload']))
        row.pop('payload')
        return self.rows.setdefault(body['idempotency_key'],row)

def gateway(**changes):
    config=dict(enabled=True, bot_uid=os.getuid(), user_id=200, chat_id=100, bot_id=300, actor='Maziyar')
    config.update(changes)
    return g.Gateway(provider=Provider(), core=Core(), clock=lambda:NOW, **config)

def test_deterministic_retry_queues_one_exact_consumer_payload():
    gw=gateway()
    first=gw.submit(command(),os.getuid()); second=gw.submit(command(),os.getuid())
    assert first == second
    assert first['status']=='QUEUED' and len(gw.core.rows)==1
    body=gw.core.calls[0]
    assert body['entity_id']==TASK['id']
    assert body['entity_type']=='task_comment' and body['operation']=='create_task_comment'
    assert body['payload']['content'].endswith('[sync:'+body['idempotency_key']+']')
    assert body['payload']==gw.core.calls[1]['payload']
    assert 'user_id' not in body['payload'] and 'chat_id' not in body['payload']

@pytest.mark.parametrize('change',[{'user_id':201},{'chat_id':101},{'task':'AAX-0'},{'task':'OTHER-36'},{'update_id':True},{'date':NOW+61},{'date':NOW-86401},{'decision':''},{'decision':'x'*2001},{'rationale':'[sync:evil]'}, {'extra':'anything'}])
def test_invalid_input_never_contacts_upstream(change):
    gw=gateway()
    with pytest.raises(g.DecisionError): gw.submit(command(**change),os.getuid())
    assert gw.core.calls==[] and gw.provider.calls==[]

def test_disabled_and_wrong_peer_never_contact_upstream():
    for gw,uid in [(gateway(enabled=False),os.getuid()),(gateway(),os.getuid()+1)]:
        with pytest.raises(g.DecisionError): gw.submit(command(),uid)
        assert not gw.core.calls and not gw.provider.calls

@pytest.mark.parametrize('change',[{'projectId':'foreign'},{'slug':'AAX-37'},{'id':'bad'},{'revision':None}])
def test_incorrect_fresh_task_resolution_never_queues(change):
    gw=gateway(); gw.provider.task.update(change)
    with pytest.raises(g.DecisionError): gw.submit(command(),os.getuid())
    assert not gw.core.calls

def test_key_collision_fails_closed_and_never_overwrites():
    gw=gateway(); gw.submit(command(),os.getuid())
    with pytest.raises(g.DecisionError,match='RECEIPT_MISMATCH'): gw.submit(command(decision='Different'),os.getuid())
    assert len(gw.core.rows)==1

def test_secrets_redacted_before_core():
    gw=gateway(); gw.submit(command(decision='token=PRIVATE_VALUE password=MORE_PRIVATE',rationale='Email owner@example.com'),os.getuid())
    text=json.dumps(gw.core.calls)
    assert 'PRIVATE_VALUE' not in text and 'MORE_PRIVATE' not in text and 'owner@example.com' not in text
    assert '[REDACTED]' in text

def test_upstream_failure_has_content_free_error():
    gw=gateway()
    def fail(_): raise RuntimeError('PRIVATE_PROVIDER_BODY')
    gw.provider.get_task=fail
    with pytest.raises(g.DecisionError) as caught: gw.submit(command(),os.getuid())
    assert 'PRIVATE' not in str(caught.value) and not gw.core.calls

@pytest.mark.parametrize('status',['conflict','quarantined','dead','unexpected'])
def test_non_delivery_states_are_not_reported_queued(status):
    gw=gateway(); gw.submit(command(),os.getuid())
    next(iter(gw.core.rows.values()))['status']=status
    with pytest.raises(g.DecisionError): gw.submit(command(),os.getuid())

def test_real_socket_fake_http_round_trip_and_retry(tmp_path):
    rows={}; requests=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            requests.append((self.path,body))
            if self.path=='/mcp':
                slug=body['params']['arguments']['id']
                task=dict(TASK,slug=slug,id=g.ANCHORS[slug]) if slug in g.ANCHORS else TASK
                result={'jsonrpc':'2.0','id':body['id'],'result':{'structuredContent':{'task':task}}}
            else:
                assert self.path=='/external-sync' and self.headers['Authorization']=='Bearer fixture'
                row=dict(body,id='queue-id',status='pending',payload_json=json.dumps(body['payload'])); row.pop('payload')
                result=rows.setdefault(body['idempotency_key'],row)
            raw=json.dumps(result).encode(); self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    http=HTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
    url='http://127.0.0.1:'+str(http.server_port)
    gw=gateway();gw.provider=g.AgiflowReader(url+'/mcp','fixture',allow_test_http=True);gw.core=g.ControlCore(url,'fixture')
    server=g.DecisionServer(str(tmp_path/'gateway.sock'),gw)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    try:
        for _ in range(2):
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as client:
                client.connect(str(tmp_path/'gateway.sock'));client.sendall(json.dumps(command()).encode()+b'\n')
                assert json.loads(client.makefile('rb').readline())['status']=='QUEUED'
        bot_spec=importlib.util.spec_from_file_location('gateway_integration_bot',HERE.parent/'ada-telegram-bot'/'bot.py')
        bot=importlib.util.module_from_spec(bot_spec);bot_spec.loader.exec_module(bot)
        bot.DECISIONS_ENABLED=True;bot.DECISION_SOCKET=str(tmp_path/'gateway.sock')
        reply=bot.queue_decision({'update_id':99,'message':{'date':NOW,'from':{'id':200},'chat':{'id':100},
            'text':'/decision AAX-36 | Use the existing queue | Preserve one durable owner'}})
        assert 'تأیید نشده' in reply
        assert len(rows)==1 and len(requests)==12
    finally:
        server.shutdown();server.server_close();http.shutdown();http.server_close()

@pytest.mark.parametrize('status',['pending','in_progress','succeeded'])
def test_actual_core_states_remain_queue_receipts(status):
    gw=gateway();gw.submit(command(),os.getuid())
    next(iter(gw.core.rows.values()))['status']=status
    assert gw.submit(command(),os.getuid())['status']=='QUEUED'


def test_committed_core_response_loss_retries_same_row():
    gw=gateway(); original=gw.core.enqueue
    def lose_response(body):
        original(body)
        raise TimeoutError('PRIVATE_RESPONSE')
    gw.core.enqueue=lose_response
    with pytest.raises(g.DecisionError,match='UPSTREAM_UNAVAILABLE'):gw.submit(command(),os.getuid())
    gw.core.enqueue=original
    assert gw.submit(command(),os.getuid())['status']=='QUEUED' and len(gw.core.rows)==1


def test_producer_payload_runs_through_actual_consumer_without_local_mirror():
    import sys
    path=HERE.parent/'agiflow-consumer'/'agiflow_external_sync_consumer.py'
    spec=importlib.util.spec_from_file_location('decision_test_consumer',path)
    consumer=importlib.util.module_from_spec(spec);sys.modules[spec.name]=consumer;spec.loader.exec_module(consumer)
    gw=gateway();gw.submit(command(),os.getuid());row=next(iter(gw.core.rows.values()))
    class Queue:
        def claim(self):return row
        def ack(self,target,outcome,**kwargs):return {'status':outcome}
    class Agiflow:
        def __init__(self):self.comments=[]
        def probe(self):return {}
        def list_comments(self,*args,**kwargs):return self.comments
        def create_comment(self,task_id,content):self.comments.append({'id':'fixture-comment','content':content})
    provider=Agiflow()
    assert consumer.consume_one(Queue(),provider,enabled=True,mirror=False)['status']=='SUCCEEDED'
    assert consumer.consume_one(Queue(),provider,enabled=True,mirror=False)['status']=='DEDUPED_EXISTING'
    assert len(provider.comments)==1


def test_strict_json_rejects_duplicate_security_fields():
    with pytest.raises(g.DecisionError):g.strict_json('{"user_id":200,"user_id":201}')


def test_supported_mcp_error_does_not_expose_body(monkeypatch):
    monkeypatch.setattr(g,'post_json',lambda *args,**kwargs:{'id':1,'result':{'isError':True,'content':[{'type':'text','text':'PRIVATE_ERROR'}]}})
    with pytest.raises(g.DecisionError,match='AGIFLOW_READ_INVALID'):
        g.AgiflowReader('https://fixture.invalid/mcp','fixture').get_task('AAX-36')


def test_secret_shapes_are_removed():
    for text in ['https://user:private@host.invalid/path','github_pat_123456789abcdefghijk','-----BEGIN PRIVATE KEY-----\nprivate\n-----END PRIVATE KEY-----']:
        assert g.clean(text)=='[REDACTED]'


def test_missing_anchor_prevents_enqueue():
    gw=gateway(); original=gw.provider.get_task
    gw.provider.get_task=lambda slug: {} if slug=='AAX-26' else original(slug)
    with pytest.raises(g.DecisionError,match='TASK_CONTEXT_INVALID'):gw.submit(command(),os.getuid())
    assert not gw.core.calls

def test_agiflow_reader_accepts_matching_mcp_sse():
    seen={}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            seen['accept']=self.headers.get('Accept')
            request=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            task=dict(TASK)
            payload={'jsonrpc':'2.0','id':request['id'],'result':{'structuredContent':{'task':task}}}
            raw=(b': keepalive\n\n'
                 b'data: {"jsonrpc":"2.0","method":"notifications/progress","params":{}}\n\n'
                 + b'event: message\ndata: '+json.dumps(payload).encode()+b'\n\n')
            self.send_response(200)
            self.send_header('Content-Type','text/event-stream; charset=utf-8')
            self.send_header('Content-Length',str(len(raw)))
            self.end_headers(); self.wfile.write(raw)
    http=HTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
    try:
        reader=g.AgiflowReader('http://127.0.0.1:'+str(http.server_port)+'/mcp','fixture',allow_test_http=True)
        assert reader.get_task('AAX-36')==TASK
        assert 'application/json' in seen['accept'] and 'text/event-stream' in seen['accept']
    finally:
        http.shutdown();http.server_close()


def test_sse_duplicate_matching_jsonrpc_is_rejected():
    payload=json.dumps({'jsonrpc':'2.0','id':1,'result':{}}).encode()
    raw=b'data: '+payload+b'\n\n'+b'data: '+payload+b'\n\n'
    with pytest.raises(g.DecisionError,match='UPSTREAM_RESPONSE_INVALID'):
        g.parse_sse_jsonrpc(raw,1)


def test_control_core_receipt_parser_remains_json_only():
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            raw=b'data: {"jsonrpc":"2.0","id":1,"result":{}}\n\n'
            self.send_response(200)
            self.send_header('Content-Type','text/event-stream')
            self.send_header('Content-Length',str(len(raw)))
            self.end_headers(); self.wfile.write(raw)
    http=HTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
    try:
        core=g.ControlCore('http://127.0.0.1:'+str(http.server_port),'fixture')
        with pytest.raises(g.DecisionError,match='UPSTREAM_RESPONSE_INVALID'):
            core.enqueue({'fixture':True})
    finally:
        http.shutdown();http.server_close()

def test_gateway_service_recovers_failures_without_infinite_clean_exit_loop():
    unit=(HERE/'ada-decision-gateway.service').read_text()
    assert 'Restart=on-failure' in unit
    assert 'RestartSec=5s' in unit
    assert 'StartLimitIntervalSec=300' in unit
    assert 'StartLimitBurst=5' in unit
    assert 'Restart=always' not in unit

def test_installer_rejects_unsafe_preexisting_gateway_account_contract():
    script=(HERE/'install.sh').read_text()
    assert '[ "$gateway_uid" -ne 0 ]' in script
    assert '[ "$gateway_gid" -eq "$expected_gid" ]' in script
    assert 'Gateway account must use a non-login shell.' in script
    assert '[ "$gateway_groups" = "$expected_gid" ]' in script
    assert 'Gateway UID must not be shared.' in script

