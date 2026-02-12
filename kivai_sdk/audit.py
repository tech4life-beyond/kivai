"""
Audit logging foundation (v0.7)

Goal:
- Provide a deterministic, structured audit trail for intent execution
- Keep the interface minimal and stable
- Allow future backends (stdout/jsonl/file/db/otel) without changing runtime logic
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class AuditEvent:
    timestamp: str
    execution_id: str
    event: str
    data: dict[str, Any]


class AuditLogger:
    """
    Minimal structured audit logger.
    v0.7 default is a no-op logger (safe for libraries).
    """

    def emit(self, evt: AuditEvent) -> None:  # pragma: no cover
        return


class NullAuditLogger(AuditLogger):
    def emit(self, evt: AuditEvent) -> None:
        return


def make_event(
    execution_id: str, event: str, data: dict[str, Any] | None = None
) -> AuditEvent:
    return AuditEvent(
        timestamp=_utc_now_iso(),
        execution_id=execution_id,
        event=event,
        data=data or {},
    )


DEFAULT_AUDIT_LOGGER = NullAuditLogger()
