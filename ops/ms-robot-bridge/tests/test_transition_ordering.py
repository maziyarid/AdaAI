import importlib.util
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer
from pathlib import Path

spec = importlib.util.spec_from_file_location('ordered_bridge', Path(__file__).resolve().parents[1] / 'bridge.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class TransitionOrderingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        bridge.STATE = Path(self.tmp.name)
        bridge.DB = bridge.STATE / 'events.sqlite3'
        bridge.BRIDGE_TOKEN = 'disposable-ordering-fixture'
        bridge.init_db()
        bridge.insert_event({'event_id': 'ordering-fixture', 'idempotency_key': 'ordering-fixture', 'source': 'ada',
                             'target': 'ms_robot', 'event_type': 'ada.alert.queued', 'payload': {'reference': 'fixture'}})
        class QuietHandler(bridge.Handler):
            def log_message(self, *args): pass
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)
        self.url = f'http://127.0.0.1:{self.server.server_port}/v1/events/ordering-fixture/'
    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
    def post(self, action):
        request = urllib.request.Request(self.url + action, data=b'{}',
            headers={'Authorization': 'Bearer disposable-ordering-fixture', 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as response:
            return response.code, json.load(response)
    def row(self):
        with bridge.db() as connection:
            return dict(connection.execute('select * from events where event_id=?', ('ordering-fixture',)).fetchone())

    def test_ack_is_terminal_and_repeated_ack_is_timestamp_stable(self):
        self.assertEqual(self.post('ack')[0], 200)
        before = self.row()
        # Force a visibly different time so repeated ACK cannot silently retimestamp.
        original = bridge.now
        bridge.now = lambda: '2026-10-04T10:00:00+00:00'
        self.addCleanup(setattr, bridge, 'now', original)
        self.assertEqual(self.post('ack'), (200, {'ok': True, 'event_id': 'ordering-fixture', 'state': 'acked'}))
        for action in ['delivered', 'fail']:
            self.assertEqual(self.post(action)[0], 409)
        self.assertEqual(self.row(), before)

    def test_dead_is_terminal_and_concurrent_failures_do_not_lose_or_exceed_attempt_budget(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            answers = list(pool.map(lambda _: self.post('fail'), range(bridge.MAX_ATTEMPTS)))
        self.assertTrue(all(status == 200 for status, _ in answers))
        self.assertEqual(self.row()['attempts'], bridge.MAX_ATTEMPTS)
        self.assertEqual(self.row()['state'], 'dead')
        before = self.row()
        for action in ['ack', 'delivered', 'fail']:
            self.assertEqual(self.post(action)[0], 409)
        self.assertEqual(self.row(), before)

    def test_duplicate_delivered_is_timestamp_stable_before_ack(self):
        self.assertEqual(self.post('delivered')[0], 200)
        before = self.row()
        original = bridge.now
        bridge.now = lambda: '2026-10-04T10:00:00+00:00'
        self.addCleanup(setattr, bridge, 'now', original)
        self.assertEqual(self.post('delivered')[0], 200)
        self.assertEqual(self.row(), before)
        self.assertEqual(self.post('ack')[0], 200)
        self.assertEqual(self.row()['state'], 'acked')

if __name__ == '__main__':
    unittest.main()
