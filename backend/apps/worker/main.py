import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from packages.core.bus import EventBus
import os
from dotenv import load_dotenv

load_dotenv()

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
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash")
        prompt = f"The user says: {payload.get('message', '')}. Please provide a helpful response as Swarn AI, an intelligent autonomous agent managing their venture. Be concise."
        res = await llm.ainvoke(prompt)
        response_text = res.content
    except Exception as e:
        response_text = f"I have successfully received your request, but I encountered an error connecting to the LLM (Ensure GOOGLE_API_KEY is set). Error: {str(e)}"
    
    tokens = response_text.split(" ")
    
    for i, token in enumerate(tokens):
        await bus.publish(client_id, "agent_token", {"text": token + (" " if i < len(tokens)-1 else "")})
        await asyncio.sleep(0.05)
        
    await bus.publish(client_id, "agent_done", {"status": "success"})
    return {"status": "success"}

class WorkerSettings:
    functions = [process_task]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
