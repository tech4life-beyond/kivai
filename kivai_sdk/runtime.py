import json
import uuid
from datetime import datetime, timezone
from typing import Any

from kivai_sdk.adapters import AdapterContext, default_registry
from kivai_sdk.adapters.capabilities import AdapterCapabilities
from kivai_sdk.adapters.contracts import normalize_adapter_output
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


def _adapter_capabilities(adapter: object, intent: str) -> AdapterCapabilities | None:
    """
    v0.9 strict: adapters must declare AdapterCapabilities via .capabilities.
    """
    caps = getattr(adapter, "capabilities", None)
    if caps is None:
        return None

    try:
        # if implemented as @property, getattr returns AdapterCapabilities directly
        value = caps
        if callable(caps):
            value = caps()
        if isinstance(value, AdapterCapabilities) and value.intent == intent:
            return value
    except Exception:
        return None

    return None


def _enforce_capability_match(
    ack: dict, caps: AdapterCapabilities
) -> tuple[bool, str | None]:
    """
    Strict: if routing produced a route, route must satisfy adapter required_capabilities.
    """
    route = ack.get("route") if isinstance(ack.get("route"), dict) else None
    if not route:
        return True, None

    route_caps = route.get("capabilities")
    if not isinstance(route_caps, list):
        return False, "ADAPTER_CAPABILITY_MISMATCH"

    route_set = {c for c in route_caps if isinstance(c, str)}
    required = set(caps.required_capabilities)

    if not required.issubset(route_set):
        return False, "ADAPTER_CAPABILITY_MISMATCH"

    return True, None


def _authorize_with_role_baseline(
    payload: dict, required_role: str | None
) -> tuple[bool, str | None]:
    """
    Evaluate authorization with an internal baseline role requirement (without mutating payload).
    """
    if not required_role:
        return evaluate_authorization(payload)
    shadow = {**payload, "_auth_required_role": required_role}
    return evaluate_authorization(shadow)


def execute_intent(
    payload: dict,
    config: ExecutionConfig = DEFAULT_EXECUTION_CONFIG,
    audit: AuditLogger = DEFAULT_AUDIT_LOGGER,
) -> dict:
    """
    v0.9 execution pipeline (strict adapter capabilities)
    - Adds execution_id for traceability
    - Supports strict mode (no normalization)
    - Enforces adapter-declared auth baseline and capability requirements deterministically
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

    registry = default_registry()
    adapter = registry.resolve(intent if isinstance(intent, str) else None)
    if adapter is None:
        audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
        return _error_ack(ack, "INTENT_UNSUPPORTED", f"Unsupported intent: {intent}")

    caps = _adapter_capabilities(adapter, str(intent))
    if caps is None:
        audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
        return _error_ack(
            ack,
            "ADAPTER_CAPABILITIES_MISSING",
            "Adapter does not declare AdapterCapabilities",
        )

    # Enforce adapter security baseline BEFORE schema validation to avoid SCHEMA_INVALID masking auth.
    if caps.requires_auth:
        authorized, error_code = _authorize_with_role_baseline(
            payload, caps.required_role
        )
        audit.emit(
            make_event(
                execution_id,
                "auth.evaluated",
                {
                    "authorized": bool(authorized),
                    "error_code": error_code,
                    "intent": intent,
                    "required_role": caps.required_role,
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
    else:
        # Normal policy evaluation for intents without adapter auth baseline
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

    # Echo is kept outside schema validation by design.
    if intent == "echo":
        _apply_route_if_available(ack, payload)
        if "route" in ack:
            audit.emit(make_event(execution_id, "route.resolved", ack["route"]))

        ok_caps, cap_err = _enforce_capability_match(ack, caps)
        if not ok_caps:
            audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
            return _error_ack(
                ack,
                cap_err or "ADAPTER_CAPABILITY_MISMATCH",
                "Adapter capability requirements not satisfied by routed device",
            )

        ctx = AdapterContext()
        raw = adapter.execute(payload, ctx)
        res = normalize_adapter_output(raw)

        if not res.ok:
            audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
            return _error_ack(ack, res.error.code, res.error.message)

        audit.emit(make_event(execution_id, "execute.end", {"status": "ok"}))
        return _success_ack(ack, res.data or {})

    # Schema validation for all non-echo intents
    ok, message = validate_command(payload)
    audit.emit(make_event(execution_id, "schema.validated", {"ok": bool(ok)}))
    if not ok:
        audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
        return _error_ack(ack, "SCHEMA_INVALID", message)

    _apply_route_if_available(ack, payload)
    if "route" in ack:
        audit.emit(make_event(execution_id, "route.resolved", ack["route"]))

    ok_caps, cap_err = _enforce_capability_match(ack, caps)
    if not ok_caps:
        audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
        return _error_ack(
            ack,
            cap_err or "ADAPTER_CAPABILITY_MISMATCH",
            "Adapter capability requirements not satisfied by routed device",
        )

    ctx = AdapterContext()
    raw = adapter.execute(payload, ctx)
    res = normalize_adapter_output(raw)

    if not res.ok:
        audit.emit(make_event(execution_id, "execute.end", {"status": "failed"}))
        return _error_ack(ack, res.error.code, res.error.message)

    audit.emit(make_event(execution_id, "execute.end", {"status": "ok"}))
    return _success_ack(ack, res.data or {})


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)
