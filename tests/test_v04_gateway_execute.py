import unittest

from fastapi.testclient import TestClient

from kivai_sdk.gateway import app


class TestV04GatewayExecute(unittest.TestCase):
    def test_execute_returns_ack_ok(self):
        client = TestClient(app)
        payload = {
            "intent": "echo",
            "message": "hola",
            "auth": {"required": False},
            "confidence": 1.0,
        }
        r = client.post("/v1/execute", json=payload)
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["result"]["echo"], "hola")

    def test_execute_returns_ack_failed_with_400(self):
        client = TestClient(app)
        payload = {
            "intent": "unlock_door",
            "device_id": "door-front-01",
            "confidence": 1.0,
        }
        r = client.post("/v1/execute", json=payload)
        self.assertEqual(r.status_code, 400)
        body = r.json()
        self.assertEqual(body["status"], "failed")
        self.assertEqual(body["error"]["code"], "AUTH_REQUIRED")
