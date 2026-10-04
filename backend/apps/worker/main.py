import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from packages.core.bus import EventBus
import os
from dotenv import load_dotenv

load_dotenv()

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

async def startup(ctx):
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ctx["bus"] = EventBus(redis_url)
    ctx["checkpointer_cm"] = AsyncSqliteSaver.from_conn_string("checkpoints.db")
    ctx["checkpointer"] = await ctx["checkpointer_cm"].__aenter__()
    await ctx["checkpointer"].setup()

async def shutdown(ctx):
    bus = ctx.get("bus")
    if bus:
        await bus.redis.close()
    if "checkpointer_cm" in ctx:
        await ctx["checkpointer_cm"].__aexit__(None, None, None)

async def process_task(ctx, payload: dict):
    job_id = ctx.get("job_id", "unknown")
    print(f"Worker processing task {job_id}")
    
    bus = ctx["bus"]
    client_id = payload.get("client_id", "default")
    user_message = payload.get("message", "")
    
    await bus.publish(client_id, "agent_thought", {"text": "Initializing Orchestrator and JevClient..."})
    
    try:
        from packages.agents.swarn_agents.base.agent_deps import AgentDeps
        from packages.agents.swarn_agents.models.model_router import ModelRouter
        from packages.decisions.adapters.jev_client import JevClient
        from packages.brain.services.brain_service import BrainService
        from packages.agents.swarn_agents.registry import AGENT_SPECS
        from packages.agents.swarn_agents.orchestrator.graph import build_orchestrator_graph
        
        # Instantiate real dependencies
        models = ModelRouter(settings=None)
        jev_client = JevClient()
        
        class DecisionRuntimeWrapper:
            def __init__(self, model):
                self.model = model
            async def run(self, use_case: str, state_obj) -> dict:
                from packages.decisions.ports import Question
                if hasattr(state_obj, "__dict__"):
                    context = state_obj.__dict__
                else:
                    context = dict(state_obj)
                q = Question(id=use_case, context=context, metadata={})
                return await self.model.evaluate(q)
                
        decisions = DecisionRuntimeWrapper(jev_client)
        store = BrainService()
        checkpointer = ctx["checkpointer"]
        
        # --- NEW: Extract Venture Info and Create it automatically ---
        import json
        from langchain_google_genai import ChatGoogleGenerativeAI
        fast_llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash")
        
        # Ensure a distinct ID per request or rely on client_id for distinct sessions
        import uuid
        venture_id = f"v_{client_id}"
        
        # Check existing using shared Redis store
        existing = await bus.redis.hget("swarn_ventures", venture_id)
        if not existing:
            venture_name = "New Venture"
            try:
                extract_prompt = f"Extract a short 2-3 word project name from this prompt. If it's about coffee, call it 'Coffee Project'. If unknown, call it 'New Venture'. Prompt: {user_message}"
                name_res = await fast_llm.ainvoke(extract_prompt)
                if name_res and name_res.content and isinstance(name_res.content, str) and name_res.content.strip():
                    venture_name = name_res.content.strip().replace("'", "").replace('"', '')
            except Exception as llm_err:
                print(f"Name extraction failed: {llm_err}")
            
            venture_data = {
                "id": venture_id,
                "name": venture_name,
                "status": "Inception",
                "budget": "TBD",
                "progress": "0%",
                "owner_id": payload.get("user_id", "u1")
            }
            # Save to shared store
            await bus.redis.hset("swarn_ventures", venture_id, json.dumps(venture_data))
            store.create_venture(venture_id, venture_data)
        elif existing:
            # Load it into the local BrainService store
            store.create_venture(venture_id, json.loads(existing))
        # -------------------------------------------------------------
        
        deps = AgentDeps(
            engine=None,
            redis=None,
            settings=None,
            registry=None,
            policies=None,
            decisions=decisions,
            models=models,
            checkpointer=checkpointer,
            store=store
        )
        
        graph = build_orchestrator_graph(deps, AGENT_SPECS)
        
        await bus.publish(client_id, "agent_action", {"text": "Routing message through LangGraph Orchestrator..."})
        
        state = {
            "messages": [("human", user_message)],
            "tenant_id": "t1", "venture_id": venture_id, "user_id": payload.get("user_id", "u1"), "role": "admin",
            "run_id": job_id, "agent": "orchestrator", "task": "",
            "artifacts": [], "events": [], "needs_human": False, "error": None,
            "next_agents": [], "agent_hops": 0
        }
        
        result = await graph.ainvoke(state, config={"configurable": {"thread_id": client_id}})
        
        response_text = result.get("summary", "Done processing.")
    except Exception as e:
        response_text = f"Orchestrator error: {str(e)}"
        
    if isinstance(response_text, list):
        # Gemini sometimes returns a list of content blocks
        if len(response_text) > 0 and isinstance(response_text[0], dict) and "text" in response_text[0]:
            response_text = response_text[0]["text"]
        else:
            response_text = str(response_text)
    elif not isinstance(response_text, str):
        response_text = str(response_text)
    
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
