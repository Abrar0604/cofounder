from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/ventures", tags=["ventures"])

# Global mock for demonstration until a DB is hooked up
MOCK_VENTURES = [
  {
    "id": "v1",
    "name": "Alpha Project",
    "status": "Active",
    "budget": "$120,000",
    "progress": "65%",
  },
  {
    "id": "v2",
    "name": "Beta Initiative",
    "status": "Pending",
    "budget": "$45,000",
    "progress": "10%",
  }
]

@router.get("/")
async def list_ventures() -> List[Dict[str, Any]]:
    return MOCK_VENTURES
