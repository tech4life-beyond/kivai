from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .capabilities import AdapterCapabilities


@dataclass
class AdapterContext:
    """
    Execution context passed to adapters.
    Extend over time (gateway_id, correlation IDs, device session, etc.)
    """

    gateway_id: str = "local"


@runtime_checkable
class KivaiAdapter(Protocol):
    """
    Adapter interface contract.
    Concrete adapters implement this protocol.
    """

    @property
    def intent(self) -> str: ...

    @property
    def capabilities(self) -> AdapterCapabilities: ...

    def execute(self, payload: dict, ctx: AdapterContext) -> dict: ...
