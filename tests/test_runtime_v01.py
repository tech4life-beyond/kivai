import unittest
import uuid
from datetime import datetime, timezone

from kivai_sdk.runtime import execute_intent


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


class TestRuntimeV01(unittest.TestCase):
    def test_echo_success(self):
        payload = canonical_payload(
            "echo",
            target={"capability": "speaker", "zone": "living_room"},
            params={"message": "hola"},
        )
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "ok")
        self.assertEqual(ack["result"]["echo"], "hola")
        self.assertIn("intent_id", ack)
        self.assertIn("timestamp", ack)

    def test_auth_required_without_token(self):
        payload = canonical_payload(
            "echo",
            target={"capability": "speaker", "zone": "living_room"},
            params={"message": "secure"},
            auth={"required_role": "owner", "token": ""},
        )
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "failed")
        self.assertEqual(ack["error"]["code"], "AUTH_REQUIRED")

    def test_invalid_schema_rejected(self):
        payload = {
            "intent_id": str(uuid.uuid4()),
            "intent": "set_temperature",
            "target": {},  # invalid by schema anyOf
            "params": {"value": 21},
            "meta": {"timestamp": _utc_now_iso(), "language": "en", "confidence": 1.0},
        }
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "failed")
        self.assertEqual(ack["error"]["code"], "SCHEMA_INVALID")
