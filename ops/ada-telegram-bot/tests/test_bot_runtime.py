import contextlib, importlib.util, io, os, tempfile, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
BOT=HERE/"bot.py"

class BotRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.state=Path(self.tmp.name)
        self.old_env=os.environ.copy()
        os.environ["STATE_DIR"]=str(self.state)
        os.environ["TELEGRAM_BOT_TOKEN"]=""
        os.environ["TELEGRAM_PAIR_CODE"]="test-pair-code"
        os.environ["ADA_QALAM_RELEASE"]=str(HERE.parents[1]/"skills/qalam/RELEASE.json")
        spec=importlib.util.spec_from_file_location("ada_bot_test",BOT)
        self.bot=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.bot)
        self.bot.init_db()
        self.sent=[]
        self.bot.send=lambda chat_id,text:self.sent.append((int(chat_id),str(text))) or [{"message_id":1}]

    def tearDown(self):
        os.environ.clear(); os.environ.update(self.old_env)
        self.tmp.cleanup()

    def pair(self,chat=100,user=200):
        self.bot.save_identity(chat,{"id":user,"username":"owner"})

    def msg(self,update_id=1,chat=100,user=200,text="/ping",chat_type="private",**extra):
        m={"chat":{"id":chat,"type":chat_type},"from":{"id":user,"username":"owner"},"text":text}
        m.update(extra)
        return {"update_id":update_id,"message":m}

    def test_state_db_mode_is_private(self):
        self.assertEqual(self.bot.DB_PATH.stat().st_mode & 0o777,0o600)

    def test_unknown_numeric_identity_is_denied(self):
        self.pair()
        self.bot.handle(self.msg(user=999))
        self.assertEqual(self.sent,[])

    def test_group_and_forwarded_messages_are_denied(self):
        self.pair()
        self.bot.handle(self.msg(chat_type="group"))
        self.bot.handle(self.msg(update_id=2,forward_date=123))
        self.assertEqual(self.sent,[])

    def test_kill_switch_blocks_nonessential_commands_but_keeps_health(self):
        self.pair()
        self.bot.KILL_SWITCH.touch()
        self.bot.handle(self.msg(text="/status"))
        self.assertIn("غیرفعال",self.sent[-1][1])
        self.bot.handle(self.msg(update_id=2,text="/ping"))
        self.assertEqual(self.sent[-1][1],"pong")

    def test_duplicate_update_id_and_cursor_are_durable(self):
        u=self.msg(update_id=55)
        self.bot.store_updates([u,u])
        with self.bot.db() as c:
            self.assertEqual(c.execute("select count(*) from inbound where update_id=55").fetchone()[0],1)
        self.assertEqual(self.bot.next_update_id(),56)
        self.assertEqual(self.bot.next_update_id(),56)

    def test_outbox_idempotency_and_state_dedupe(self):
        self.assertIsNotNone(self.bot.enqueue_alert("x",idem_key="same"))
        self.assertIsNone(self.bot.enqueue_alert("x",idem_key="same"))
        self.assertIsNotNone(self.bot.enqueue_alert("down",idem_key="state1",fingerprint="svc",alert_state="down"))
        self.assertIsNone(self.bot.enqueue_alert("down-again",idem_key="state2",fingerprint="svc",alert_state="down"))

    def test_outbox_failure_reaches_dead_letter(self):
        self.pair()
        self.bot.MAX_OUTBOX_ATTEMPTS=3
        def fail_send(*_args,**_kwargs):
            raise RuntimeError("provider down")
        self.bot.send=fail_send
        oid=self.bot.enqueue_alert("x",idem_key="retry")
        for _ in range(3):
            with self.bot.db() as c:
                c.execute("update outbox set next_attempt_at=0 where id=?",(oid,))
            self.bot.flush_outbox(100,10)
        with self.bot.db() as c:
            row=c.execute("select status,attempts from outbox where id=?",(oid,)).fetchone()
        self.assertEqual((row["status"],row["attempts"]),("dead",3))

    def test_feedback_is_explicit_redacted_and_deduplicated(self):
        first=self.bot.store_feedback("naturalness","token=abcdefghijklmnop","متن طبیعی","",200,1)
        second=self.bot.store_feedback("naturalness","token=abcdefghijklmnop","متن طبیعی","",200,2)
        self.assertIsNotNone(first)
        self.assertIsNone(second)
        with self.bot.db() as c:
            row=c.execute("select original,status from feedback where id=?",(first,)).fetchone()
        self.assertIn("[REDACTED]",row["original"])
        self.assertEqual(row["status"],"pending_review")

    def test_log_redacts_bearer_and_token_values(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            self.bot.log("test",detail="Bearer abcdefghijklmnop token=abcdefghijklmnop")
        rendered=out.getvalue()
        self.assertNotIn("abcdefghijklmnop",rendered)
        self.assertIn("REDACTED",rendered)

    def test_task_formatter_has_no_action_side_effect(self):
        data={"total":2,"tasks":[
          {"slug":"AAX-1","title":"One","status":"In Progress","priority":"high"},
          {"slug":"AAX-2","title":"Two","status":"Blocked","priority":"medium"},
        ]}
        text=self.bot.format_task_snapshot(data)
        self.assertIn("AAX-1",text)
        self.assertIn("AAX-2",text)
        source=BOT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess.",source)
        self.assertNotIn("os.system(",source)

    def test_tasks_commands_use_read_snapshot_only(self):
        self.pair()
        self.bot.agiflow_snapshot=lambda kind:{"kind":kind,"total":1,"tasks":[{"slug":"AAX-33","title":"Bot","status":"In Progress","priority":"high"}]}
        self.bot.handle(self.msg(text="/tasks"))
        self.assertIn("AAX-33",self.sent[-1][1])
        self.bot.handle(self.msg(update_id=2,text="/blocked"))
        self.assertIn("AAX-33",self.sent[-1][1])

if __name__=="__main__":
    unittest.main()
