import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("msrobot_bridge",HERE/"bridge.py")
bridge=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        bridge.STATE=Path(self.tmp.name)
        bridge.DB=bridge.STATE/"events.sqlite3"
        bridge.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def envelope(self, **overrides):
        x={
          "schema_version":1,
          "event_id":"evt-test-00000001",
          "idempotency_key":"idem-test-00000001",
          "source":"ada",
          "target":"ms_robot",
          "event_type":"integration.health",
          "correlation_id":"corr-1",
          "site_key":"teznevise",
          "project_key":"other-infra",
          "sensitivity":"internal",
          "payload":{"state":"healthy"}
        }
        x.update(overrides)
        return x

    def test_insert_and_duplicate_are_idempotent(self):
        first=bridge.insert_event(self.envelope())
        second=bridge.insert_event(self.envelope())
        self.assertTrue(first["accepted"])
        self.assertFalse(first["duplicate"])
        self.assertTrue(second["duplicate"])
        self.assertEqual(first["event_id"],second["event_id"])

    def test_same_idempotency_key_with_different_payload_conflicts(self):
        bridge.insert_event(self.envelope())
        with self.assertRaisesRegex(ValueError,"idempotency_key_payload_conflict"):
            bridge.insert_event(self.envelope(payload={"state":"down"}))

    def test_rejects_secret_like_payload_keys(self):
        with self.assertRaisesRegex(ValueError,"secret_like_payload_key"):
            bridge.validate(self.envelope(payload={"api_key":"do-not-store"}))
        with self.assertRaisesRegex(ValueError,"secret_like_payload_key"):
            bridge.validate(self.envelope(payload={"nested":{"authorization":"bearer"}}))

    def test_rejects_unknown_target_and_oversize_payload(self):
        with self.assertRaisesRegex(ValueError,"unsupported_target"):
            bridge.validate(self.envelope(target="root-shell"))
        with self.assertRaisesRegex(ValueError,"payload_too_large"):
            bridge.validate(self.envelope(payload={"x":"y"*70000}))

    def test_state_file_is_durable_sqlite(self):
        bridge.insert_event(self.envelope())
        self.assertTrue(bridge.DB.exists())
        with bridge.db() as c:
            row=c.execute("select state,target,event_type from events").fetchone()
        self.assertEqual((row["state"],row["target"],row["event_type"]),("queued","ms_robot","integration.health"))

if __name__=="__main__":
    unittest.main()
