import unittest
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from kivai_sdk.gateway import app


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_payload(
    intent: str, target: dict, params: dict | None = None, auth: dict | None = None
) -> dict:
    payload = {
        "intent_id": str(uuid.uuid4()),
        "intent": intent,
        "target": target,
        "params": params or {},
        "meta": {
            "timestamp": _utc_now_iso(),
            "language": "en",
            "confidence": 1.0,
            "source": "test",
        },
    }
    if auth is not None:
        payload["auth"] = auth
    return payload


class TestV04GatewayExecute(unittest.TestCase):
    def test_execute_returns_ack_ok(self):
        client = TestClient(app)
        payload = canonical_payload(
            "echo",
            target={"capability": "speaker", "zone": "living_room"},
            params={"message": "hola"},
        )
        r = client.post("/v1/execute", json=payload)
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["result"]["echo"], "hola")

    def test_execute_returns_ack_failed_with_400(self):
        client = TestClient(app)
        payload = canonical_payload(
            "unlock_door",
            target={"device_id": "door-front-01"},
        )
        r = client.post("/v1/execute", json=payload)
        self.assertEqual(r.status_code, 400)
        body = r.json()
        self.assertEqual(body["status"], "failed")
        self.assertEqual(body["error"]["code"], "AUTH_REQUIRED")
