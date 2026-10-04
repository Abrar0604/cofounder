from pydantic import BaseModel

class DraftContentCalendarState(BaseModel):
    task: str
    timeline: str
