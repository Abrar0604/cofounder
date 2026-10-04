from fastapi import APIRouter
from typing import List, Dict, Any

import os
import json
import redis.asyncio as redis

router = APIRouter(prefix="/ventures", tags=["ventures"])

@router.get("/")
async def list_ventures() -> List[Dict[str, Any]]:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    client = redis.from_url(redis_url)
    try:
        data = await client.hgetall("swarn_ventures")
        if not data:
            return []
        
        ventures = []
        for v in data.values():
            try:
                ventures.append(json.loads(v))
            except:
                pass
        return ventures
    finally:
        await client.close()
