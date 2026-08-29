"""Common schemas shared across modules (Phase 3)."""
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Uniform error body returned by the API."""

    detail: str
