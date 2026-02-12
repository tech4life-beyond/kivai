from __future__ import annotations

from kivai_sdk.devices import DeviceMatch, default_device_registry


def route_target(payload: dict) -> DeviceMatch | None:
    """
    v0.3 routing:
      - direct: payload.device_id
      - indirect: payload.target.zone + payload.target.capability
      - indirect: payload.target.capability (unique)
    """
    device_id = payload.get("device_id")

    target = payload.get("target")
    zone = None
    capability = None
    if isinstance(target, dict):
        zone = target.get("zone")
        capability = target.get("capability")

    reg = default_device_registry()
    return reg.resolve(device_id=device_id, zone=zone, capability=capability)
