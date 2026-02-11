import unittest

from kivai_sdk.adapters import AdapterContext, default_registry


class TestAdaptersV02(unittest.TestCase):
    def test_registry_resolves_echo(self):
        reg = default_registry()
        adapter = reg.resolve("echo")
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.intent, "echo")

    def test_echo_adapter_execute(self):
        reg = default_registry()
        adapter = reg.resolve("echo")
        ctx = AdapterContext(gateway_id="test-gw")
        result = adapter.execute({"intent": "echo", "message": "hola"}, ctx)
        self.assertEqual(result["echo"], "hola")
        self.assertEqual(result["gateway_id"], "test-gw")
