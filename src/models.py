from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime

class Event(BaseModel):
    topic: str = Field(..., min_length=1)
    event_id: str = Field(..., min_length=1)
    timestamp: str  # ISO8601 format
    source: str = Field(..., min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "user.signup",
                "event_id": "evt-12345",
                "timestamp": "2025-10-22T10:30:00Z",
                "source": "api-server",
                "payload": {"user_id": 123, "email": "test@example.com"}
            }
        }

class EventBatch(BaseModel):
    events: list[Event]

class EventResponse(BaseModel):
    message: str
    received: int
    processed: int
    duplicates: int

class StatsResponse(BaseModel):
    received: int
    unique_processed: int
    duplicate_dropped: int
    topics: list[str]
    uptime: float