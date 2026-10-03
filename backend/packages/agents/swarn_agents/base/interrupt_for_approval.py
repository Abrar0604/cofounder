from langgraph.types import interrupt
from typing import Dict, Any

class ApprovalRequired(Exception):
    def __init__(self, approval_id: str, action: str, args_preview: str):
        self.approval_id = approval_id
        self.action = action
        self.args_preview = args_preview

def interrupt_for_approval(error: ApprovalRequired) -> Dict[str, Any]:
    # Pure code before interrupt: prep payload
    payload = {
        "kind": "approval",
        "approval_id": error.approval_id,
        "action": error.action,
        "args_preview": error.args_preview
    }
    
    # LangGraph interrupt
    resume_val = interrupt(payload)
    
    # Returns the resume value which should be a dict with approval_id and decision
    return resume_val
