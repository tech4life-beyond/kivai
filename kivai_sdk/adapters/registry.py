from __future__ import annotations

from typing import Dict, Optional

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

    Provides:
    - register(adapter)
    - resolve(intent)
    - list_intents()

    Compatible with runtime, CLI, and tests.
    """

    def __init__(self) -> None:
        # CLI expects this exact name
        self._by_intent: Dict[str, object] = {}

    def register(self, adapter: object) -> None:
        intent = getattr(adapter, "intent", None)

        if callable(intent):
            intent = intent()

        if not isinstance(intent, str) or not intent.strip():
            raise ValueError("Adapter must define a non-empty .intent")

        self._by_intent[intent] = adapter

    def resolve(self, intent: Optional[str]) -> Optional[object]:
        """
        Resolve adapter by intent.

        Required by runtime and tests.
        """
        if not intent or not isinstance(intent, str):
            return None

        return self._by_intent.get(intent)

    # Backwards compatibility
    def get(self, intent: str) -> Optional[object]:
        return self.resolve(intent)

    def list_intents(self) -> list[str]:
        return sorted(self._by_intent.keys())


def _build_default_registry() -> AdapterRegistry:
    reg = AdapterRegistry()

    # Built-in adapters
    reg.register(SetTemperatureAdapter())
    reg.register(PlayMusicAdapter())
    reg.register(UnlockDoorAdapter())

    # Mock adapters
    reg.register(MockDevicePingAdapter())
    reg.register(MockPowerOnAdapter())
    reg.register(MockPowerOffAdapter())
    reg.register(MockFindBeepAdapter())

    return reg


def default_registry() -> AdapterRegistry:
    """
    Factory function used by runtime/tests.
    Must return fresh instance.
    """
    return _build_default_registry()


# Singleton instance for CLI / non-test paths
DEFAULT_REGISTRY = _build_default_registry()


__all__ = [
    "AdapterRegistry",
    "AdapterContext",
    "default_registry",
    "DEFAULT_REGISTRY",
]
