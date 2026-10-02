from pydantic import BaseModel
from typing import Dict, Any

class FinancialRequest(BaseModel):
    business_model: str
    projected_users: int

class FinancialResponse(BaseModel):
    revenue_projection: float
    costs: Dict[str, float]
    break_even_months: int
