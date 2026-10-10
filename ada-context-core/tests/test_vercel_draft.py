"""No dependency installation, DB, provider or network required.

Source wiring tests use explicit framework/HTTP spies, not a Vercel build or
real FastMCP protocol validation.
"""
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VercelDraftTest(unittest.TestCase):
    def setUp(self):
        self.urls = load('service_url', ROOT / 'mcp/service_url.py')

    def test_runtime_binding_read_is_not_cached_at_import(self):
        with patch.dict(os.environ, {'VERCEL': '1', 'ADA_CORE_URL': 'https://first.invalid/'}, clear=True):
            self.assertEqual(self.urls.core_url('/v1/bootstrap'), 'https://first.invalid/v1/bootstrap')
            os.environ['ADA_CORE_URL'] = 'https://second.invalid'
            self.assertEqual(self.urls.core_url('/healthz'), 'https://second.invalid/healthz')

    def test_vercel_missing_binding_fails_closed(self):
        with patch.dict(os.environ, {'VERCEL': '1'}, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'service binding'):
                self.urls.core_url('/healthz')

    def test_existing_standalone_loopback_default_is_preserved(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(self.urls.core_url('/healthz'), 'http://127.0.0.1:8791/healthz')

    def test_real_server_calls_use_binding_and_preserve_auth_header(self):
        calls = []

        class Response:
            def raise_for_status(self): pass
            def json(self): return {'ok': True}

        class Client:
            def __init__(self, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def get(self, url, **kwargs):
                calls.append(('GET', url, kwargs)); return Response()

        class AsyncClient(Client):
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def get(self, url, **kwargs): return super().get(url, **kwargs)
            async def post(self, url, **kwargs):
                calls.append(('POST', url, kwargs)); return Response()

        class MCP:
            def __init__(self, name): pass
            def tool(self, function): return function
            def http_app(self, **kwargs): return kwargs

        modules = {'service_url': self.urls,
                   'httpx': types.SimpleNamespace(Client=Client, AsyncClient=AsyncClient),
                   'fastmcp': types.SimpleNamespace(FastMCP=MCP)}
        env = {'VERCEL': '1', 'ADA_CORE_URL': 'https://bound.invalid/', 'ADA_INTERNAL_API_KEY': 'x'*32}
        with patch.dict(sys.modules, modules), patch.dict(os.environ, env, clear=True):
            server = load('draft_server', ROOT / 'mcp/server.py')
            asyncio.run(server.context_bootstrap('dummy-agent', 'dummy-task'))
            asyncio.run(server.context_validate_receipt('dummy-receipt'))
            server.context_status()
            self.assertEqual([call[:2] for call in calls], [
                ('POST', 'https://bound.invalid/v1/bootstrap'),
                ('GET', 'https://bound.invalid/v1/receipts/dummy-receipt/validate'),
                ('GET', 'https://bound.invalid/healthz')])
            for call in calls[:2]:
                self.assertEqual(call[2]['headers'], {'X-Ada-Internal-Key': 'x'*32})
            with patch.dict(sys.modules, {'server': server}):
                entry = load('draft_entry', ROOT / 'mcp/vercel_entry.py')
                self.assertEqual(entry.app, {'path': '/mcp', 'stateless_http': True})

    def test_config_matches_only_actual_call_and_package_entrypoints(self):
        config = json.loads((ROOT.parent / 'vercel.json').read_text())
        self.assertEqual(config['rewrites'], [])
        self.assertEqual(set(config['services']), {'app', 'mcp'})
        self.assertEqual(config['services']['mcp']['bindings'], [
            {'type': 'service', 'service': 'app', 'format': 'url', 'env': 'ADA_CORE_URL'}])
        for service in config['services'].values():
            module, variable = service['entrypoint'].split(':')
            self.assertTrue((ROOT.parent / service['root'] / (module.replace('.', '/') + '.py')).is_file())
            self.assertEqual(variable, 'app')


if __name__ == '__main__':
    unittest.main()
