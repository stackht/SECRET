"""Audit service (original Phase 13).

Records and queries append-only audit entries for meaningful actions.
"""
from __future__ import annotations

from typing import Any

from app.models.audit import AuditLog
from app.models.user import User
from app.repositories.audit_repository import AuditRepository


class AuditService:
    """Write and read audit log entries."""

    def __init__(self, session) -> None:
        self._repo = AuditRepository(session)

    async def record(
        self,
        user: User | None,
        action: str,
        object_id: str | None = None,
        object_type: str | None = None,
        result: dict[str, Any] | None = None,
    ) -> AuditLog:
        return await self._repo.create(
            user_id=user.id if user else None,
            action=action,
            object_id=object_id,
            object_type=object_type,
            result=result or {},
        )

    async def list_recent(self, limit: int = 50) -> list[AuditLog]:
        return await self._repo.list_recent(limit=limit)
