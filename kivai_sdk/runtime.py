import json
import uuid
from datetime import datetime, timezone
from typing import Any

from kivai_sdk.adapters import AdapterContext, default_registry
from kivai_sdk.router import route_target
from kivai_sdk.validator import validate_command


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_target_device_id(payload: dict) -> str | None:
    target = payload.get("target")
    if isinstance(target, dict):
        device_id = target.get("device_id")
        if isinstance(device_id, str) and device_id.strip():
            return device_id
    return None


def _make_ack_base(payload: dict) -> dict:
    """
    Stable ACK envelope. Mirrors key routing fields for auditability.
    """
    return {
        "intent_id": str(payload.get("intent_id") or uuid.uuid4()),
        "timestamp": _utc_now_iso(),
        "status": "ok",
        "intent": payload.get("intent"),
        "device_id": _get_target_device_id(payload),
    }


def _auth_required(payload: dict) -> bool:
    """
    Schema-aligned auth:
      auth = { required_role, token }
    If auth exists, it's required.
    Additionally, some intents (e.g., unlock_door) may require auth by baseline.
    """
    if payload.get("_auth_required_role"):
        return True
    auth = payload.get("auth")
    return bool(isinstance(auth, dict))


def _has_auth_proof(payload: dict) -> bool:
    auth = payload.get("auth")
    if not isinstance(auth, dict):
        return False

    token = auth.get("token")
    required_role = auth.get("required_role")

    if not (isinstance(token, str) and token.strip()):
        return False
    if not (isinstance(required_role, str) and required_role.strip()):
        return False

    baseline_role = payload.get("_auth_required_role")
    if isinstance(baseline_role, str) and baseline_role.strip():
        return required_role == baseline_role

    return True


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
    if not ack.get("device_id"):
        ack["device_id"] = match.device.device_id


def _ensure_meta(payload: dict) -> None:
    """
    Operational normalization:
    - Schema requires meta. If missing, supply safe defaults.
    """
    meta = payload.get("meta")
    if not isinstance(meta, dict):
        payload["meta"] = {
            "timestamp": _utc_now_iso(),
            "language": "en",
            "confidence": float(
                payload.get("confidence")
                if isinstance(payload.get("confidence"), (int, float))
                else 1.0
            ),
            "source": "gateway",
        }
        return

    meta.setdefault("timestamp", _utc_now_iso())
    meta.setdefault("language", "en")
    if "confidence" not in meta:
        meta["confidence"] = float(
            payload.get("confidence")
            if isinstance(payload.get("confidence"), (int, float))
            else 1.0
        )


def _ensure_intent_id(payload: dict) -> None:
    if (
        not isinstance(payload.get("intent_id"), str)
        or len(payload.get("intent_id", "")) < 8
    ):
        payload["intent_id"] = str(uuid.uuid4())


def _ensure_target(payload: dict) -> None:
    """
    Schema requires target. If missing, create an empty target.
    """
    if not isinstance(payload.get("target"), dict):
        payload["target"] = {}


def _ensure_params(payload: dict) -> None:
    if "params" not in payload or not isinstance(payload.get("params"), dict):
        payload["params"] = {}


def _enforce_unlock_door_auth(payload: dict) -> None:
    """
    v0.5 baseline: unlock_door requires owner auth by default.

    IMPORTANT:
    - Do NOT inject an auth object with an empty token before schema validation,
      because schema requires token minLength 1 if auth is present.
    - Instead, record an internal requirement and let runtime return AUTH_REQUIRED
      deterministically if auth proof is missing.
    """
    if payload.get("intent") != "unlock_door":
        return

    payload["_auth_required_role"] = "owner"


def execute_intent(payload: dict) -> dict:
    """
    v0.5 execution pipeline (schema-aligned)
    """
    _ensure_intent_id(payload)
    _ensure_meta(payload)
    _ensure_target(payload)
    _ensure_params(payload)

    _enforce_unlock_door_auth(payload)

    ack = _make_ack_base(payload)
    intent = payload.get("intent")

    if intent == "echo":
        if _auth_required(payload) and not _has_auth_proof(payload):
            return _error_ack(ack, "AUTH_REQUIRED", "Owner authentication required")

        _apply_route_if_available(ack, payload)

        registry = default_registry()
        adapter = registry.resolve("echo")
        if adapter is None:
            return _error_ack(
                ack, "INTENT_UNSUPPORTED", "Adapter not registered for intent: echo"
            )

        ctx = AdapterContext()
        result = adapter.execute(payload, ctx)

        if isinstance(result, dict) and result.get("ok") is False:
            err = result.get("error") if isinstance(result.get("error"), dict) else {}
            code = err.get("code") or "ADAPTER_ERROR"
            msg = err.get("message") or "Adapter execution failed"
            return _error_ack(ack, str(code), str(msg))

        return _success_ack(ack, result)

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

    if isinstance(result, dict) and result.get("ok") is False:
        err = result.get("error") if isinstance(result.get("error"), dict) else {}
        code = err.get("code") or "ADAPTER_ERROR"
        msg = err.get("message") or "Adapter execution failed"
        return _error_ack(ack, str(code), str(msg))

    return _success_ack(ack, result)


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)
