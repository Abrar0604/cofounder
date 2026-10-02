import json
import asyncio
from typing import Any, Dict, AsyncGenerator

class SSEPublisher:
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = {}

    def subscribe(self, client_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.queues[client_id] = queue
        return queue

    def unsubscribe(self, client_id: str):
        if client_id in self.queues:
            del self.queues[client_id]

    async def publish(self, client_id: str, data: Dict[str, Any]):
        if client_id in self.queues:
            await self.queues[client_id].put(data)

    async def event_generator(self, client_id: str) -> AsyncGenerator[str, None]:
        queue = self.subscribe(client_id)
        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
        finally:
            if self.queues.get(client_id) is queue:
                del self.queues[client_id]
