import unittest

from kivai_sdk.router import route_target
from kivai_sdk.runtime import execute_intent


class TestRoutingV03(unittest.TestCase):
    def test_route_by_device_id(self):
        payload = {
            "intent": "echo",
            "message": "hi",
            "device_id": "speaker-living-02",
            "auth": {"required": False},
            "confidence": 1.0,
        }
        match = route_target(payload)
        self.assertIsNotNone(match)
        self.assertEqual(match.device.device_id, "speaker-living-02")

    def test_route_by_zone_and_capability(self):
        payload = {
            "intent": "echo",
            "message": "hi",
            "target": {"zone": "living_room", "capability": "thermostat"},
            "auth": {"required": False},
            "confidence": 1.0,
        }
        match = route_target(payload)
        self.assertIsNotNone(match)
        self.assertEqual(match.device.device_id, "thermostat-living-01")

    def test_execute_adds_route_to_ack(self):
        payload = {
            "intent": "echo",
            "message": "hola",
            "target": {"zone": "living_room", "capability": "speaker"},
            "auth": {"required": False},
            "confidence": 1.0,
        }
        ack = execute_intent(payload)
        self.assertEqual(ack["status"], "ok")
        self.assertIn("route", ack)
        self.assertEqual(ack["route"]["device_id"], "speaker-living-02")
