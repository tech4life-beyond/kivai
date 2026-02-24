from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from kivai_sdk.adapters.base import KivaiAdapter

# Built-in reference adapters
from kivai_sdk.adapters.builtin.lock import DoorLockAdapter
from kivai_sdk.adapters.builtin.speaker import PlayMusicAdapter
from kivai_sdk.adapters.builtin.thermostat import SetTemperatureAdapter
from kivai_sdk.adapters.builtin.vision import DetectObjectsAdapter

# Demo/mock adapters (software-only)
from kivai_sdk.adapters.mock_adapter import (
    MockDevicePingAdapter,
    MockPowerOnAdapter,
    MockPowerOffAdapter,
    MockFindBeepAdapter,
)


@dataclass
class AdapterRegistration:
    intent: str
    adapter: KivaiAdapter


class AdapterRegistry:
    """
    Registry maps `intent` -> adapter that can execute that intent.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, AdapterRegistration] = {}

    def register(self, adapter: KivaiAdapter) -> None:
        intent = getattr(adapter, "intent", None)
        if not isinstance(intent, str) or not intent.strip():
            raise ValueError("Adapter must define non-empty .intent string")
        self._adapters[intent] = AdapterRegistration(intent=intent, adapter=adapter)

    def resolve(self, intent: str | None) -> Optional[KivaiAdapter]:
        if not intent:
            return None
        reg = self._adapters.get(intent)
        return reg.adapter if reg else None

    def list_intents(self) -> list[str]:
        return sorted(self._adapters.keys())


# Canonical default registry (ships with built-ins + demo mocks)
default_registry = AdapterRegistry()

# Built-ins (examples)
default_registry.register(DoorLockAdapter())
default_registry.register(PlayMusicAdapter())
default_registry.register(SetTemperatureAdapter())
default_registry.register(DetectObjectsAdapter())

# Mocks (demo-ready immediately)
default_registry.register(MockDevicePingAdapter())
default_registry.register(MockPowerOnAdapter())
default_registry.register(MockPowerOffAdapter())
default_registry.register(MockFindBeepAdapter())
