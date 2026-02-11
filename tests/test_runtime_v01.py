import unittest

from kivai_sdk.runtime import execute_intent


class TestRuntimeV01(unittest.TestCase):

    def test_echo_success(self):
        payload = {
            "intent": "echo",
            "message": "hola",
            "auth": {"required": False},
            "confidence": 1.0,
        }
        ack = execute_intent(payload)

        self.assertEqual(ack["status"], "ok")
        self.assertEqual(ack["result"]["echo"], "hola")
        self.assertIn("intent_id", ack)
        self.assertIn("timestamp", ack)

    def test_auth_required_without_token(self):
        payload = {
            "intent": "echo",
            "message": "secure",
            "auth": {"required": True},
            "confidence": 1.0,
        }
        ack = execute_intent(payload)

        self.assertEqual(ack["status"], "failed")
        self.assertEqual(ack["error"]["code"], "AUTH_REQUIRED")

    def test_unsupported_intent(self):
        payload = {
            "intent": "unknown_intent",
            "auth": {"required": False},
            "confidence": 1.0,
        }
        ack = execute_intent(payload)

        self.assertEqual(ack["status"], "failed")
        self.assertEqual(ack["error"]["code"], "INTENT_UNSUPPORTED")
