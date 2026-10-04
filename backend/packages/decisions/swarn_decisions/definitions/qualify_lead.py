from pydantic import BaseModel

class QualifyLeadState(BaseModel):
    task: str
    lead_score: int
