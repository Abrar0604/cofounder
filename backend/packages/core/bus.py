import redis.asyncio as redis
import json
from typing import Dict, Any, AsyncGenerator

class EventBus:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url)
        
    async def publish(self, channel: str, event_type: str, payload: Dict[str, Any]):
        message = {
            "type": event_type,
            "payload": payload
        }
        await self.redis.publish(channel, json.dumps(message))
        
    async def subscribe(self, channel: str) -> AsyncGenerator[Dict[str, Any], None]:
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        
        # Wait for subscription confirmation
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=False, timeout=1.0)
            if msg and msg.get("type") == "subscribe":
                break
                
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        yield data
                    except json.JSONDecodeError:
                        continue
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
