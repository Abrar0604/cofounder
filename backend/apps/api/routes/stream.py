from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from packages.core.sse import SSEPublisher

router = APIRouter(prefix="/stream", tags=["stream"])
publisher = SSEPublisher()

@router.get("/{client_id}")
async def stream_events(client_id: str, request: Request):
    return StreamingResponse(
        publisher.event_generator(client_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/{client_id}/test-publish")
async def test_publish(client_id: str, data: dict):
    await publisher.publish(client_id, data)
    return {"status": "published"}
