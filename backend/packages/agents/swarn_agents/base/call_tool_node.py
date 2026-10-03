from typing import Any, Dict
from .interrupt_for_approval import ApprovalRequired, interrupt_for_approval

# Mock ToolResult for typing
class ToolResult:
    def __init__(self, output: Any):
        self.output = output

import inspect

async def call_tool_with_approval(deps, state, tool_name: str, raw_args: Dict[str, Any]) -> ToolResult:
    ctx = state.get("ctx") # Typically we'd build ctx from state
    # Mocking tenant_session usage
    
    try:
        # Initial execution attempt
        result = deps.registry.execute_tool(tool_name, raw_args)
        if inspect.isawaitable(result):
            result = await result
        return ToolResult(output=result)
        
    except ApprovalRequired as e:
        # Pause graph execution and wait for human input
        resume_val = interrupt_for_approval(e)
        
        # We got resumed!
        decision = resume_val.get("decision")
        if decision != "approved":
            return ToolResult(output={"rejected": True})
            
        approval_id = resume_val.get("approval_id")
        
        # Retry with the approval_id
        # Note: registry.execute_tool signature needs to accept approval_id
        result = deps.registry.execute_tool(
            tool_name, 
            raw_args, 
            approval_id=approval_id
        )
        if inspect.isawaitable(result):
            result = await result
        return ToolResult(output=result)
