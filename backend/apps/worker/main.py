import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from packages.core.bus import EventBus
import os
from dotenv import load_dotenv

load_dotenv()

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
    user_message = payload.get("message", "")
    
    await bus.publish(client_id, "agent_thought", {"text": "Initializing Orchestrator and JevClient..."})
    
    try:
        from packages.agents.swarn_agents.base.agent_deps import AgentDeps
        from packages.agents.swarn_agents.models.model_router import ModelRouter
        from packages.decisions.adapters.jev_client import JevClient
        from packages.brain.services.brain_service import BrainService
        from packages.agents.swarn_agents.registry import AGENT_SPECS
        from packages.agents.swarn_agents.orchestrator.graph import build_orchestrator_graph
        from langgraph.checkpoint.memory import MemorySaver
        
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
        checkpointer = MemorySaver()
        
        # --- NEW: Extract Venture Info and Create it automatically ---
        from langchain_google_genai import ChatGoogleGenerativeAI
        fast_llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash")
        extract_prompt = f"Extract a short 2-3 word project name from this prompt. If it's about coffee, call it 'Coffee Project'. If unknown, call it 'New Venture'. Prompt: {user_message}"
        name_res = await fast_llm.ainvoke(extract_prompt)
        venture_name = name_res.content.strip().replace("'", "").replace('"', '')
        
        # Create it in our mock store
        venture_id = f"v_{client_id}"
        if venture_id not in store.ventures:
            store.create_venture(venture_id, {
                "name": venture_name,
                "status": "Inception",
                "budget": "TBD",
                "progress": "0%"
            })
            # To make it globally accessible for the dashboard route, we should append to the global MOCK_VENTURES in the router
            try:
                from apps.api.routes.ventures import MOCK_VENTURES
                # Check if it exists
                if not any(v.get("id") == venture_id for v in MOCK_VENTURES):
                    MOCK_VENTURES.append({
                        "id": venture_id,
                        "name": venture_name,
                        "status": "Inception",
                        "budget": "TBD",
                        "progress": "0%"
                    })
            except ImportError:
                pass
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
            "tenant_id": "t1", "venture_id": "v1", "user_id": "u1", "role": "admin",
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
