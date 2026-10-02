from typing import Any, Dict, Protocol
from pydantic import BaseModel

class Question(BaseModel):
    id: str
    context: Dict[str, Any]
    metadata: Dict[str, Any] = {}

class Decision(BaseModel):
    question_id: str
    confidence: float
    reasoning: str
    action: str

class DecisionModel(Protocol):
    async def evaluate(self, question: Question) -> Decision:
        ...
