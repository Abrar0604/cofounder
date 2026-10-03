import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from packages.core.bus import EventBus
import os

# Note: In a real system, you'd wire up the real AgentDeps here.
# For now, we mock the dependency injection just to run the worker.

async def startup(ctx):
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ctx["bus"] = EventBus(redis_url)

async def shutdown(ctx):
    bus = ctx.get("bus")
    if bus:
        await bus.redis.close()

async def process_task(ctx, payload: dict):
    job_id = ctx.get("job_id", "unknown")
    print(f"Worker processing task {job_id}")
    
    bus = ctx["bus"]
    client_id = payload.get("client_id", "default")
    
    await bus.publish(client_id, "agent_thought", {"text": "Processing your request..."})
    await asyncio.sleep(1)
    await bus.publish(client_id, "agent_action", {"text": "Invoking Orchestrator..."})
    await asyncio.sleep(1)
    
    response_text = "I have successfully analyzed the market data and found the following..."
    tokens = response_text.split(" ")
    
    for token in tokens:
        await bus.publish(client_id, "agent_token", {"text": token + " "})
        await asyncio.sleep(0.1)
        
    await bus.publish(client_id, "agent_done", {"status": "success"})
    return {"status": "success"}

class WorkerSettings:
    functions = [process_task]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
