from pydantic import BaseModel, Field
from typing import List

class MarketIntelRequest(BaseModel):
    industry: str
    target_audience: str

class Competitor(BaseModel):
    name: str
    strengths: List[str]
    weaknesses: List[str]

class MarketIntelResponse(BaseModel):
    market_size: str
    competitors: List[Competitor]
    trends: List[str]
