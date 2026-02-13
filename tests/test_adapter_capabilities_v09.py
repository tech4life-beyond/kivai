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


class TestAdapterCapabilitiesV09(unittest.TestCase):
    def test_unlock_door_requires_owner_auth_by_adapter_caps(self):
        payload = canonical_payload(
            "unlock_door",
            target={"device_id": "door-front-01"},
            params={},
        )
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "failed")
        self.assertEqual(ack["error"]["code"], "AUTH_REQUIRED")

    def test_unlock_door_succeeds_with_owner_auth(self):
        payload = canonical_payload(
            "unlock_door",
            target={"device_id": "door-front-01"},
            params={},
            auth={"required_role": "owner", "token": "test-token"},
        )
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "ok")
        self.assertEqual(ack["result"]["action"], "unlock_door")

    def test_set_temperature_fails_on_capability_mismatch_when_routed(self):
        # Route will resolve thermostat-living-01 with capabilities ["thermostat"]
        # We intentionally ask for a speaker capability in target to route to speaker device,
        # but intent is set_temperature which requires "thermostat" by adapter caps.
        payload = canonical_payload(
            "set_temperature",
            target={"capability": "speaker", "zone": "living_room"},
            params={"value": 21, "unit": "C"},
        )
        ack = execute_intent(payload)
        # routing exists, but capabilities mismatch, must fail deterministically
        self.assertEqual(ack["status"], "failed")
        self.assertEqual(ack["error"]["code"], "ADAPTER_CAPABILITY_MISMATCH")

    def test_play_music_ok_when_capability_matches(self):
        payload = canonical_payload(
            "play_music",
            target={"capability": "speaker", "zone": "living_room"},
            params={"query": "lofi"},
        )
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "ok")
        self.assertEqual(ack["result"]["action"], "play_music")
        self.assertIn("route", ack)
        self.assertEqual(ack["route"]["device_id"], "speaker-living-02")

    def test_echo_still_runs_outside_schema(self):
        payload = canonical_payload(
            "echo",
            target={"capability": "speaker", "zone": "living_room"},
            params={"message": "hola"},
        )
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "ok")
        self.assertEqual(ack["result"]["echo"], "hola")
        self.assertIn("execution_id", ack)
