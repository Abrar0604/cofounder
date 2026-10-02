from typing import Dict, Any
from packages.decisions.ports import DecisionModel, Question, Decision
import asyncio

class JevClient(DecisionModel):
    def __init__(self, api_key: str = "dummy_key"):
        self.api_key = api_key
        
    async def evaluate(self, question: Question) -> Decision:
        # Dummy call to external Jev Model
        await asyncio.sleep(0.1)
        
        # Mock evaluation logic
        confidence = 0.85
        action = "APPROVE" if confidence > 0.8 else "REVIEW"
        
        return Decision(
            question_id=question.id,
            confidence=confidence,
            reasoning="Mock reasoning based on context",
            action=action
        )
