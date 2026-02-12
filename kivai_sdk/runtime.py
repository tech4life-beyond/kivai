import json
import uuid
from datetime import datetime, timezone
from typing import Any

from kivai_sdk.adapters import AdapterContext, default_registry
from kivai_sdk.audit import DEFAULT_AUDIT_LOGGER, AuditLogger, make_event
from kivai_sdk.config import DEFAULT_EXECUTION_CONFIG, ExecutionConfig
from kivai_sdk.router import route_target
from kivai_sdk.security import evaluate_authorization
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


def _make_ack_base(payload: dict, execution_id: str) -> dict:
    """
    Stable ACK envelope. Mirrors key routing fields for auditability.
    """
    return {
        "execution_id": execution_id,
        "intent_id": str(payload.get("intent_id") or uuid.uuid4()),
        "timestamp": _utc_now_iso(),
        "status": "ok",
        "intent": payload.get("intent"),
        "device_id": _get_target_device_id(payload),
    }


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
    Operational normalization (dev mode only):
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


def execute_intent(
    payload: dict,
    config: ExecutionConfig = DEFAULT_EXECUTION_CONFIG,
    audit: AuditLogger = DEFAULT_AUDIT_LOGGER,
) -> dict:
    """
    v0.7 execution pipeline (policy-driven, schema-aligned, auditable)
    - Adds execution_id for traceability
    - Supports strict mode (no normalization)
    """
    execution_id = str(uuid.uuid4())

    audit.emit(
        make_event(
            execution_id,
            "execute.start",
            {"strict": bool(config.strict), "intent": payload.get("intent")},
        )
    )

    # Dev-mode normalization only
    if not config.strict:
        _ensure_intent_id(payload)
        _ensure_meta(payload)
        _ensure_target(payload)
        _ensure_params(payload)

    ack = _make_ack_base(payload, execution_id)
    intent = payload.get("intent")

    # Debug/devtool intent: echo (kept outside schema by design)
    if intent == "echo":
        authorized, error_code = evaluate_authorization(payload)
        audit.emit(
            make_event(
                execution_id,
                "auth.evaluated",
                {
                    "authorized": bool(authorized),
                    "error_code": error_code,
                    "intent": "echo",
                },
            )
        )
        if not authorized:
            audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
            return _error_ack(
                ack,
                error_code or "AUTH_REQUIRED",
                "Authorization failed",
            )

        _apply_route_if_available(ack, payload)
        if "route" in ack:
            audit.emit(make_event(execution_id, "route.resolved", ack["route"]))

        registry = default_registry()
        adapter = registry.resolve("echo")
        if adapter is None:
            audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
            return _error_ack(
                ack, "INTENT_UNSUPPORTED", "Adapter not registered for intent: echo"
            )

        ctx = AdapterContext()
        result = adapter.execute(payload, ctx)

        if isinstance(result, dict) and result.get("ok") is False:
            err = result.get("error") if isinstance(result.get("error"), dict) else {}
            code = err.get("code") or "ADAPTER_ERROR"
            msg = err.get("message") or "Adapter execution failed"
            audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
            return _error_ack(ack, str(code), str(msg))

        audit.emit(make_event(execution_id, "execute.end", {"status": "ok"}))
        return _success_ack(ack, result)

    # Policy evaluation (v0.6+)
    authorized, error_code = evaluate_authorization(payload)
    audit.emit(
        make_event(
            execution_id,
            "auth.evaluated",
            {
                "authorized": bool(authorized),
                "error_code": error_code,
                "intent": intent,
            },
        )
    )
    if not authorized:
        audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
        return _error_ack(
            ack,
            error_code or "AUTH_REQUIRED",
            "Authorization failed",
        )

    # Schema validation for all non-echo intents
    ok, message = validate_command(payload)
    audit.emit(make_event(execution_id, "schema.validated", {"ok": bool(ok)}))
    if not ok:
        audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
        return _error_ack(ack, "SCHEMA_INVALID", message)

    _apply_route_if_available(ack, payload)
    if "route" in ack:
        audit.emit(make_event(execution_id, "route.resolved", ack["route"]))

    registry = default_registry()
    adapter = registry.resolve(intent)
    if adapter is None:
        audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
        return _error_ack(ack, "INTENT_UNSUPPORTED", f"Unsupported intent: {intent}")

    ctx = AdapterContext()
    result = adapter.execute(payload, ctx)

    if isinstance(result, dict) and result.get("ok") is False:
        err = result.get("error") if isinstance(result.get("error"), dict) else {}
        code = err.get("code") or "ADAPTER_ERROR"
        msg = err.get("message") or "Adapter execution failed"
        audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
        return _error_ack(ack, str(code), str(msg))

    audit.emit(make_event(execution_id, "execute.end", {"status": "ok"}))
    return _success_ack(ack, result)


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)
