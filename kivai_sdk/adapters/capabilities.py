from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Optional


@dataclass(frozen=True)
class AdapterCapabilities:
    """
    Strict adapter declaration contract (v0.9).

    This is how Kivai becomes universal:
    - Runtime can enforce security and compatibility deterministically
    - Routing can reason about capability/zone without hardcoding per-intent logic
    """

    # Canonical intent this adapter executes (e.g., "set_temperature")
    intent: str

    # Capability set required for target device execution (e.g., {"thermostat"})
    required_capabilities: FrozenSet[str]

    # Security baseline: if True, runtime requires auth for this adapter/intent
    requires_auth: bool = False

    # If requires_auth, role required (e.g., "owner")
    required_role: Optional[str] = None

    # Placeholder for operational control; enforced later in runtime/gateway
    timeout_ms: int = 5000

    def __post_init__(self) -> None:
        if not isinstance(self.intent, str) or not self.intent.strip():
            raise ValueError("AdapterCapabilities.intent must be a non-empty string")

        if not isinstance(self.required_capabilities, frozenset):
            raise ValueError(
                "AdapterCapabilities.required_capabilities must be a frozenset"
            )

        for c in self.required_capabilities:
            if not isinstance(c, str) or not c.strip():
                raise ValueError(
                    "AdapterCapabilities.required_capabilities must contain non-empty strings"
                )

        if self.requires_auth:
            if not (isinstance(self.required_role, str) and self.required_role.strip()):
                raise ValueError(
                    "AdapterCapabilities.required_role is required when requires_auth=True"
                )
