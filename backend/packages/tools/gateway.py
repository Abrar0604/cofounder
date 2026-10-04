from typing import Any, Dict
from packages.tools.registry import ToolRegistry
from langgraph.types import interrupt

class ToolGateway:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def call_tool(self, name: str, params: Dict[str, Any], requires_approval: bool = False) -> Any:
        try:
            approval_id = None
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
                    
                approval_id = approval.get("approval_id", "dummy_approval")
                self.registry.pending_approvals[approval_id] = name
                
            result = self.registry.execute_tool(name, params, approval_id=approval_id)
            return {"status": "success", "data": result}
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
