from __future__ import annotations

from kivai_sdk.devices import DeviceMatch, default_device_registry

_INTENT_DEFAULT_CAPABILITY = {
    "set_temperature": "thermostat",
    "play_music": "speaker",
    "unlock_door": "lock",
    "echo": None,
}


def route_target(payload: dict) -> DeviceMatch | None:
    """
    v0.5 routing aligned to schema:

    target:
      - device_id
      - capability + zone
    """
    target = payload.get("target") if isinstance(payload.get("target"), dict) else {}
    device_id = target.get("device_id")
    zone = target.get("zone")
    capability = target.get("capability")

    if capability is None:
        capability = _INTENT_DEFAULT_CAPABILITY.get(payload.get("intent"))

    reg = default_device_registry()
    return reg.resolve(device_id=device_id, zone=zone, capability=capability)
