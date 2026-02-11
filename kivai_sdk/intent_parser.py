# kivai_sdk/intent_parser.py
import re
import uuid
from datetime import datetime, timezone
import requests  # used to call the mock device


def send_to_device(intent_payload: dict):
    # mock device server endpoint
    url = "http://127.0.0.1:5000/intent"
    response = requests.post(url, json=intent_payload)
    return response.json()


def _extract_zone(raw_input: str) -> str | None:
    text = raw_input.lower()

    # Pattern 1: "in the kitchen" / "in the living room"
    match = re.search(r"\bin the\s+([a-z]+(?:\s[a-z]+)?)\b", text)
    if match:
        return match.group(1).strip()

    # Pattern 2 (strict): capture the 1–2 words immediately before the device noun
    # e.g. "the kitchen light" -> "kitchen"
    #      "living room lights" -> "living room"
    match = re.search(
        r"\b(?:the\s+)?([a-z]+(?:\s[a-z]+)?)\s+(?:light|lights|thermostat)\b", text
    )
    if match:
        return match.group(1).strip()

    return None


def _infer_intent(raw_input: str) -> str:
    text = raw_input.lower()

    if "turn on" in text:
        return "turn_on"
    if "turn off" in text:
        return "turn_off"
    if "set temperature" in text or "set the temperature" in text:
        return "set_temperature"
    if "find" in text or "locate" in text:
        return "locate"

    return "unknown"


def _infer_capability(raw_input: str) -> str:
    text = raw_input.lower()

    if "light" in text or "lights" in text:
        return "light_control"
    if "thermostat" in text or "temperature" in text:
        return "thermostat_control"

    return "generic"


def parse_input(
    raw_input: str, user_id="abc123", language="en", trigger="Kivai"
) -> tuple[dict, dict]:
    """
    Parse raw text into a Kivai Intent v1 payload.

    This is a minimal reference parser (not NLP).
    In production, AI/Gateway generates this payload.
    """
    zone = _extract_zone(raw_input)
    intent = _infer_intent(raw_input)
    capability = _infer_capability(raw_input)

    confidence = 0.9 if intent != "unknown" and capability != "generic" else 0.5

    payload = {
        "intent_id": str(uuid.uuid4()),
        "intent": intent,
        "target": {
            # For v1 parser demo, we use capability+zone targeting.
            # In production, device_id targeting is preferred when available.
            "capability": capability,
            "zone": zone or "unknown",
        },
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "language": language,
            "confidence": confidence,
            "source": "gateway",
            "trigger": trigger,
            "user_id": user_id,
        },
    }

    response = send_to_device(payload)
    return payload, response
