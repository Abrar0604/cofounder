from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    client_id: str

@router.post("/")
async def submit_chat(req: ChatRequest, request: Request):
    try:
        arq_pool = request.app.state.arq_pool
        await arq_pool.enqueue_job(
            "process_task", 
            payload={"client_id": req.client_id, "message": req.message}
        )
        return {"status": "enqueued", "client_id": req.client_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
