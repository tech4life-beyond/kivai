import unittest
from unittest.mock import patch
from kivai_sdk.intent_parser import parse_input


class TestIntentPipeline(unittest.TestCase):
    @patch("kivai_sdk.intent_parser.requests.post")
    def test_turn_on_light(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}

        raw_input = "Please turn on the kitchen light"
        payload, status = parse_input(raw_input)

        self.assertEqual(payload["intent"], "turn_on")
        self.assertEqual(payload["target"]["capability"], "light_control")
        self.assertEqual(payload["target"]["zone"], "kitchen")
