import json
from typing import Any, Dict, AsyncGenerator
from .bus import EventBus
import os

class SSEPublisher:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.bus = EventBus(redis_url)

    async def publish(self, client_id: str, data: Dict[str, Any]):
        await self.bus.publish(client_id, "sse_event", data)

    async def event_generator(self, client_id: str) -> AsyncGenerator[str, None]:
        async for event in self.bus.subscribe(client_id):
            if event["type"] == "sse_event":
                data = event["payload"]
                yield f"data: {json.dumps(data)}\n\n"
            else:
                yield f"data: {json.dumps(event)}\n\n"
