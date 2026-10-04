import importlib.util
import json
from pathlib import Path
import time
import pytest

BOT=Path(__file__).resolve().parents[1]/'bot.py'

@pytest.fixture
def bot(tmp_path,monkeypatch):
    monkeypatch.setenv('STATE_DIR',str(tmp_path))
    monkeypatch.setenv('ADA_DECISIONS_ENABLED','true')
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN','')
    spec=importlib.util.spec_from_file_location('bot_decision_test',BOT)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.init_db();module.save_identity(100,{'id':200})
    module.sent=[];module.send=lambda c,t:module.sent.append(t)
    return module

def update(**extra):
    value={'update_id':99,'message':{'date':int(time.time()),'chat':{'id':100,'type':'private'},'from':{'id':200},'text':'/decision AAX-36 | Use one queue | Preserve ownership'}}
    value['message'].update(extra)
    return value

def test_explicit_command_uses_gateway_and_never_model(bot):
    calls=[];bot.queue_decision=lambda u:calls.append(u) or 'queued fixture'
    bot.chat_with_ada=lambda _:pytest.fail('decision reached model')
    bot.handle(update())
    assert len(calls)==1 and bot.sent==['queued fixture']

@pytest.mark.parametrize('changes',[{'chat':{'id':100,'type':'group'}},{'from':{'id':201}},{'forward_date':1}])
def test_untrusted_commands_never_reach_gateway(bot,changes):
    bot.queue_decision=lambda _:pytest.fail('untrusted decision')
    bot.handle(update(**changes));assert bot.sent==[]

def test_kill_switch_prevents_gateway(bot):
    bot.queue_decision=lambda _:pytest.fail('disabled decision')
    bot.KILL_SWITCH.touch();bot.handle(update());assert len(bot.sent)==1

def test_pending_retry_reuses_original_update_when_reply_fails(bot):
    calls=[]
    bot.queue_decision=lambda u:calls.append(u) or 'queued fixture'
    def fail(*args): raise RuntimeError('delivery failed')
    bot.send=fail;bot.store_updates([update()]);bot.process_pending()
    bot.send=lambda c,t:bot.sent.append(t);bot.process_pending()
    assert len(calls)==2 and calls[0]==calls[1]
    with bot.db() as c: assert c.execute('select state from inbound').fetchone()[0]=='done'

def test_gateway_failure_retries_with_content_free_durable_error(bot):
    bot.DECISION_SOCKET='/does/not/exist'
    bot.store_updates([update()]);bot.process_pending()
    with bot.db() as c:
        row=c.execute('select state,last_error from inbound').fetchone()
    assert row['state']=='pending' and row['last_error']=='RuntimeError: decision_gateway_unavailable'
    assert not bot.sent

def test_malformed_command_offers_explicit_format_without_gateway(bot):
    bot.DECISION_SOCKET='/does/not/exist'
    bot.handle(update(text='/decision missing fields'))
    assert '/decision AAX-' in bot.sent[-1]


def test_disabled_gate_does_not_contact_socket(bot):
    bot.DECISIONS_ENABLED=False;bot.DECISION_SOCKET='/does/not/exist'
    bot.handle(update());assert 'فعال نیست' in bot.sent[-1]

def fill_rate_limit(bot, count):
    with bot.db() as c:
        c.executemany('insert into rate_events(user_id,ts) values(?,?)',
                      [('200',int(time.time()))]*count)

def pending_row(bot):
    with bot.db() as c:
        return c.execute('select * from inbound where update_id=99').fetchone()

def test_uncertain_gateway_retry_keeps_admission_at_rate_limit(bot):
    calls=[]
    def gateway(u):
        calls.append(u)
        if len(calls)==1: raise RuntimeError('decision_gateway_unavailable')
        return 'queued fixture'
    bot.queue_decision=gateway
    fill_rate_limit(bot,bot.RATE_LIMIT_PER_MIN-1)
    bot.store_updates([update()]);bot.process_pending()
    assert pending_row(bot)['attempts']==1
    bot.init_db()  # Repeated startup migration must retain admission.
    bot.process_pending()
    assert len(calls)==2 and calls[0]==calls[1]
    assert pending_row(bot)['state']=='done'
    another=update();another['update_id']=100
    bot.store_updates([another]);bot.process_pending()
    assert len(calls)==2
    with bot.db() as c:
        assert c.execute('select count(*) from rate_events').fetchone()[0]==bot.RATE_LIMIT_PER_MIN

