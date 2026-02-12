import unittest
import uuid
from datetime import datetime, timezone

from kivai_sdk.validator import validate_command


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
            "confidence": 0.99,
            "source": "test",
        },
    }
    if auth is not None:
        payload["auth"] = auth
    return payload


class TestSchemaComplianceV05(unittest.TestCase):
    def test_valid_target_device_id_passes(self):
        payload = canonical_payload(
            "unlock_door",
            target={"device_id": "door-front-01"},
            params={},
            auth={"required_role": "owner", "token": "test-token"},
        )
        ok, message = validate_command(payload)
        self.assertTrue(ok, message)

    def test_valid_target_zone_capability_passes(self):
        payload = canonical_payload(
            "set_temperature",
            target={"capability": "thermostat", "zone": "living_room"},
            params={"value": 21, "unit": "C"},
        )
        ok, message = validate_command(payload)
        self.assertTrue(ok, message)

    def test_missing_meta_fails(self):
        payload = canonical_payload(
            "play_music",
            target={"capability": "speaker", "zone": "living_room"},
            params={"query": "lofi"},
        )
        payload.pop("meta")
        ok, message = validate_command(payload)
        self.assertFalse(ok)
        self.assertIsInstance(message, str)

    def test_missing_intent_id_fails(self):
        payload = canonical_payload(
            "play_music",
            target={"capability": "speaker", "zone": "living_room"},
            params={"query": "lofi"},
        )
        payload.pop("intent_id")
        ok, message = validate_command(payload)
        self.assertFalse(ok)
        self.assertIsInstance(message, str)

    def test_target_missing_required_fields_fails(self):
        payload = canonical_payload(
            "set_temperature",
            target={},  # violates anyOf (needs device_id OR capability+zone)
            params={"value": 21},
        )
        ok, message = validate_command(payload)
        self.assertFalse(ok)
        self.assertIsInstance(message, str)

    def test_auth_missing_token_or_role_fails(self):
        payload = canonical_payload(
            "unlock_door",
            target={"device_id": "door-front-01"},
            params={},
            auth={"required_role": "owner", "token": ""},  # token minLength 1
        )
        ok, message = validate_command(payload)
        self.assertFalse(ok)
        self.assertIsInstance(message, str)
