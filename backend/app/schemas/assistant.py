"""AI assistant schemas (original Phase 11, extended Task 5-6)."""
from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    case_key: str | None = Field(default=None, description="Case to scope the intelligence to")


class KeyFinding(BaseModel):
    label: str
    detail: str = ""


class AssistantEntity(BaseModel):
    id: str
    type: str = ""
    name: str = ""
    priority: float = 0.0


class AssistantRelItem(BaseModel):
    source: str
    target: str
    kind: str = "CONFIRMED"      # CONFIRMED | POTENTIAL
    confidence: float = 0.0


class AssistantRecommendation(BaseModel):
    kind: str
    subject: str
    priority: float = 0.0
    info_gain: float = 0.0
    reasoning: list[str] = Field(default_factory=list)
    recommended_data: str = ""
    window: str = ""


class IntelligenceResponse(BaseModel):
    type: str = "GENERAL_INVESTIGATION_QUERY"
    query: str
    summary: str = ""
    key_findings: list[KeyFinding] = Field(default_factory=list)
    entities: list[AssistantEntity] = Field(default_factory=list)
    relationships: list[AssistantRelItem] = Field(default_factory=list)
    anomalies: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    next_best_action: AssistantRecommendation | None = None
    source_ids: list[str] = Field(default_factory=list)
    found: bool = False


class AssistantResponse(BaseModel):
    question: str
    answer: str
    source_ids: list[str] = Field(default_factory=list)
    found: bool = False
    structured: IntelligenceResponse | None = None
