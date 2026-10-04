from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict
from packages.approvals.service import ApprovalService
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from packages.agents.orchestrator.graph import create_orchestrator_graph
import aiosqlite

router = APIRouter(prefix="/approvals", tags=["approvals"])

def get_approval_service(request: Request) -> ApprovalService:
    return request.app.state.approval_service

class ApprovalRequest(BaseModel):
    data: Dict[str, Any]

class RejectionRequest(BaseModel):
    reason: str

@router.get("/")
async def list_approvals(request: Request, service: ApprovalService = Depends(get_approval_service)) -> list[dict]:
    checkpointer = request.app.state.checkpointer
    
    # Extract unique thread_ids from the checkpointer
    thread_ids = set()
    async for c in checkpointer.alist(None):
        t = c.config.get("configurable", {}).get("thread_id")
        if t:
            thread_ids.add(t)
    
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
