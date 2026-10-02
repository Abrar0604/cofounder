from typing import Any, Dict, Protocol
from pydantic import BaseModel, Field

class AgentInput(BaseModel):
    task: str
    context: Dict[str, Any] = Field(default_factory=dict)
    thread_id: str

class AgentOutput(BaseModel):
    status: str
    result: Dict[str, Any]
    error: str | None = None

class AgentProtocol(Protocol):
    async def invoke(self, input_data: AgentInput) -> AgentOutput:
        ...
