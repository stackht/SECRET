"""Shared cross-dialect column types (Phase 4).

Centralizes types that must behave identically on PostgreSQL (production) and
SQLite (tests):
- `BigSerialId`: BIGINT PK on Postgres, INTEGER rowid on SQLite (auto-increment).
- `JsonType`: JSONB on Postgres, JSON elsewhere.
"""
from sqlalchemy import JSON, BigInteger, Integer
from sqlalchemy.dialects.postgresql import JSONB

BigSerialId = BigInteger().with_variant(Integer, "sqlite")

JsonType = JSON().with_variant(JSONB, "postgresql")
