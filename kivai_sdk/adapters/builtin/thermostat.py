from __future__ import annotations

from kivai_sdk.adapters.base import AdapterContext, AdapterResult


class SetTemperatureAdapter:
    """
    Reference adapter: set_temperature

    Expected payload fields (v0.4 minimal):
      - intent: "set_temperature"
      - value: number
      - unit: "C" or "F" (optional; default "C")
      - location OR routing target (handled by router)
    """

    intent = "set_temperature"

    def execute(self, payload: dict, ctx: AdapterContext) -> AdapterResult:
        value = payload.get("value")
        unit = payload.get("unit") or "C"

        if not isinstance(value, (int, float)):
            return {
                "ok": False,
                "error": {"code": "BAD_REQUEST", "message": "value must be a number"},
            }

        return {
            "ok": True,
            "action": "set_temperature",
            "value": float(value),
            "unit": unit,
            "gateway_id": ctx.gateway_id,
        }
