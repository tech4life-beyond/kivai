import unittest
import uuid
from datetime import datetime, timezone

from kivai_sdk.router import route_target
from kivai_sdk.runtime import execute_intent


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_payload(intent: str, target: dict, params: dict | None = None) -> dict:
    return {
        "intent_id": str(uuid.uuid4()),
        "intent": intent,
        "target": target,
        "params": params or {},
        "meta": {"timestamp": _utc_now_iso(), "language": "en", "confidence": 1.0},
    }


class TestRoutingV03(unittest.TestCase):
    def test_route_by_device_id(self):
        payload = canonical_payload(
            "echo", target={"device_id": "speaker-living-02"}, params={"message": "hi"}
        )
        match = route_target(payload)
        self.assertIsNotNone(match)
        self.assertEqual(match.device.device_id, "speaker-living-02")

    def test_route_by_zone_and_capability(self):
        payload = canonical_payload(
            "echo",
            target={"zone": "living_room", "capability": "thermostat"},
            params={"message": "hi"},
        )
        match = route_target(payload)
        self.assertIsNotNone(match)
        self.assertEqual(match.device.device_id, "thermostat-living-01")

    def test_execute_adds_route_to_ack(self):
        payload = canonical_payload(
            "echo",
            target={"zone": "living_room", "capability": "speaker"},
            params={"message": "hola"},
        )
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "ok")
        self.assertIn("route", ack)
        self.assertEqual(ack["route"]["device_id"], "speaker-living-02")
