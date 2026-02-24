from __future__ import annotations

from kivai_sdk.adapters.base import AdapterContext
from kivai_sdk.adapters.capabilities import AdapterCapabilities


class UnlockDoorAdapter:
    """
    Built-in reference adapter (demo-grade).
    Intent: unlock_door

    NOTE:
    - This is NOT a real lock integration.
    - It only returns a deterministic result for demos/tests.
    """

    @property
    def intent(self) -> str:
        return "unlock_door"

    @property
    def capabilities(self) -> AdapterCapabilities:
        # Locks are sensitive; require auth baseline.
        return AdapterCapabilities(
            intent=self.intent,
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
            "intent": self.intent,
            "device_id": device_id,
            "state": "unlocked",
        }


# Backwards-compatible alias:
# Some older docs/branches may refer to DoorLockAdapter.
DoorLockAdapter = UnlockDoorAdapter
