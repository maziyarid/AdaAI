"""Offline recovery proof through the existing online backup command."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]


def load_bot(state):
    with patch.dict(os.environ, {
        "STATE_DIR": str(state), "TELEGRAM_BOT_TOKEN": "",
        "ADA_QALAM_RELEASE": str(HERE.parents[1] / "skills/qalam/RELEASE.json"),
    }):
        spec = importlib.util.spec_from_file_location("ada_restore_fixture", HERE / "bot.py")
        bot = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot)
    return bot


class StateRestoreTests(unittest.TestCase):
    def test_online_backup_restore_preserves_cursor_and_duplicate_prevention(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = load_bot(root / "source")
            source.init_db()
            source.store_updates([{
                "update_id": 55, "message": {
                    "chat": {"id": 100, "type": "private"},
                    "from": {"id": 200}, "text": "/ping",
                },
            }])
            alert_id = source.enqueue_alert("synthetic recovery fixture", idem_key="restore-fixture")
            feedback_id = source.store_feedback("wording", "synthetic original", "synthetic preferred", "", 200, 55)
            source.save_identity(100, {"id": 200, "username": "fixture"})

            command = runpy.run_path(str(HERE / "bin/ada-botctl"))
            backup = command["backup"]
            backup.__globals__.update(
                DB=source.DB_PATH, BACKUPS=root / "backups",
                require_root=lambda: None,  # isolate the root-only CLI boundary
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(backup(), 0)
            snapshot = Path(output.getvalue().strip())
            self.assertEqual(snapshot.stat().st_mode & 0o777, 0o600)
            self.assertFalse((snapshot.parent / "allowed_identity.json").exists())

            restored_dir = root / "restored"
            restored_dir.mkdir()
            restored_file = restored_dir / "state.sqlite3"
            with sqlite3.connect(snapshot) as src, sqlite3.connect(restored_file) as dst:
                src.backup(dst)
                self.assertEqual(dst.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            os.chmod(restored_file, 0o600)
            restored = load_bot(restored_dir)
            restored.init_db()
            self.assertEqual(restored.next_update_id(), 56)
            self.assertIsNone(restored.enqueue_alert("synthetic recovery fixture", idem_key="restore-fixture"))
            self.assertIsNone(restored.store_feedback("wording", "synthetic original", "synthetic preferred", "", 200, 55))
            with restored.db() as connection:
                self.assertEqual(connection.execute("SELECT count(*) FROM inbound WHERE update_id=55").fetchone()[0], 1)
                row = connection.execute("SELECT status,attempts FROM outbox WHERE id=?", (alert_id,)).fetchone()
                self.assertEqual((row["status"], row["attempts"]), ("queued", 0))
                self.assertEqual(connection.execute("SELECT status FROM feedback WHERE id=?", (feedback_id,)).fetchone()[0], "pending_review")
            # Pairing and runtime readiness are separate protected files:
            # restoring SQLite alone must never reactivate delivery.
            self.assertFalse(restored.identity())
            self.assertFalse(restored.READY_FILE.exists())
            self.assertFalse(restored.HEARTBEAT_FILE.exists())


if __name__ == "__main__":
    unittest.main()
