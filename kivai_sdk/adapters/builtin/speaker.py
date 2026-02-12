from __future__ import annotations

from kivai_sdk.adapters.base import AdapterContext, AdapterResult


class PlayMusicAdapter:
    """
    Reference adapter: play_music

    Expected payload fields (v0.4 minimal):
      - intent: "play_music"
      - query: string (optional; default "default_playlist")
    """

    intent = "play_music"

    def execute(self, payload: dict, ctx: AdapterContext) -> AdapterResult:
        query = payload.get("query") or "default_playlist"
        if not isinstance(query, str):
            return {
                "ok": False,
                "error": {"code": "BAD_REQUEST", "message": "query must be a string"},
            }

        return {
            "ok": True,
            "action": "play_music",
            "query": query,
            "gateway_id": ctx.gateway_id,
        }
