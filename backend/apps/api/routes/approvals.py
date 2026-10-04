from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from packages.approvals.service import ApprovalService
from langgraph.checkpoint.memory import MemorySaver
from packages.agents.orchestrator.graph import create_orchestrator_graph

router = APIRouter(prefix="/approvals", tags=["approvals"])

# Shared checkpointer and graph
shared_checkpointer = MemorySaver()
shared_graph = create_orchestrator_graph(checkpointer=shared_checkpointer)
shared_approval_service = ApprovalService(shared_graph)

def get_approval_service() -> ApprovalService:
    return shared_approval_service

class ApprovalRequest(BaseModel):
    data: Dict[str, Any]

class RejectionRequest(BaseModel):
    reason: str

@router.get("/")
async def list_approvals(service: ApprovalService = Depends(get_approval_service)) -> list[dict]:
    # Extract unique thread_ids from the MemorySaver storage
    thread_ids = set([key[0] for key in shared_checkpointer.storage.keys()])
    
    pending = []
    for t_id in thread_ids:
        state = await service.get_pending_approvals(t_id)
        if state and state.get("status") == "pending_approval":
            # Extract data from the pending node state if possible, otherwise use generic data
            # state["pending_nodes"] contains the interrupted nodes
            pending.append({
                "id": f"approval_{t_id}",
                "title": f"Approval required for thread {t_id}",
                "requester": "System",
                "date": "Now",
                "details": f"Pending action on nodes: {state.get('pending_nodes', [])}. Please review and approve."
            })
    return pending

@router.get("/{thread_id}")
async def get_approval(thread_id: str, service: ApprovalService = Depends(get_approval_service)):
    return await service.get_pending_approvals(thread_id)

@router.post("/{thread_id}/approve")
async def approve(thread_id: str, req: ApprovalRequest, service: ApprovalService = Depends(get_approval_service)):
    return await service.approve(thread_id, req.data)

@router.post("/{thread_id}/reject")
async def reject(thread_id: str, req: RejectionRequest, service: ApprovalService = Depends(get_approval_service)):
    return await service.reject(thread_id, req.reason)
