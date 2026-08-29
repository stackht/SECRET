"""Analytics result schemas (Phase 8)."""
from pydantic import BaseModel, Field


class CentralityResult(BaseModel):
    entity_id: str
    degree: float
    betweenness: float
    closeness: float
    pagerank: float


class CentralityResponse(BaseModel):
    items: list[CentralityResult] = Field(default_factory=list)


class CommunityResult(BaseModel):
    community_id: int
    size: int
    entities: list[str] = Field(default_factory=list)


class CommunityResponse(BaseModel):
    communities: list[CommunityResult] = Field(default_factory=list)
    count: int = 0
    network_density: float = 0.0


class KeyEntityResult(BaseModel):
    entity_id: str
    score: float
    degree: int
    dominant_factor: str


class KeyEntitiesResponse(BaseModel):
    items: list[KeyEntityResult] = Field(default_factory=list)


class LinkPredictionResult(BaseModel):
    source: str
    target: str
    score: float


class LinkPredictionResponse(BaseModel):
    candidates: list[LinkPredictionResult] = Field(default_factory=list)


class RiskResult(BaseModel):
    entity_id: str
    risk_score: float
    risk_level: str
    confidence: float
    indicators: dict = Field(default_factory=dict)


class RiskResponse(BaseModel):
    items: list[RiskResult] = Field(default_factory=list)
    anomalies: list[str] = Field(default_factory=list)
