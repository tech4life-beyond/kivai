"""
Policy Engine (v0.6)

Responsible for:
- Determining if an intent requires authorization
- Validating auth proof presence and role alignment
- Returning deterministic decision

Does NOT:
- Validate schema
- Execute adapters
- Perform routing
"""

from typing import Optional, Tuple

from kivai_sdk.security.roles import Role


# Baseline intent → required role mapping
_INTENT_ROLE_POLICY: dict[str, Role] = {
    "unlock_door": "owner",
    # extend here in future versions
}


def required_role_for_intent(intent: str) -> Optional[Role]:
    return _INTENT_ROLE_POLICY.get(intent)


def evaluate_authorization(payload: dict) -> Tuple[bool, Optional[str]]:
    """
    Returns:
        (authorized: bool, error_code: Optional[str])
    """
    intent = payload.get("intent")
    required_role = required_role_for_intent(intent)

    # If no role required → always allowed
    if required_role is None:
        return True, None

    auth = payload.get("auth")

    if not isinstance(auth, dict):
        return False, "AUTH_REQUIRED"

    token = auth.get("token")
    role = auth.get("required_role")

    if not isinstance(token, str) or not token.strip():
        return False, "AUTH_REQUIRED"

    if role != required_role:
        return False, "AUTH_FORBIDDEN"

    # v0.6 baseline does not verify token cryptographically yet
    return True, None
