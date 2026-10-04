from fastapi import APIRouter, Depends, Query
from packages.core.experiments import ExperimentService
from typing import Dict

router = APIRouter(prefix="/v1/experiments", tags=["experiments"])

def get_experiment_service():
    return ExperimentService()

@router.get("/assignments")
async def get_user_assignments(
    user_id: str = Query(..., description="The ID of the user"),
    service: ExperimentService = Depends(get_experiment_service)
) -> Dict[str, str]:
    """
    Get all active experiment variant assignments for a given user.
    """
    return service.get_all_assignments_for_user(user_id)
