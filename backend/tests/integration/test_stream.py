import pytest
import asyncio
from packages.core.bus import EventBus
from packages.core.sse import SSEPublisher

@pytest.mark.asyncio
async def test_event_bus():
    # Only run if redis is running locally (we'll just catch the connection error)
    bus = EventBus()
    try:
        await bus.redis.ping()
    except Exception:
        pytest.skip("Redis not available")

    # Subscribe in a background task
    events = []
    
    async def subscriber():
        async for msg in bus.subscribe("test_channel"):
            events.append(msg)
            if len(events) >= 2:
                break
                
    task = asyncio.create_task(subscriber())
    await asyncio.sleep(0.1) # Let it connect
    
    await bus.publish("test_channel", "test_type", {"foo": "bar"})
    await bus.publish("test_channel", "test_type2", {"foo": "baz"})
    
    await asyncio.wait_for(task, timeout=2.0)
    
    assert len(events) == 2
    assert events[0]["type"] == "test_type"
    assert events[1]["payload"]["foo"] == "baz"
