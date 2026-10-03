import importlib.util
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

spec=importlib.util.spec_from_file_location('scoped_bridge',Path(__file__).resolve().parents[1]/'bridge.py')
bridge=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class ScopedListingTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        bridge.STATE=Path(self.tmp.name);bridge.DB=bridge.STATE/'events.sqlite3'
        bridge.BRIDGE_TOKEN='disposable-fixture-only';bridge.init_db()
        class QuietHandler(bridge.Handler):
            def log_message(self,*args): pass
        self.server=ThreadingHTTPServer(('127.0.0.1',0),QuietHandler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.addCleanup(self.stop)
        self.url=f'http://127.0.0.1:{self.server.server_port}/v1/events?target=ms_robot&state=queued&limit=1'
        for event_id,project,site in [('aaa','other-project','example.com'),('aab','own-project','other.example'),('zzz','own-project','example.com')]:
            bridge.insert_event({'schema_version':1,'event_id':event_id,'idempotency_key':event_id,'source':'ada','target':'ms_robot','event_type':'ada.alert.queued','project_key':project,'site_key':site,'payload':{'reference':event_id}})
    def stop(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)
    def get(self, suffix='', token=True):
        req=urllib.request.Request(self.url+suffix,headers={'Authorization':'Bearer disposable-fixture-only'} if token else {})
        with urllib.request.urlopen(req,timeout=2) as response: return json.load(response)
    def test_scope_filters_before_limit_and_confirms_exact_scope(self):
        response=self.get('&project_key=own-project&site_key=example.com')
        self.assertEqual([row['event_id'] for row in response['events']],['zzz'])
        self.assertEqual(response['scope'],{'project_key':'own-project','site_key':'example.com'})
        with bridge.db() as db:
            self.assertEqual(db.execute("select count(*) from events where state='queued'").fetchone()[0],3)
    def test_legacy_unscoped_listing_is_unchanged(self):
        response=self.get()
        self.assertEqual([row['event_id'] for row in response['events']],['aaa'])
        self.assertNotIn('scope',response)
    def test_partial_blank_duplicate_and_oversize_scopes_fail_closed(self):
        for suffix in ['&project_key=own-project','&site_key=example.com','&project_key=&site_key=example.com','&project_key=own-project&site_key=example.com&project_key=other-project','&project_key='+('x'*161)+'&site_key=example.com']:
            with self.subTest(suffix=suffix):
                with self.assertRaises(urllib.error.HTTPError) as error: self.get(suffix)
                self.assertEqual(error.exception.code,400)
    def test_scoped_listing_still_requires_authentication(self):
        with self.assertRaises(urllib.error.HTTPError) as error: self.get('&project_key=own-project&site_key=example.com',token=False)
        self.assertEqual(error.exception.code,401)
    def test_transition_decodes_only_the_encoded_event_id_segment(self):
        from urllib.parse import quote
        for action in ['ack','fail']:
            event_id='event:'+action+'/reference'
            bridge.insert_event({'schema_version':1,'event_id':event_id,'idempotency_key':event_id,'source':'ada','target':'ms_robot','event_type':'ada.alert.queued','payload':{'reference':'fixture'}})
            url=self.url.split('/v1/events?')[0]+'/v1/events/'+quote(event_id,safe='')+'/'+action
            req=urllib.request.Request(url,data=b'{}',headers={'Authorization':'Bearer disposable-fixture-only','Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=2) as response: result=json.load(response)
            self.assertEqual(result['event_id'],event_id)
            self.assertEqual(result['state'],'acked' if action=='ack' else 'queued')
            with bridge.db() as db:
                row=db.execute('select state,attempts from events where event_id=?',(event_id,)).fetchone()
                self.assertEqual((row['state'],row['attempts']),('acked',0) if action=='ack' else ('queued',1))

    def lookup(self, event_id='zzz', suffix='&project_key=own-project&site_key=example.com', token=True):
        from urllib.parse import quote
        url=self.url.split('/v1/events?')[0]+'/v1/events/'+quote(event_id,safe='')+'?target=ms_robot'+suffix
        req=urllib.request.Request(url,headers={'Authorization':'Bearer disposable-fixture-only'} if token else {})
        with urllib.request.urlopen(req,timeout=2) as response: return json.load(response)
    def test_scoped_lookup_confirms_acked_identity_without_changing_bridge_state(self):
        with bridge.db() as db:
            db.execute("update events set state='acked',acked_at='2026-10-03T10:00:00+00:00' where event_id='zzz'")
            before=tuple(db.execute("select * from events where event_id='zzz'").fetchone())
        answer=self.lookup()
        self.assertEqual(answer['scope'],{'project_key':'own-project','site_key':'example.com'})
        self.assertEqual(answer['event']['event_id'],'zzz')
        self.assertEqual(answer['event']['state'],'acked')
        self.assertEqual(answer['event']['payload'],{'reference':'zzz'})
        with bridge.db() as db:
            self.assertEqual(tuple(db.execute("select * from events where event_id='zzz'").fetchone()),before)
    def test_lookup_requires_exact_scope_and_auth_and_hides_foreign_identity(self):
        for suffix,expected in [('',400),('&project_key=own-project',400),('&project_key=&site_key=example.com',400),('&project_key=own-project&site_key=example.com&site_key=example.com',400),('&project_key=other-project&site_key=example.com',404)]:
            with self.subTest(suffix=suffix):
                with self.assertRaises(urllib.error.HTTPError) as error:self.lookup(suffix=suffix)
                self.assertEqual(error.exception.code,expected)
        for identity in ['missing','aaa','aab']:
            with self.assertRaises(urllib.error.HTTPError) as error:self.lookup(identity)
            self.assertEqual(error.exception.code,404)
        with self.assertRaises(urllib.error.HTTPError) as error:self.lookup(token=False)
        self.assertEqual(error.exception.code,401)
    def test_lookup_addresses_encoded_id_and_never_returns_last_error(self):
        identity='event:lookup/reference'
        bridge.insert_event({'event_id':identity,'idempotency_key':identity,'source':'ada','target':'ms_robot','event_type':'ada.alert.queued','project_key':'own-project','site_key':'example.com','payload':{'reference':'fixture'}})
        with bridge.db() as db:db.execute("update events set state='dead',last_error='private diagnostic' where event_id=?",(identity,))
        answer=self.lookup(identity)['event']
        self.assertEqual(answer['state'],'dead')
        self.assertNotIn('last_error',answer)
        self.assertNotIn('private diagnostic',json.dumps(answer))

if __name__=='__main__': unittest.main()
