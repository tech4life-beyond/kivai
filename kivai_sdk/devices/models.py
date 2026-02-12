from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet


@dataclass(frozen=True)
class Device:
    """
    Minimal device representation (v0.3).

    - device_id: stable identifier
    - zone: physical/logical location (e.g., living_room, kitchen)
    - capabilities: set of capability strings (e.g., thermostat, speaker, lock)
    """

    device_id: str
    zone: str
    capabilities: FrozenSet[str] = field(default_factory=frozenset)

    def has_capability(self, cap: str) -> bool:
        return cap in self.capabilities


@dataclass(frozen=True)
class DeviceMatch:
    """
    Routing result. `reason` is auditable for debugging and logs.
    """

    device: Device
    reason: str
