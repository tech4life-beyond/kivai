from __future__ import annotations

from typing import Dict

from kivai_sdk.adapters.base import AdapterContext

# Builtins
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


def _build_default_registry() -> AdapterRegistry:
    """
    Build a fresh registry instance (tests expect default_registry() callable).
    """
    reg = AdapterRegistry()

    # Built-in reference adapters
    reg.register(SetTemperatureAdapter())
    reg.register(PlayMusicAdapter())
    reg.register(UnlockDoorAdapter())

    # Demo/mock intents so /v1/execute is exciting immediately
    reg.register(MockDevicePingAdapter())
    reg.register(MockPowerOnAdapter())
    reg.register(MockPowerOffAdapter())
    reg.register(MockFindBeepAdapter())

    return reg


def default_registry() -> AdapterRegistry:
    """
    Backwards-compatible factory (callable) used across tests/runtime.
    Returns a registry pre-loaded with builtin + mock adapters.
    """
    return _build_default_registry()


# Optional: a single prebuilt instance for non-test code paths.
DEFAULT_REGISTRY = _build_default_registry()

__all__ = ["AdapterRegistry", "AdapterContext", "default_registry", "DEFAULT_REGISTRY"]
