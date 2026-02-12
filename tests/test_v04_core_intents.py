import unittest

from kivai_sdk.runtime import execute_intent


class TestV04CoreIntents(unittest.TestCase):
    def test_set_temperature_routes_and_executes(self):
        payload = {
            "intent": "set_temperature",
            "value": 21,
            "unit": "C",
            "target": {"zone": "living_room"},
            "auth": {"required": False},
            "confidence": 1.0,
        }
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "ok")
        self.assertEqual(ack["result"]["action"], "set_temperature")
        self.assertEqual(ack["result"]["value"], 21.0)
        self.assertIn("route", ack)
        self.assertEqual(ack["route"]["device_id"], "thermostat-living-01")

    def test_play_music_routes_and_executes(self):
        payload = {
            "intent": "play_music",
            "query": "lofi",
            "auth": {"required": False},
            "confidence": 1.0,
        }
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "ok")
        self.assertEqual(ack["result"]["action"], "play_music")
        self.assertEqual(ack["result"]["query"], "lofi")
        self.assertIn("route", ack)
        self.assertEqual(ack["route"]["device_id"], "speaker-living-02")

    def test_unlock_door_requires_auth_by_default(self):
        payload = {
            "intent": "unlock_door",
            "device_id": "door-front-01",
            "confidence": 1.0,
        }
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "failed")
        self.assertEqual(ack["error"]["code"], "AUTH_REQUIRED")
