from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from .base import AdapterContext, AdapterResult, KivaiAdapter
from kivai_sdk.adapters.builtin import (
    PlayMusicAdapter,
    SetTemperatureAdapter,
    UnlockDoorAdapter,
)


@dataclass
class AdapterRegistry:
    """
    Simple in-process registry (v0.2).
    Future: dynamic discovery, versioning, capability matching, remote adapters.
    """

    _by_intent: Dict[str, KivaiAdapter]

    @classmethod
    def empty(cls) -> "AdapterRegistry":
        return cls(_by_intent={})

    def register(self, adapter: KivaiAdapter) -> None:
        self._by_intent[adapter.intent] = adapter

    def register_many(self, adapters: Iterable[KivaiAdapter]) -> None:
        for a in adapters:
            self.register(a)

    def resolve(self, intent: str | None) -> KivaiAdapter | None:
        if not intent:
            return None
        return self._by_intent.get(intent)


class EchoAdapter:
    """
    v0.2 reference adapter (local, deterministic).
    """

    intent = "echo"

    def execute(self, payload: dict, ctx: AdapterContext) -> AdapterResult:
        params = (
            payload.get("params") if isinstance(payload.get("params"), dict) else {}
        )
        msg = params.get("message", "")
        return {"echo": msg, "gateway_id": ctx.gateway_id}


def default_registry() -> AdapterRegistry:
    reg = AdapterRegistry.empty()
    reg.register(EchoAdapter())
    reg.register(SetTemperatureAdapter())
    reg.register(PlayMusicAdapter())
    reg.register(UnlockDoorAdapter())

    return reg
