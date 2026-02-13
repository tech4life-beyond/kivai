from __future__ import annotations

from kivai_sdk.adapters.base import AdapterContext
from kivai_sdk.adapters.capabilities import AdapterCapabilities


class UnlockDoorAdapter:
    """
    Reference adapter: unlock_door

    v0.9 strict:
    - adapter declares auth baseline (owner)
    - runtime enforces auth deterministically
    """

    intent = "unlock_door"

    @property
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            intent="unlock_door",
            required_capabilities=frozenset({"lock"}),
            requires_auth=True,
            required_role="owner",
            timeout_ms=5000,
        )

    def execute(self, payload: dict, ctx: AdapterContext) -> dict:
        return {
            "ok": True,
            "action": "unlock_door",
            "gateway_id": ctx.gateway_id,
        }
