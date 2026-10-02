from fastapi import APIRouter, HTTPException
from packages.core.experiments import ExperimentAssignment
from pydantic import BaseModel

router = APIRouter(prefix="/experiments", tags=["experiments"])
assigner = ExperimentAssignment()

class AssignmentRequest(BaseModel):
    user_id: str
    experiment_id: str

@router.post("/assign")
async def get_assignment(req: AssignmentRequest):
    try:
        bucket = assigner.assign_user(req.user_id, req.experiment_id)
        return {"user_id": req.user_id, "experiment_id": req.experiment_id, "bucket": bucket}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
