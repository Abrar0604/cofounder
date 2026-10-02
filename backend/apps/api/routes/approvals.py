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

@router.get("/{thread_id}")
async def get_approval(thread_id: str, service: ApprovalService = Depends(get_approval_service)):
    return await service.get_pending_approvals(thread_id)

@router.post("/{thread_id}/approve")
async def approve(thread_id: str, req: ApprovalRequest, service: ApprovalService = Depends(get_approval_service)):
    return await service.approve(thread_id, req.data)

@router.post("/{thread_id}/reject")
async def reject(thread_id: str, req: RejectionRequest, service: ApprovalService = Depends(get_approval_service)):
    return await service.reject(thread_id, req.reason)
