from pydantic import BaseModel
from typing import List

class ValidationRequest(BaseModel):
    idea: str
    target_market: str

class ValidationResponse(BaseModel):
    is_valid: bool
    score: int
    feedback: List[str]
