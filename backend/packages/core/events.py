from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class DomainEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str
    payload: Dict[str, Any]
