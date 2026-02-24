from __future__ import annotations

from typing import Dict, Optional

from kivai_sdk.adapters.base import AdapterContext

# Builtins
from kivai_sdk.adapters.builtin.lock import UnlockDoorAdapter
from kivai_sdk.adapters.builtin.speaker import PlayMusicAdapter
from kivai_sdk.adapters.builtin.thermostat import SetTemperatureAdapter

# Mock adapters
from kivai_sdk.adapters.mock_adapter import (
    EchoAdapter,
    MockDevicePingAdapter,
    MockPowerOnAdapter,
    MockPowerOffAdapter,
    MockFindBeepAdapter,
)


class AdapterRegistry:
    def __init__(self) -> None:
        self._by_intent: Dict[str, object] = {}

    def register(self, adapter: object) -> None:
        intent = getattr(adapter, "intent", None)

        if callable(intent):
            intent = intent()

        if not isinstance(intent, str) or not intent.strip():
            raise ValueError("Adapter must define a non-empty .intent")

        self._by_intent[intent] = adapter

    def resolve(self, intent: Optional[str]) -> Optional[object]:
        if not intent or not isinstance(intent, str):
            return None

        return self._by_intent.get(intent)

    def get(self, intent: str) -> Optional[object]:
        return self.resolve(intent)

    def list_intents(self) -> list[str]:
        return sorted(self._by_intent.keys())


def _build_default_registry() -> AdapterRegistry:
    reg = AdapterRegistry()

    # Builtins
    reg.register(SetTemperatureAdapter())
    reg.register(PlayMusicAdapter())
    reg.register(UnlockDoorAdapter())

    # REQUIRED by tests
    reg.register(EchoAdapter())

    # Mock adapters
    reg.register(MockDevicePingAdapter())
    reg.register(MockPowerOnAdapter())
    reg.register(MockPowerOffAdapter())
    reg.register(MockFindBeepAdapter())

    return reg


def default_registry() -> AdapterRegistry:
    return _build_default_registry()


DEFAULT_REGISTRY = _build_default_registry()


__all__ = [
    "AdapterRegistry",
    "AdapterContext",
    "default_registry",
    "DEFAULT_REGISTRY",
]
