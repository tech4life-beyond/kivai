import unittest
import os
import sys

# Add repo root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivai_sdk.validator import validate_command

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "schema",
    "kivai-intent-v1.schema.json"
)


class TestValidator(unittest.TestCase):

    def test_valid_intent_v1(self):
        payload = {
            "intent_id": "c9c4c8d1-2d6f-4d6c-9a2f-1f2c3a4b5c6d",
            "intent": "turn_on",
            "target": {"capability": "light_control", "zone": "kitchen"},
            "meta": {
                "timestamp": "2026-02-06T21:10:00Z",
                "language": "en",
                "confidence": 0.98,
                "source": "gateway",
                "trigger": "Kivai"
            }
        }

        valid, message = validate_command(payload, schema_path=SCHEMA_PATH)
        self.assertTrue(valid)
        self.assertIn("valid", message.lower())

    def test_invalid_intent_v1_missing_required(self):
        payload = {
            "intent": "turn_on"
            # missing intent_id, target, meta
        }

        valid, message = validate_command(payload, schema_path=SCHEMA_PATH)
        self.assertFalse(valid)
        self.assertIn("required", message.lower())


if __name__ == "__main__":
    unittest.main()



