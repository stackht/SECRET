"""SQLAlchemy ORM models.

Importing each model registers it on Base.metadata (used by Alembic autogenerate
and by `create_all` helpers).
"""
from app.models.user import User, UserRole, UserStatus
from app.models.criminal import CriminalProfile, EntityType, RiskLevel
from app.models.case import Case, CaseCriminal, CasePriority, CaseStatus
from app.models.audit import AuditLog

__all__ = [
    "User",
    "UserRole",
    "UserStatus",
    "CriminalProfile",
    "EntityType",
    "RiskLevel",
    "Case",
    "CaseCriminal",
    "CasePriority",
    "CaseStatus",
    "AuditLog",
]
