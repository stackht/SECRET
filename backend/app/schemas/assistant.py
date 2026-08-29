"""AI assistant schemas (original Phase 11)."""
from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class AssistantResponse(BaseModel):
    question: str
    answer: str
    source_ids: list[str] = Field(default_factory=list)
    found: bool = False
