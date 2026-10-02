from pydantic import BaseModel, Field

class ApprovalRiskDefinition(BaseModel):
    version: str = "1.0"
    id: str = "D1_Approval_Risk"
    description: str = "Assesses the risk of automatically approving a user action."
    auto_threshold: float = Field(default=0.95, description="Threshold above which action is auto-approved")
    escalate_threshold: float = Field(default=0.60, description="Threshold below which action must be escalated to human")
