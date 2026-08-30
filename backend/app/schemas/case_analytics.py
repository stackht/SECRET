"""Per-case analytics schemas (comms/tx/timeline/location)."""
from pydantic import BaseModel, Field


class CommsResponse(BaseModel):
    total_communications: int = 0
    top_contacts: list[dict] = Field(default_factory=list)
    flows: list[dict] = Field(default_factory=list)
    bursts: list[dict] = Field(default_factory=list)


class TransResponse(BaseModel):
    total_transactions: int = 0
    total_amount: float = 0.0
    flows: list[dict] = Field(default_factory=list)
    top_senders: list[dict] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    timestamp: str
    record_id: str
    source_id: str
    summary: str
    location: str | None = None


class LocationSummary(BaseModel):
    name: str
    observations: int


class LocationsResponse(BaseModel):
    locations: list[LocationSummary] = Field(default_factory=list)
    visits: list[dict] = Field(default_factory=list)