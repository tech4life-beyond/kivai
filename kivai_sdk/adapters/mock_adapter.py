from __future__ import annotations

from kivai_sdk.adapters.base import AdapterContext
from kivai_sdk.adapters.capabilities import AdapterCapabilities


class MockDevicePingAdapter:
    @property
    def intent(self) -> str:
        return "device.ping"

    @property
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            intent=self.intent,
            required_capabilities=[],
            requires_auth=False,
            required_role=None,
        )

    def execute(self, payload: dict, ctx: AdapterContext) -> dict:
        target = payload.get("target") or {}
        device_id = target.get("device_id") or "unknown-device"
        return {
            "ok": True,
            "adapter": "mock",
            "intent": self.intent,
            "device_id": device_id,
            "pong": True,
        }


class MockPowerOnAdapter:
    @property
    def intent(self) -> str:
        return "power.on"

    @property
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            intent=self.intent,
            required_capabilities=[],
            requires_auth=False,
            required_role=None,
        )

    def execute(self, payload: dict, ctx: AdapterContext) -> dict:
        target = payload.get("target") or {}
        device_id = target.get("device_id") or "unknown-device"
        return {
            "ok": True,
            "adapter": "mock",
            "intent": self.intent,
            "device_id": device_id,
            "state": "on",
        }


class MockPowerOffAdapter:
    @property
    def intent(self) -> str:
        return "power.off"

    @property
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            intent=self.intent,
            required_capabilities=[],
            requires_auth=False,
            required_role=None,
        )

    def execute(self, payload: dict, ctx: AdapterContext) -> dict:
        target = payload.get("target") or {}
        device_id = target.get("device_id") or "unknown-device"
        return {
            "ok": True,
            "adapter": "mock",
            "intent": self.intent,
            "device_id": device_id,
            "state": "off",
        }


class MockFindBeepAdapter:
    @property
    def intent(self) -> str:
        return "find.beep"

    @property
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            intent=self.intent,
            required_capabilities=[],
            requires_auth=False,
            required_role=None,
        )

    def execute(self, payload: dict, ctx: AdapterContext) -> dict:
        target = payload.get("target") or {}
        params = payload.get("params") or {}
        device_id = target.get("device_id") or "unknown-device"
        duration_ms = params.get("duration_ms", 1500)
        return {
            "ok": True,
            "adapter": "mock",
            "intent": self.intent,
            "device_id": device_id,
            "action": "beep",
            "duration_ms": duration_ms,
        }
