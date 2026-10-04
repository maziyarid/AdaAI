"""Public-script health regressions using real isolated SQLite state."""
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import sqlite3
import tempfile
import time
import unittest
from unittest.mock import patch

HEALTH = Path(__file__).resolve().parents[1] / "healthcheck.py"


class BotHealthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name)
        self.now = int(time.time())
        self.pid = os.getpid()
        self.ready = {"ready_at": "fixture", "pid": self.pid}
        self.heartbeat = {"epoch": self.now, "pid": self.pid, "state": "running"}
        self.write_status()
        self.make_db()

    def tearDown(self):
        self.tmp.cleanup()

    def write_status(self):
        (self.state / "ready.json").write_text(json.dumps(self.ready))
        (self.state / "heartbeat.json").write_text(json.dumps(self.heartbeat))

    def make_db(self):
        with sqlite3.connect(self.state / "state.sqlite3") as connection:
            connection.executescript("""
                CREATE TABLE inbound(update_id INTEGER PRIMARY KEY, state TEXT);
                CREATE TABLE outbox(id INTEGER PRIMARY KEY, status TEXT);
                INSERT INTO inbound VALUES(1, 'pending'), (2, 'done');
                INSERT INTO outbox VALUES(1, 'queued'), (2, 'dead'), (3, 'sent');
            """)
        os.chmod(self.state / "state.sqlite3", 0o600)

    def check(self):
        # Redirect only the documented default path; never access installed state.
        original = Path
        def scoped_path(value, *parts):
            if str(value) == "/var/lib/ada-telegram-bot":
                return self.state.joinpath(*parts)
            return original(value, *parts)
        output = io.StringIO()
        with patch("pathlib.Path", side_effect=scoped_path), patch("time.time", return_value=self.now):
            with contextlib.redirect_stdout(output):
                try:
                    runpy.run_path(str(HEALTH), run_name="__main__")
                except SystemExit as exc:
                    code = exc.code
                else:
                    code = 0
        return code, json.loads(output.getvalue())

    def assert_unhealthy(self):
        code, payload = self.check()
        self.assertEqual(code, 2)
        self.assertFalse(payload["ok"])
        return payload

    def test_healthy_database_counts_are_read_without_writes(self):
        db = self.state / "state.sqlite3"
        before = db.read_bytes()
        code, result = self.check()
        self.assertEqual(code, 0)
        self.assertTrue(result["ok"])
        self.assertEqual([result[k] for k in ("outbox_queued", "outbox_dead", "inbound_pending")], [1, 1, 1])
        self.assertEqual(db.read_bytes(), before)

    def test_missing_database_stays_missing(self):
        db = self.state / "state.sqlite3"
        db.unlink()
        self.assert_unhealthy()
        self.assertFalse(db.exists())

    def test_status_symlink_is_rejected(self):
        ready = self.state / "ready.json"
        target = self.state / "ready-target.json"
        ready.rename(target)
        ready.symlink_to(target.name)
        result = self.assert_unhealthy()
        self.assertIn("readiness_invalid", result["errors"])

    def test_heartbeat_symlink_is_rejected(self):
        heartbeat = self.state / "heartbeat.json"
        target = self.state / "heartbeat-target.json"
        heartbeat.rename(target)
        heartbeat.symlink_to(target.name)
        result = self.assert_unhealthy()
        self.assertIn("heartbeat_invalid", result["errors"])

    def test_database_symlink_is_rejected_even_when_target_is_valid(self):
        database = self.state / "state.sqlite3"
        target = self.state / "state-target.sqlite3"
        database.rename(target)
        database.symlink_to(target.name)
        result = self.assert_unhealthy()
        self.assertFalse(result["database_ok"])

    def test_corrupt_database_cannot_report_healthy(self):
        (self.state / "state.sqlite3").write_bytes(b"not a sqlite database")
        self.assert_unhealthy()

    def test_missing_queue_schema_cannot_report_healthy(self):
        with sqlite3.connect(self.state / "state.sqlite3") as connection:
            connection.execute("DROP TABLE outbox")
        self.assert_unhealthy()

    def test_malformed_readiness_cannot_report_healthy(self):
        (self.state / "ready.json").write_text("not-json")
        self.assert_unhealthy()

    def test_different_process_readiness_cannot_report_healthy(self):
        self.ready["pid"] += 1
        self.write_status()
        self.assert_unhealthy()

    def test_future_heartbeat_cannot_report_healthy(self):
        self.heartbeat["epoch"] = self.now + 10
        self.write_status()
        self.assert_unhealthy()

    def test_boolean_heartbeat_epoch_cannot_report_healthy(self):
        self.now = 1
        self.heartbeat["epoch"] = True
        self.write_status()
        self.assert_unhealthy()

    def test_stale_heartbeat_and_stopped_state_are_unhealthy(self):
        self.heartbeat["epoch"] = self.now - 91
        self.write_status()
        self.assert_unhealthy()
        self.heartbeat.update(epoch=self.now, state="stopped")
        self.write_status()
        self.assert_unhealthy()

    def test_readable_by_other_users_database_is_unhealthy(self):
        os.chmod(self.state / "state.sqlite3", 0o644)
        self.assert_unhealthy()

    def test_degraded_process_remains_visible_with_healthy_storage(self):
        self.heartbeat["state"] = "degraded"
        self.write_status()
        code, result = self.check()
        self.assertEqual(code, 0)
        self.assertEqual(result["state"], "degraded")

    def test_missing_readiness_is_unhealthy(self):
        (self.state / "ready.json").unlink()
        self.assert_unhealthy()

    def test_dead_process_is_unhealthy(self):
        self.pid = 99999999
        self.ready["pid"] = self.pid
        self.heartbeat["pid"] = self.pid
        self.write_status()
        self.assert_unhealthy()

    def test_read_only_health_sees_committed_wal_receipts(self):
        connection = sqlite3.connect(self.state / "state.sqlite3")
        try:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("INSERT INTO outbox VALUES(4, 'queued')")
            connection.commit()
            self.assertTrue((self.state / "state.sqlite3-wal").exists())
            code, result = self.check()
            self.assertEqual(code, 0)
            self.assertEqual(result["outbox_queued"], 2)
        finally:
            connection.close()

    def test_database_query_budget_fails_closed(self):
        with sqlite3.connect(self.state / "state.sqlite3") as connection:
            connection.executemany("INSERT INTO outbox VALUES(?, 'queued')", ((i,) for i in range(4, 2004)))
        with patch("time.monotonic", side_effect=[0.0] + [3.0] * 100):
            result = self.assert_unhealthy()
        self.assertFalse(result["database_ok"])
        self.assertIsNone(result["outbox_queued"])

    def test_invalid_status_does_not_leak_its_contents(self):
        (self.state / "heartbeat.json").write_text("private fixture text")
        result = self.assert_unhealthy()
        self.assertNotIn("private fixture text", json.dumps(result))

    def test_deeply_nested_readiness_fails_with_json_diagnostic(self):
        nested = "[" * 1200 + "0" + "]" * 1200
        text = json.dumps(self.ready)[:-1] + ', "unused":' + nested + "}"
        (self.state / "ready.json").write_text(text)
        result = self.assert_unhealthy()
        self.assertIn("readiness_invalid", result["errors"])

    def test_deeply_nested_heartbeat_fails_with_json_diagnostic(self):
        nested = "[" * 1200 + "0" + "]" * 1200
        text = json.dumps(self.heartbeat)[:-1] + ', "unused":' + nested + "}"
        (self.state / "heartbeat.json").write_text(text)
        result = self.assert_unhealthy()
        self.assertIn("heartbeat_invalid", result["errors"])

    def test_status_nesting_over_64_containers_fails_closed(self):
        # Root object plus 64 arrays exceeds the explicit application limit,
        # independently of the interpreter's JSON recursion allowance.
        nested = "[" * 64 + "0" + "]" * 64
        for name, value, category in (
            ("ready.json", self.ready, "readiness_invalid"),
            ("heartbeat.json", self.heartbeat, "heartbeat_invalid"),
        ):
            with self.subTest(name=name):
                self.write_status()
                text = json.dumps(value)[:-1] + ', "unused":' + nested + "}"
                path = self.state / name
                path.write_text(text)
                result = self.assert_unhealthy()
                self.assertIn(category, result["errors"])
                self.assertEqual(path.read_text(), text)

    def test_status_nesting_at_64_containers_is_accepted(self):
        nested = "[" * 63 + "0" + "]" * 63
        text = json.dumps(self.ready)[:-1] + ', "unused":' + nested + "}"
        (self.state / "ready.json").write_text(text)
        code, result = self.check()
        self.assertEqual(code, 0)
        self.assertTrue(result["ok"])

    def test_mixed_object_array_nesting_is_bounded(self):
        nested = '{"a":[' * 32 + "0" + "]}" * 32
        text = json.dumps(self.heartbeat)[:-1] + ', "unused":' + nested + "}"
        (self.state / "heartbeat.json").write_text(text)
        result = self.assert_unhealthy()
        self.assertIn("heartbeat_invalid", result["errors"])

    def test_brackets_in_status_strings_do_not_count_as_nesting(self):
        self.ready["unused"] = ('[{"escaped": "\\"}]' * 100)
        self.write_status()
        code, result = self.check()
        self.assertEqual(code, 0)
        self.assertTrue(result["ok"])

    def test_duplicate_keys_cannot_hide_overdeep_status_values(self):
        for name, value, category in (
            ("ready.json", self.ready, "readiness_invalid"),
            ("heartbeat.json", self.heartbeat, "heartbeat_invalid"),
        ):
            for depth in (64, 1200):
                with self.subTest(name=name, depth=depth):
                    self.write_status()
                    nested = "[" * depth + "0" + "]" * depth
                    text = json.dumps(value)[:-1] + ', "unused":' + nested + ', "unused":0}'
                    path = self.state / name
                    path.write_text(text)
                    self.assertLess(len(text.encode()), 4096)
                    result = self.assert_unhealthy()
                    self.assertIn(category, result["errors"])
                    self.assertEqual(path.read_text(), text)

    def test_duplicate_status_members_fail_closed_at_every_depth(self):
        for suffix in (
            ', "pid":' + str(self.pid) + "}",
            ', "\\u0070id":' + str(self.pid) + "}",
            ', "unused":{"name":1,"name":2}}',
        ):
            with self.subTest(suffix=suffix):
                (self.state / "ready.json").write_text(json.dumps(self.ready)[:-1] + suffix)
                result = self.assert_unhealthy()
                self.assertIn("readiness_invalid", result["errors"])


if __name__ == "__main__":
    unittest.main()
