from typing import Any, Dict, Optional
from packages.tools.registry import ToolRegistry
from packages.decisions.ports import DecisionModel, Question
from packages.decisions.policy.apply_threshold import apply_threshold
from langgraph.types import interrupt
import uuid

class ToolGateway:
    def __init__(self, registry: ToolRegistry, decision_model: Optional[DecisionModel] = None):
        self.registry = registry
        self.decision_model = decision_model

    async def call_tool(self, name: str, params: Dict[str, Any], requires_approval: bool = False, evaluate_risk: bool = True) -> Any:
        try:
            approval_id = None
            
            # Step 1: Decision Layer Policy Evaluation (D1 Approval Risk)
            if self.decision_model and evaluate_risk:
                question = Question(
                    id="D1_Approval_Risk",
                    context={"tool": name, "params": params},
                    metadata={}
                )
                decision = await self.decision_model.evaluate(question)
                
                # Apply Threshold Policy (AUTO, CONFIRM, ESCALATE)
                policy_action = apply_threshold(decision, auto_threshold=0.9, confirm_threshold=0.7)
                
                if policy_action in ("ESCALATE", "CONFIRM"):
                    requires_approval = True
                    
            if requires_approval:
                # Suspend execution until approved
                approval = interrupt({
                    "action": "requires_approval",
                    "tool": name,
                    "params": params
                })
                if approval.get("action") != "approve":
                    return {"status": "rejected", "reason": approval.get("reason", "No reason provided")}
                
                # Option to overwrite params from approval data
                if "data" in approval and isinstance(approval["data"], dict):
                    params.update(approval["data"])
                    
                approval_id = approval.get("approval_id") or str(uuid.uuid4())
                self.registry.pending_approvals[approval_id] = name
                
            result = self.registry.execute_tool(name, params, approval_id=approval_id)
            return {"status": "success", "data": result}
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
