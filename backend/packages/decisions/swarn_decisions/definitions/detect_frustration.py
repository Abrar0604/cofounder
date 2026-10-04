from pydantic import BaseModel

class DetectFrustrationState(BaseModel):
    task: str
    sentiment: str
