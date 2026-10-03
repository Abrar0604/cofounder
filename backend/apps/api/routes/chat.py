from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from arq import create_pool
from arq.connections import RedisSettings
import os

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    client_id: str

@router.post("/")
async def submit_chat(req: ChatRequest):
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        redis_settings = RedisSettings.from_dsn(redis_url)
        arq_pool = await create_pool(redis_settings)
        await arq_pool.enqueue_job(
            "process_task", 
            f"task_{req.client_id}",
            {"client_id": req.client_id, "message": req.message}
        )
        return {"status": "enqueued", "client_id": req.client_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
