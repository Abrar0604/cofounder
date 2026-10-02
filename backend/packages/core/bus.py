import json
import logging
from typing import Any, Dict, Optional
from redis.asyncio import Redis
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = Redis.from_url(redis_url)

    async def publish(self, stream_name: str, event_data: Dict[str, Any]) -> str:
        """Publish an event to a Redis Stream."""
        try:
            # Convert values to strings as Redis Streams requires
            serialized_data = {k: json.dumps(v) if not isinstance(v, str) else v for k, v in event_data.items()}
            message_id = await self.redis.xadd(stream_name, serialized_data)
            logger.info(f"Published event to {stream_name}: {message_id}")
            return message_id.decode('utf-8') if isinstance(message_id, bytes) else message_id
        except Exception as e:
            logger.error(f"Failed to publish event to {stream_name}: {e}")
            raise

    async def close(self):
        await self.redis.close()