def test_failed_rate_denial_does_not_admit_retry(bot):
    bot.queue_decision=lambda _:pytest.fail('rate-denied update reached gateway')
    fill_rate_limit(bot,bot.RATE_LIMIT_PER_MIN)
    bot.store_updates([update()])
    def fail(*_): raise RuntimeError('delivery failed')
    bot.send=fail;bot.process_pending()
    bot.send=lambda c,t:bot.sent.append(t);bot.process_pending()
    assert pending_row(bot)['state']=='done'
    assert len(bot.sent)==1

def test_admission_is_bound_to_original_inbound_payload(bot):
    calls=[]
    def gateway(u):
        calls.append(u)
        raise RuntimeError('decision_gateway_unavailable')
    bot.queue_decision=gateway
    original=update();bot.store_updates([original]);bot.process_pending()
    altered=update(text='/decision AAX-36 | Changed decision | Changed rationale')
    bot.store_updates([altered])
    with pytest.raises(RuntimeError,match='decision_update_mismatch'):
        bot.handle(altered)
    bot.process_pending()
    assert calls==[original,original]
    assert json.loads(pending_row(bot)['payload_json'])==original

@pytest.mark.parametrize('gate',['identity','kill','group','forward'])
def test_admitted_retry_rechecks_authentication_and_kill_switch(bot,gate):
    calls=[]
    def gateway(u):
        calls.append(u)
        raise RuntimeError('decision_gateway_unavailable')
    bot.queue_decision=gateway
    original=update();bot.store_updates([original]);bot.process_pending()
    if gate=='identity': bot.save_identity(100,{'id':201})
    elif gate=='kill': bot.KILL_SWITCH.touch()
    elif gate=='group':
        original['message']['chat']['type']='group'
    else: original['message']['forward_date']=1
    bot.handle(original)
    assert len(calls)==1

def test_admission_survives_sqlite_backup_restore(bot,tmp_path):
    calls=[]
    def gateway(u):
        calls.append(u)
        if len(calls)==1: raise RuntimeError('decision_gateway_unavailable')
        return 'queued fixture'
    bot.queue_decision=gateway
    fill_rate_limit(bot,bot.RATE_LIMIT_PER_MIN-1)
    bot.store_updates([update()]);bot.process_pending()
    import sqlite3
    restored=tmp_path/'restored.sqlite3'
    with bot.db() as source, sqlite3.connect(str(restored)) as destination:
        source.backup(destination)
    bot.DB_PATH=restored;bot.init_db();bot.process_pending()
    assert len(calls)==2 and pending_row(bot)['state']=='done'

def test_legacy_inbound_migration_requires_fresh_admission(bot):
    with bot.db() as c:
        c.execute('drop table inbound')
        c.execute("""create table inbound(
            update_id integer primary key,payload_json text not null,
            state text not null default 'pending',attempts integer not null default 0,
            received_at text not null,done_at text,last_error text)""")
    bot.store_updates([update()])
    with bot.db() as c: c.execute('update inbound set attempts=1')
    bot.init_db()
    fill_rate_limit(bot,bot.RATE_LIMIT_PER_MIN)
    bot.queue_decision=lambda _:pytest.fail('legacy attempts inferred admission')
    bot.process_pending()
    assert pending_row(bot)['state']=='done'

def test_leading_whitespace_decision_reaches_gateway(bot):
    bot.DECISION_SOCKET='/does/not/exist'
    with pytest.raises(RuntimeError,match='decision_gateway_unavailable'):
        bot.handle(update(text='  /decision AAX-36 | Use one queue | Preserve ownership'))

def admission_counts(bot):
    with bot.db() as c:
        return (
            c.execute('select count(*) from rate_events').fetchone()[0],
            c.execute('select count(*) from decision_admission').fetchone()[0],
        )

def test_malformed_decision_does_not_consume_shared_rate_or_admission(bot):
    before=admission_counts(bot)
    bot.handle(update(text='/decision missing fields'))
    assert admission_counts(bot)==before
    assert bot.sent and '/decision AAX-' in bot.sent[-1]

def test_disabled_decision_does_not_consume_shared_rate_or_admission(bot):
    bot.DECISIONS_ENABLED=False
    before=admission_counts(bot)
    bot.handle(update())
    assert admission_counts(bot)==before
    assert bot.sent and 'فعال نیست' in bot.sent[-1]

def test_oversized_decision_does_not_consume_shared_rate_or_admission(bot):
    before=admission_counts(bot)
    bot.handle(update(text='/decision AAX-36 | '+('x'*9000)+' | '+('y'*9000)))
    assert admission_counts(bot)==before
    assert bot.sent and 'طولانی' in bot.sent[-1]

