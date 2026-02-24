from __future__ import annotations

from typing import Dict

from kivai_sdk.adapters.base import AdapterContext
from kivai_sdk.adapters.builtin.lock import UnlockDoorAdapter
from kivai_sdk.adapters.builtin.speaker import PlayMusicAdapter
from kivai_sdk.adapters.builtin.thermostat import SetTemperatureAdapter

# Mock adapters (demo-ready)
from kivai_sdk.adapters.mock_adapter import (
    MockDevicePingAdapter,
    MockFindBeepAdapter,
    MockPowerOffAdapter,
    MockPowerOnAdapter,
)


class AdapterRegistry:
    """
    In-memory adapter registry.
    """

    def __init__(self) -> None:
        self._adapters: Dict[str, object] = {}

    def register(self, adapter: object) -> None:
        intent = getattr(adapter, "intent", None)
        if callable(intent):
            intent = intent()
        if not isinstance(intent, str) or not intent.strip():
            raise ValueError("Adapter must define a non-empty .intent")
        self._adapters[intent] = adapter

    def get(self, intent: str) -> object | None:
        return self._adapters.get(intent)

    def list_intents(self) -> list[str]:
        return sorted(self._adapters.keys())


# Default registry used by the runtime (demo + builtin)
default_registry = AdapterRegistry()
default_registry.register(SetTemperatureAdapter())
default_registry.register(PlayMusicAdapter())
default_registry.register(UnlockDoorAdapter())

# Demo/mock intents so /v1/execute is exciting immediately
default_registry.register(MockDevicePingAdapter())
default_registry.register(MockPowerOnAdapter())
default_registry.register(MockPowerOffAdapter())
default_registry.register(MockFindBeepAdapter())


__all__ = ["AdapterRegistry", "AdapterContext", "default_registry"]
