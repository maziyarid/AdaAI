"""Offline dataset governance tests; no real conversations or provider jobs."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[1]

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class FeedbackExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.state=Path(self.tmp.name)
        self.env=patch.dict(os.environ,{"STATE_DIR":str(self.state),
            "TELEGRAM_BOT_TOKEN":"","ADA_QALAM_RELEASE":str(HERE.parents[1]/"skills/qalam/RELEASE.json")})
        self.env.start()
        self.bot=load_module("export_bot_fixture",HERE/"bot.py")
        self.bot.init_db()
        self.admin=load_module("feedback_admin_fixture",HERE/"feedback_admin.py")

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def seed(self,original="Original prompt",preferred="Preferred reply",status="approved",
             fingerprint=None,qalam=None):
        fp=fingerprint or hashlib.sha256((original+preferred).encode()).hexdigest()
        with self.bot.db() as c:
            cur=c.execute("""INSERT INTO feedback(category,original,preferred,reason,status,created_at,
                actor_user_id,source_update_id,qalam_version,fingerprint)
                VALUES('naturalness',?,?, 'Explicit fixture feedback',?,'2026-10-04T00:00:00+00:00',
                'PRIVATE_ACTOR_999',1,?,?)""",(original,preferred,status,qalam or self.bot.QALAM_VERSION,fp))
            return cur.lastrowid

    def export(self,version):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            self.admin.export(version)
        return json.loads(output.getvalue())

    def rows(self,version):
        result=[]
        for split in ("train","dev","eval"):
            with (self.admin.DATASETS/version/(split+".jsonl")).open() as f:
                result.extend(json.loads(line) for line in f if line.strip())
        return result

    def test_only_approved_explicit_feedback_is_exported(self):
        approved=self.seed()
        self.seed(preferred="Pending",status="pending_review")
        self.seed(preferred="Rejected",status="rejected")
        self.bot.store_updates([{"update_id":33,"message":{"text":"PRIVATE_RAW_CHAT_999"}}])
        manifest=self.export("approved-only")
        self.assertEqual(manifest["record_count"],1)
        self.assertEqual([r["id"] for r in self.rows("approved-only")],[approved])
        rendered="".join(p.read_text() for p in (self.admin.DATASETS/"approved-only").iterdir())
        self.assertNotIn("PRIVATE_RAW_CHAT_999",rendered)
        self.assertNotIn("PRIVATE_ACTOR_999",rendered)

    def test_same_prompt_revisions_stay_in_one_split(self):
        self.seed(fingerprint="00"*32)
        self.seed(preferred="Revised answer",fingerprint="ff"*32,qalam="router@future+bible@future")
        self.export("grouped")
        rows=self.rows("grouped")
        self.assertEqual(len(rows),2)
        self.assertEqual(len({r["split"] for r in rows}),1)
        self.assertEqual(len({r["split_group"] for r in rows}),1)

    def test_equivalent_whitespace_case_and_unicode_prompts_stay_together(self):
        self.seed(original="Hello  Ada",fingerprint="00"*32)
        self.seed(original="  HELLO\tＡｄａ  ",preferred="Second",fingerprint="ff"*32)
        self.export("normalised")
        rows=self.rows("normalised")
        self.assertEqual(len({r["split"] for r in rows}),1)
        self.assertEqual(len({r["split_group"] for r in rows}),1)

    def test_export_files_and_hashes_are_deterministic_and_private(self):
        self.seed()
        first=self.export("one")
        second=self.export("two")
        self.assertEqual(first["files"],second["files"])
        for version in ("one","two"):
            folder=self.admin.DATASETS/version
            self.assertEqual(folder.stat().st_mode & 0o777,0o700)
            for path in folder.iterdir():
                self.assertEqual(path.stat().st_mode & 0o777,0o600)
            manifest=json.loads((folder/"manifest.json").read_text())
            for split,info in manifest["files"].items():
                self.assertEqual(hashlib.sha256((folder/info["file"]).read_bytes()).hexdigest(),info["sha256"])
                self.assertEqual(len([r for r in self.rows(version) if r["split"]==split]),info["count"])

    def test_rejection_affects_future_versions_and_preserves_old_release(self):
        fid=self.seed()
        keep=self.seed(original="Different prompt",preferred="Keep")
        self.export("before")
        before={p.name:p.read_bytes() for p in (self.admin.DATASETS/"before").iterdir()}
        with contextlib.redirect_stdout(io.StringIO()):
            self.admin.set_status(fid,"rejected")
        self.export("after")
        self.assertEqual([r["id"] for r in self.rows("after")],[keep])
        self.assertEqual(before,{p.name:p.read_bytes() for p in (self.admin.DATASETS/"before").iterdir()})

    def test_existing_version_is_never_overwritten(self):
        self.seed()
        self.export("immutable")
        before={p.name:p.read_bytes() for p in (self.admin.DATASETS/"immutable").iterdir()}
        with self.assertRaisesRegex(SystemExit,"already exists"):
            self.export("immutable")
        self.assertEqual(before,{p.name:p.read_bytes() for p in (self.admin.DATASETS/"immutable").iterdir()})

    def test_failed_export_does_not_publish_partial_release_and_can_retry(self):
        self.seed()
        with patch.object(self.admin,"sha",side_effect=OSError("fixture write failure")):
            with self.assertRaises(OSError):
                self.export("recoverable")
        self.assertFalse((self.admin.DATASETS/"recoverable").exists())
        self.assertFalse(list(self.admin.DATASETS.glob(".export-*")))
        self.assertEqual(self.export("recoverable")["record_count"],1)

    def test_empty_approved_set_does_not_create_release(self):
        self.seed(status="pending_review")
        with self.assertRaisesRegex(SystemExit,"no approved"):
            self.export("empty")
        self.assertFalse((self.admin.DATASETS/"empty").exists())

    def test_dot_directory_versions_are_invalid(self):
        self.seed()
        for version in (".",".."):
            with self.subTest(version=version):
                with self.assertRaisesRegex(SystemExit,"invalid version"):
                    self.export(version)

    def test_manifest_names_grouping_and_approval_policy(self):
        self.seed()
        manifest=self.export("policy")
        self.assertEqual(manifest["schema"],"ada.feedback.dataset/v2")
        self.assertEqual(manifest["split_policy"],"sha256-nfkc-casefold-whitespace-original/v1")
        self.assertIn("approved-only",manifest["policy"])
        self.assertIn("no automatic promotion",manifest["policy"])

    def test_parallel_exporters_publish_one_complete_immutable_release(self):
        self.seed()
        commands=[sys.executable,str(HERE/"feedback_admin.py"),"export","concurrent"]
        env={"STATE_DIR":str(self.state),"PATH":os.defpath}
        first=subprocess.Popen(commands,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        second=subprocess.Popen(commands,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            first_output,first_error=first.communicate(timeout=10)
            second_output,second_error=second.communicate(timeout=10)
        finally:
            for process in (first,second):
                if process.poll() is None:
                    process.kill()
                    process.communicate()
        self.assertEqual(sorted([first.returncode,second.returncode]),[0,1])
        self.assertEqual(len(self.rows("concurrent")),1)
        output=first_output if first.returncode==0 else second_output
        error=second_error if first.returncode==0 else first_error
        manifest=json.loads(output)
        self.assertEqual(manifest["record_count"],1)
        self.assertIn(b"already exists",error)
        self.assertFalse(list(self.admin.DATASETS.glob(".export-*")))

    def test_broken_symlink_version_is_not_replaced(self):
        self.seed()
        self.admin.DATASETS.mkdir(mode=0o700)
        destination=self.admin.DATASETS/"symlink"
        destination.symlink_to(self.state/"missing-target",target_is_directory=True)
        with self.assertRaisesRegex(SystemExit,"already exists"):
            self.export("symlink")
        self.assertTrue(destination.is_symlink())

    def test_published_release_reports_unconfirmed_durability_without_overwrite(self):
        self.seed()
        real_sync=self.admin.sync_directory
        def fail_parent(path):
            if path==self.admin.DATASETS:
                raise OSError("PRIVATE_STORAGE_DETAIL")
            return real_sync(path)
        with patch.object(self.admin,"sync_directory",side_effect=fail_parent):
            with self.assertRaisesRegex(SystemExit,"durability is unconfirmed") as caught:
                self.export("uncertain")
        self.assertNotIn("PRIVATE_STORAGE_DETAIL",str(caught.exception))
        folder=self.admin.DATASETS/"uncertain"
        manifest=json.loads((folder/"manifest.json").read_text())
        self.assertEqual(len(self.rows("uncertain")),1)
        for info in manifest["files"].values():
            self.assertEqual(hashlib.sha256((folder/info["file"]).read_bytes()).hexdigest(),info["sha256"])
        self.assertFalse(list(self.admin.DATASETS.glob(".export-*")))
        with self.assertRaisesRegex(SystemExit,"already exists"):
            self.export("uncertain")

if __name__=="__main__":
    unittest.main()
