from __future__ import annotations

from kivai_sdk.devices import DeviceMatch, default_device_registry


_INTENT_DEFAULT_CAPABILITY = {
    "set_temperature": "thermostat",
    "play_music": "speaker",
    "unlock_door": "lock",
    "echo": None,  # echo can route if user provides device_id or target, but no default capability
}


def route_target(payload: dict) -> DeviceMatch | None:
    """
    v0.4 routing (hub):
      Priority:
        1) payload.device_id (direct)
        2) payload.target.zone + payload.target.capability
        3) payload.target.capability
        4) intent default capability (if unique)
    """
    device_id = payload.get("device_id")

    target = payload.get("target")
    zone = None
    capability = None
    if isinstance(target, dict):
        zone = target.get("zone")
        capability = target.get("capability")

    if capability is None:
        capability = _INTENT_DEFAULT_CAPABILITY.get(payload.get("intent"))

    reg = default_device_registry()
    return reg.resolve(device_id=device_id, zone=zone, capability=capability)
