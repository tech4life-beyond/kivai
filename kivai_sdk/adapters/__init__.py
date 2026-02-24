from .base import AdapterContext, KivaiAdapter
from .registry import AdapterRegistry, default_registry, DEFAULT_REGISTRY
from .contracts import AdapterError, AdapterResult, normalize_adapter_output
from .capabilities import AdapterCapabilities

# Mock adapters (demo-ready)
from .mock_adapter import (
    MockDevicePingAdapter,
    MockPowerOnAdapter,
    MockPowerOffAdapter,
    MockFindBeepAdapter,
)

__all__ = [
    "AdapterContext",
    "KivaiAdapter",
    "AdapterRegistry",
    "default_registry",
    "DEFAULT_REGISTRY",
    "AdapterError",
    "AdapterResult",
    "normalize_adapter_output",
    "AdapterCapabilities",
    # Mock adapters
    "MockDevicePingAdapter",
    "MockPowerOnAdapter",
    "MockPowerOffAdapter",
    "MockFindBeepAdapter",
]
