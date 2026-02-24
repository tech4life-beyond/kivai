from __future__ import annotations

from kivai_sdk.adapters.base import AdapterContext
from kivai_sdk.adapters.capabilities import AdapterCapabilities


class UnlockDoorAdapter:
    @property
    def intent(self) -> str:
        return "unlock_door"

    @property
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            intent="unlock_door",
            required_capabilities=frozenset({"lock_control"}),
            requires_auth=True,
            required_role="owner",
        )

    def execute(self, payload: dict, ctx: AdapterContext) -> dict:

        target = payload.get("target") or {}
        device_id = target.get("device_id") or "unknown-device"

        return {
            "ok": True,
            "adapter": "builtin",
            "intent": "unlock_door",
            "device_id": device_id,
            "state": "unlocked",
            "gateway_id": ctx.gateway_id,
        }


DoorLockAdapter = UnlockDoorAdapter
