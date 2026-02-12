import json
import uuid
from datetime import datetime, timezone
from typing import Any

from kivai_sdk.adapters import AdapterContext, default_registry
from kivai_sdk.router import route_target
from kivai_sdk.validator import validate_command


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_ack_base(payload: dict) -> dict:
    """
    Minimal ACK envelope (v0.1). Designed to be stable and auditable.
    """
    return {
        "intent_id": str(uuid.uuid4()),
        "timestamp": _utc_now_iso(),
        "status": "ok",
        "intent": payload.get("intent"),
        "device_id": payload.get("device_id"),
    }


def _auth_required(payload: dict) -> bool:
    auth = payload.get("auth")
    return bool(isinstance(auth, dict) and auth.get("required") is True)


def _has_auth_proof(payload: dict) -> bool:
    """
    v0.1 auth proof is intentionally simple:
    - if payload.auth.token exists and is non-empty, treat as present
    Future: JWT, mTLS, local device pairing, role-based policy engine, etc.
    """
    auth = payload.get("auth")
    if not isinstance(auth, dict):
        return False
    token = auth.get("token")
    return bool(isinstance(token, str) and token.strip())


def _error_ack(base: dict, code: str, message: str) -> dict:
    base["status"] = "failed"
    base["error"] = {"code": code, "message": message}
    return base


def _success_ack(base: dict, result: dict) -> dict:
    base["status"] = "ok"
    base["result"] = result
    return base


def _apply_route_if_available(ack: dict, payload: dict) -> None:
    match = route_target(payload)
    if match is None:
        return
    ack["route"] = {
        "device_id": match.device.device_id,
        "zone": match.device.zone,
        "capabilities": sorted(list(match.device.capabilities)),
        "reason": match.reason,
    }


def execute_intent(payload: dict) -> dict:
    """
    v0.3 execution pipeline:
      1) ACK envelope
      2) Demo intents allowed (echo) without canonical schema validation
      3) Canonical schema validation for non-demo intents
      4) Auth stub (when required)
      5) Hub routing annotation (device_id / target.zone / target.capability)
      6) Adapter execution
    """
    ack = _make_ack_base(payload)
    intent = payload.get("intent")

    # v0.4 security baseline: unlock_door requires auth by default
    if intent == "unlock_door":
        auth = payload.get("auth")
        if not isinstance(auth, dict):
            payload["auth"] = {"required": True}
        else:
            auth.setdefault("required", True)

    # v0.4 builtin intents are allowed outside the canonical schema so the platform
    # remains runnable while schema v1 is stabilized/reviewed.
    builtin_intents = {"echo", "set_temperature", "play_music", "unlock_door"}

    if intent in builtin_intents:
        if _auth_required(payload) and not _has_auth_proof(payload):
            return _error_ack(ack, "AUTH_REQUIRED", "Owner authentication required")

        _apply_route_if_available(ack, payload)

        registry = default_registry()
        adapter = registry.resolve(intent)
        if adapter is None:
            return _error_ack(
                ack,
                "INTENT_UNSUPPORTED",
                f"Adapter not registered for intent: {intent}",
            )

        ctx = AdapterContext()
        result = adapter.execute(payload, ctx)

        # Normalize adapter result into ACK success/failure (v0.4 contract)
        if isinstance(result, dict) and result.get("ok") is False:
            err = result.get("error") if isinstance(result.get("error"), dict) else {}
            code = err.get("code") or "ADAPTER_ERROR"
            msg = err.get("message") or "Adapter execution failed"
            return _error_ack(ack, str(code), str(msg))

        return _success_ack(ack, result)

    # Non-demo intents: enforce canonical schema validation first
    ok, message = validate_command(payload)
    if not ok:
        return _error_ack(ack, "SCHEMA_INVALID", message)

    if _auth_required(payload) and not _has_auth_proof(payload):
        return _error_ack(ack, "AUTH_REQUIRED", "Owner authentication required")

    _apply_route_if_available(ack, payload)

    registry = default_registry()
    adapter = registry.resolve(intent)

    if adapter is None:
        return _error_ack(ack, "INTENT_UNSUPPORTED", f"Unsupported intent: {intent}")

    ctx = AdapterContext()
    result = adapter.execute(payload, ctx)

    # Normalize adapter result into ACK success/failure (v0.4 contract)
    if isinstance(result, dict) and result.get("ok") is False:
        err = result.get("error") if isinstance(result.get("error"), dict) else {}
        code = err.get("code") or "ADAPTER_ERROR"
        msg = err.get("message") or "Adapter execution failed"
        return _error_ack(ack, str(code), str(msg))

    return _success_ack(ack, result)


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)
