from pydantic import BaseModel
from typing import List

class DefineLandingPageState(BaseModel):
    task: str
    target_audience: str
