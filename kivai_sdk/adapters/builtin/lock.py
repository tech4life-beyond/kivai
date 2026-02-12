from __future__ import annotations

from kivai_sdk.adapters.base import AdapterContext, AdapterResult


class UnlockDoorAdapter:
    """
    Reference adapter: unlock_door

    v0.4: returns a deterministic result. Security is enforced by runtime auth stub.
    """

    intent = "unlock_door"

    def execute(self, payload: dict, ctx: AdapterContext) -> AdapterResult:
        return {
            "ok": True,
            "action": "unlock_door",
            "gateway_id": ctx.gateway_id,
        }
