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


class TestV04CoreIntents(unittest.TestCase):
    def test_set_temperature_routes_and_executes(self):
        payload = canonical_payload(
            "set_temperature",
            target={"capability": "thermostat", "zone": "living_room"},
            params={"value": 21, "unit": "C"},
        )
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "ok")
        self.assertEqual(ack["result"]["action"], "set_temperature")
        self.assertEqual(ack["result"]["value"], 21.0)
        self.assertIn("route", ack)
        self.assertEqual(ack["route"]["device_id"], "thermostat-living-01")

    def test_play_music_routes_and_executes(self):
        payload = canonical_payload(
            "play_music",
            target={"capability": "speaker", "zone": "living_room"},
            params={"query": "lofi"},
        )
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "ok")
        self.assertEqual(ack["result"]["action"], "play_music")
        self.assertEqual(ack["result"]["query"], "lofi")
        self.assertIn("route", ack)
        self.assertEqual(ack["route"]["device_id"], "speaker-living-02")

    def test_unlock_door_requires_auth_by_default(self):
        payload = canonical_payload(
            "unlock_door",
            target={"device_id": "door-front-01"},
            params={},
        )
        # runtime enforces auth baseline for unlock_door
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "failed")
        self.assertEqual(ack["error"]["code"], "AUTH_REQUIRED")
