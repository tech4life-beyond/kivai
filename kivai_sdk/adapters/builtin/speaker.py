from __future__ import annotations

from kivai_sdk.adapters.base import AdapterContext
from kivai_sdk.adapters.capabilities import AdapterCapabilities


class PlayMusicAdapter:
    """
    Reference adapter: play_music

    Expected payload fields:
      - intent: "play_music"
      - params.query: string (optional; default "default_playlist")
    """

    intent = "play_music"

    @property
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            intent="play_music",
            required_capabilities=frozenset({"speaker"}),
            requires_auth=False,
            required_role=None,
            timeout_ms=5000,
        )

    def execute(self, payload: dict, ctx: AdapterContext) -> dict:
        params = (
            payload.get("params") if isinstance(payload.get("params"), dict) else {}
        )
        query = params.get("query") or "default_playlist"

        if not isinstance(query, str):
            return {
                "ok": False,
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "params.query must be a string",
                },
            }

        return {
            "ok": True,
            "action": "play_music",
            "query": query,
            "gateway_id": ctx.gateway_id,
        }
