"""Temporal + location analysis schemas (original Phase 9)."""
from pydantic import BaseModel, Field


class TimeWindowResult(BaseModel):
    window_start: str
    count: int
    sources: list[str] = Field(default_factory=list)


class EventSequenceItem(BaseModel):
    record_id: str
    timestamp: str
    source: str
    summary: str
    location: str | None = None


class BurstResult(BaseModel):
    window_start: str
    count: int


class LocationActivityEntry(BaseModel):
    location: str
    events: int
    level: str


class TemporalLocationResponse(BaseModel):
    windows: list[TimeWindowResult] = Field(default_factory=list)
    event_sequence: list[EventSequenceItem] = Field(default_factory=list)
    communication_bursts: list[BurstResult] = Field(default_factory=list)
    location_activity: list[LocationActivityEntry] = Field(default_factory=list)
    movement: list[EventSequenceItem] = Field(default_factory=list)
