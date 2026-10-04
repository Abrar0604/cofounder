from pydantic import BaseModel, Field

class ContentScreeningDefinition(BaseModel):
    version: str = "1.0"
    id: str = "D2_Content_Screening"
    description: str = "Assesses if user input or generated content violates safety or brand guidelines."
    auto_threshold: float = Field(default=0.99, description="Threshold above which content is marked safe automatically")
    escalate_threshold: float = Field(default=0.75, description="Threshold below which content is blocked or sent for human review")
