from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from kivai_sdk.adapters.builtin import (
    PlayMusicAdapter,
    SetTemperatureAdapter,
    UnlockDoorAdapter,
)

from .base import AdapterContext, KivaiAdapter
from .capabilities import AdapterCapabilities


@dataclass
class AdapterRegistry:
    """
    Simple in-process registry.

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
    Reference adapter: echo (local, deterministic).
    Kept outside schema by design, but still must declare capabilities in v0.9 strict.
    """

    intent = "echo"

    @property
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            intent="echo",
            required_capabilities=frozenset(),
            requires_auth=False,
            required_role=None,
            timeout_ms=1000,
        )

    def execute(self, payload: dict, ctx: AdapterContext) -> dict:
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
