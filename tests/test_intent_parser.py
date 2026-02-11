import unittest
from unittest.mock import patch
from kivai_sdk.intent_parser import parse_input


class TestIntentParser(unittest.TestCase):
    @patch("kivai_sdk.intent_parser.requests.post")
    def test_parse_turn_off_lights(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}

        input_text = "Turn off the lights"
        payload, status = parse_input(input_text)

        self.assertEqual(payload["intent"], "turn_off")
        self.assertEqual(payload["target"]["capability"], "light_control")

    @patch("kivai_sdk.intent_parser.requests.post")
    def test_unknown_command(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}

        input_text = "Do something weird"
        payload, status = parse_input(input_text)

        self.assertEqual(payload["intent"], "unknown")
