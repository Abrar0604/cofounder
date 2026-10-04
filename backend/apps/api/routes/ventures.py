from fastapi import APIRouter, Depends, Request
from typing import List, Dict, Any
import json
import logging
from apps.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ventures", tags=["ventures"])

@router.get("/")
async def list_ventures(request: Request, user_id: str = Depends(get_current_user)) -> List[Dict[str, Any]]:
    client = request.app.state.redis_client
    data = await client.hgetall("swarn_ventures")
    if not data:
        return []
    
    ventures = []
    for k, v in data.items():
        try:
            # handle both bytes and string
            val_str = v.decode('utf-8') if isinstance(v, bytes) else v
            venture_data = json.loads(val_str)
            # Filter by owner identity
            if venture_data.get("owner_id") == user_id:
                ventures.append(venture_data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Skipping invalid venture record {k}: {e}")
            
    return ventures
