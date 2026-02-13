import json
import tempfile
import unittest
from pathlib import Path

from kivai_sdk.cli import main


class TestCLIV010(unittest.TestCase):
    def test_cli_help(self):
        # argparse exits with SystemExit(0) on -h
        with self.assertRaises(SystemExit) as cm:
            main(["-h"])
        self.assertEqual(cm.exception.code, 0)

    def test_cli_list_adapters(self):
        rc = main(["list", "adapters"])
        self.assertEqual(rc, 0)

    def test_cli_execute_echo_from_file(self):
        payload = {
            "intent_id": "test-intent-12345678",
            "intent": "echo",
            "target": {"capability": "speaker", "zone": "living_room"},
            "params": {"message": "hola"},
            "meta": {
                "timestamp": "2026-02-12T00:00:00Z",
                "language": "en",
                "confidence": 1.0,
                "source": "test",
            },
        }

        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "intent.json"
            f.write_text(json.dumps(payload), encoding="utf-8")

            rc = main(["execute", str(f)])
            self.assertEqual(rc, 0)
