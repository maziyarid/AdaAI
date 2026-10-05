import importlib.util
import pathlib
import tempfile
import unittest
from unittest import mock

HERE=pathlib.Path(__file__).resolve().parent
CLI=HERE/"ada-google-approval"

class ApprovalCliTests(unittest.TestCase):
    def load(self):
        spec=importlib.util.spec_from_file_location("approval_cli",CLI)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_source_has_human_token_only_and_no_proof_consume_actions(self):
        source=CLI.read_text(encoding="utf-8")
        self.assertIn("CONTROL_APPROVAL_TOKEN",source)
        self.assertNotIn("CONTROL_MS_ROBOT_TOKEN",source)
        self.assertNotIn("/proof",source)
        self.assertNotIn("/consume",source)

    def test_config_requires_loopback_and_nonempty_token(self):
        cli=self.load()
        with tempfile.TemporaryDirectory() as td:
            path=pathlib.Path(td)/"env"
            path.write_text("CONTROL_APPROVAL_TOKEN=test-human-token\nCONTROL_APPROVAL_URL=http://127.0.0.1:8770\n")
            self.assertEqual(cli.config(str(path)),("http://127.0.0.1:8770","test-human-token"))
            path.write_text("CONTROL_APPROVAL_TOKEN=x\nCONTROL_APPROVAL_URL=https://example.com\n")
            with self.assertRaises(SystemExit): cli.config(str(path))

    def test_grant_uses_human_endpoint_and_never_prints_token(self):
        cli=self.load()
        ticket="123e4567-e89b-42d3-a456-426614174000"
        calls=[]
        def fake(path,method="GET",payload=None,env_path=cli.DEFAULT_ENV):
            calls.append((path,method,payload,env_path))
            return {"ticket_id":ticket,"state":"GRANTED","tool_name":"gtm.version.publish","resource_id":"accounts/1/containers/2"}
        with mock.patch.object(cli,"call",fake), mock.patch("builtins.print") as out:
            self.assertEqual(cli.main(["grant",ticket,"--approver","maziyar"]),0)
        self.assertEqual(calls[0][0],"/approvals/"+ticket+"/grant")
        self.assertEqual(calls[0][1],"POST")
        self.assertEqual(calls[0][2],{"approver":"maziyar"})
        rendered=" ".join(str(call.args) for call in out.call_args_list)
        self.assertNotIn("test-human-token",rendered)

if __name__=="__main__":
    unittest.main()
