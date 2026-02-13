import unittest

from kivai_sdk.adapters.contracts import AdapterResult, normalize_adapter_output


class TestAdapterContractV08(unittest.TestCase):
    def test_normalize_success_dict(self):
        out = {"echo": "hola"}
        res = normalize_adapter_output(out)
        self.assertTrue(res.ok)
        self.assertEqual(res.data, {"echo": "hola"})
        self.assertIsNone(res.error)

    def test_normalize_failure_legacy_dict(self):
        out = {"ok": False, "error": {"code": "ADAPTER_ERROR", "message": "boom"}}
        res = normalize_adapter_output(out)
        self.assertFalse(res.ok)
        self.assertIsNotNone(res.error)
        self.assertEqual(res.error.code, "ADAPTER_ERROR")
        self.assertEqual(res.error.message, "boom")

    def test_normalize_adapter_result_success(self):
        out = AdapterResult.success({"action": "set_temperature", "value": 21.0})
        res = normalize_adapter_output(out)
        self.assertTrue(res.ok)
        self.assertEqual(res.data["action"], "set_temperature")
        self.assertEqual(res.data["value"], 21.0)

    def test_normalize_adapter_result_failure(self):
        out = AdapterResult.failure("DEVICE_OFFLINE", "Device is offline")
        res = normalize_adapter_output(out)
        self.assertFalse(res.ok)
        self.assertIsNotNone(res.error)
        self.assertEqual(res.error.code, "DEVICE_OFFLINE")
        self.assertEqual(res.error.message, "Device is offline")

    def test_normalize_invalid_output_type(self):
        out = "not-a-dict"
        res = normalize_adapter_output(out)
        self.assertFalse(res.ok)
        self.assertIsNotNone(res.error)
        self.assertEqual(res.error.code, "ADAPTER_INVALID_RESULT")
