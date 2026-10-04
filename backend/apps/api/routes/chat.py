from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from apps.api.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    client_id: str

@router.post("/")
async def submit_chat(req: ChatRequest, request: Request, user_id: str = Depends(get_current_user)):
    try:
        arq_pool = request.app.state.arq_pool
        await arq_pool.enqueue_job(
            "process_task", 
            payload={"client_id": req.client_id, "message": req.message, "user_id": user_id}
        )
        return {"status": "enqueued", "client_id": req.client_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ResumeRequest(BaseModel):
    client_id: str
    answers: dict

@router.post("/resume")
async def resume_chat(req: ResumeRequest, request: Request, user_id: str = Depends(get_current_user)):
    try:
        arq_pool = request.app.state.arq_pool
        await arq_pool.enqueue_job(
            "resume_task", 
            payload={"client_id": req.client_id, "answers": req.answers, "user_id": user_id}
        )
        return {"status": "enqueued", "client_id": req.client_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
