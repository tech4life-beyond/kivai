import json
import uuid
from datetime import datetime, timezone
from typing import Any

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


def execute_intent(payload: dict) -> dict:
    """
    v0.1 execution pipeline:
      1) Validate schema (non-demo intents)
      2) Enforce auth stub (if required)
      3) Route by intent (adapter)
      4) Return ACK envelope
    """
    ack = _make_ack_base(payload)

    intent = payload.get("intent")

    # v0.1: allow a small "developer demo" intent that is intentionally outside
    # the canonical schema. This keeps the schema stable while enabling a runnable loop.
    if intent == "echo":
        if _auth_required(payload) and not _has_auth_proof(payload):
            return _error_ack(ack, "AUTH_REQUIRED", "Owner authentication required")
        msg = payload.get("message", "")
        return _success_ack(ack, {"echo": msg})

    # For all non-demo intents, enforce canonical schema validation.
    ok, message = validate_command(payload)
    if not ok:
        return _error_ack(ack, "SCHEMA_INVALID", message)

    if _auth_required(payload) and not _has_auth_proof(payload):
        return _error_ack(ack, "AUTH_REQUIRED", "Owner authentication required")

    # v0.1: non-demo intents are not executed yet (adapter layer comes next).
    return _error_ack(ack, "INTENT_UNSUPPORTED", f"Unsupported intent: {intent}")


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)
