from typing import Any, Dict
from .interrupt_for_approval import ApprovalRequired, interrupt_for_approval

# Mock ToolResult for typing
class ToolResult:
    def __init__(self, output: Any):
        self.output = output

async def call_tool_with_approval(deps, state, tool_name: str, raw_args: Dict[str, Any]) -> ToolResult:
    ctx = state.get("ctx") # Typically we'd build ctx from state
    # Mocking tenant_session usage
    
    try:
        # Initial execution attempt
        result = await deps.registry.execute_tool(tool_name, raw_args)
        return ToolResult(output=result)
        
    except ApprovalRequired as e:
        # Pause graph execution and wait for human input
        resume_val = interrupt_for_approval(e)
        
        # We got resumed!
        decision = resume_val.get("decision")
        if decision != "approved":
            return ToolResult(output={"rejected": True})
            
        # Retry with the approval_id
        result = await deps.registry.execute_tool(
            tool_name, 
            raw_args, 
            approval_id=resume_val.get("approval_id")
        )
        return ToolResult(output=result)
