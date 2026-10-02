from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from packages.approvals.service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["approvals"])

# Dummy dependency injection setup
def get_approval_service() -> ApprovalService:
    # In a real setup, this would return an instantiated ApprovalService 
    # with a real checkpointer.
    class DummyCheckpointer:
        async def aget(self, config):
            return {"mock": "state"}
            
    return ApprovalService(DummyCheckpointer())

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
