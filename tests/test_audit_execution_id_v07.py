import unittest
import uuid
from datetime import datetime, timezone

from kivai_sdk.runtime import execute_intent


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class TestAuditExecutionIdV07(unittest.TestCase):
    def test_ack_contains_execution_id(self):
        payload = {
            "intent_id": str(uuid.uuid4()),
            "intent": "echo",
            "target": {"capability": "speaker", "zone": "living_room"},
            "params": {"message": "hola"},
            "meta": {"timestamp": _utc_now_iso(), "language": "en", "confidence": 1.0},
        }
        ack = execute_intent(payload)
        self.assertIn("execution_id", ack)
        self.assertIsInstance(ack["execution_id"], str)
        self.assertGreaterEqual(len(ack["execution_id"]), 8)
