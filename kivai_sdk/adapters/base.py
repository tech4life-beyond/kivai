from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol


AdapterResult = Dict[str, Any]


@dataclass(frozen=True)
class AdapterContext:
    """
    Execution context (v0.2).
    Keep minimal and explicit (auditable).
    """

    gateway_id: str = "local-gateway"
    user_id: str | None = None
    request_id: str | None = None


class KivaiAdapter(Protocol):
    """
    Adapter contract: intent payload -> execution result.

    - Deterministic behavior
    - No hidden state
    - No network by default (networked adapters are explicit)
    """

    intent: str

    def execute(self, payload: dict, ctx: AdapterContext) -> AdapterResult: ...
