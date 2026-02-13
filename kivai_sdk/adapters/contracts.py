from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class AdapterError:
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class AdapterResult:
    ok: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[AdapterError] = None

    @staticmethod
    def success(data: Dict[str, Any]) -> "AdapterResult":
        return AdapterResult(ok=True, data=data)

    @staticmethod
    def failure(
        code: str, message: str, details: Optional[Dict[str, Any]] = None
    ) -> "AdapterResult":
        return AdapterResult(
            ok=False, error=AdapterError(code=code, message=message, details=details)
        )


def normalize_adapter_output(output: Any) -> AdapterResult:
    """
    Back-compat normalizer:
    - If adapter already returns AdapterResult, keep it.
    - If adapter returns dict with ok False + error, convert.
    - Otherwise treat any dict as success payload.
    """
    if isinstance(output, AdapterResult):
        return output

    if isinstance(output, dict):
        if output.get("ok") is False:
            err = output.get("error") if isinstance(output.get("error"), dict) else {}
            return AdapterResult.failure(
                code=str(err.get("code") or "ADAPTER_ERROR"),
                message=str(err.get("message") or "Adapter execution failed"),
                details=err.get("details")
                if isinstance(err.get("details"), dict)
                else None,
            )
        return AdapterResult.success(output)

    return AdapterResult.failure(
        code="ADAPTER_INVALID_RESULT",
        message="Adapter returned unsupported result type",
        details={"type": str(type(output))},
    )
