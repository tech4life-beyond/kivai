from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .models import Device, DeviceMatch


@dataclass
class DeviceRegistry:
    """
    In-memory device registry (v0.3).

    Future: persistence, discovery, pairing/binding, trust posture, heartbeat/health.
    """

    _by_id: Dict[str, Device]

    @classmethod
    def empty(cls) -> "DeviceRegistry":
        return cls(_by_id={})

    def upsert(self, device: Device) -> None:
        self._by_id[device.device_id] = device

    def get(self, device_id: str) -> Optional[Device]:
        return self._by_id.get(device_id)

    def all(self) -> List[Device]:
        return list(self._by_id.values())

    def resolve(
        self,
        device_id: str | None = None,
        zone: str | None = None,
        capability: str | None = None,
    ) -> DeviceMatch | None:
        """
        Routing resolution rules (hub default):
          1) If device_id provided -> direct match
          2) Else match by zone + capability
          3) Else match by capability only (if unique)
        """
        if device_id:
            d = self.get(device_id)
            if d:
                return DeviceMatch(device=d, reason="device_id")
            return None

        candidates = self.all()

        if zone:
            candidates = [d for d in candidates if d.zone == zone]
        if capability:
            candidates = [d for d in candidates if d.has_capability(capability)]

        if len(candidates) == 1:
            reason = (
                "zone+capability"
                if zone and capability
                else ("zone" if zone else "capability")
            )
            return DeviceMatch(device=candidates[0], reason=reason)

        return None


def default_device_registry() -> DeviceRegistry:
    """
    v0.3 defaults: a tiny virtual home for demos.

    These are *not* authoritative device definitions—just runnable defaults.
    """
    reg = DeviceRegistry.empty()
    reg.upsert(
        Device(
            device_id="thermostat-living-01",
            zone="living_room",
            capabilities=frozenset({"thermostat"}),
        )
    )
    reg.upsert(
        Device(
            device_id="speaker-living-02",
            zone="living_room",
            capabilities=frozenset({"speaker"}),
        )
    )
    reg.upsert(
        Device(
            device_id="door-front-01",
            zone="front_door",
            capabilities=frozenset({"lock"}),
        )
    )
    return reg
