import re

with open('backend/apps/worker/main.py', 'r') as f:
    content = f.read()

resume_task_code = """
async def resume_task(ctx, payload: dict):
    job_id = ctx.get("job_id", "unknown")
    print(f"Worker processing resume {job_id}")
    
    bus = ctx["bus"]
    client_id = payload.get("client_id", "default")
    answers = payload.get("answers", {})
    
    await bus.publish(client_id, "agent_action", {"text": "Resuming Orchestrator with survey answers..."})
    
    try:
        from packages.agents.swarn_agents.base.agent_deps import AgentDeps
        from packages.agents.swarn_agents.models.model_router import ModelRouter
        from packages.decisions.adapters.jev_client import JevClient
        from packages.brain.services.brain_service import BrainService
        from packages.agents.swarn_agents.registry import AGENT_SPECS
        from packages.agents.swarn_agents.orchestrator.graph import build_orchestrator_graph
        from langgraph.types import Command
        
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
        
        deps = AgentDeps(
            engine=None, redis=None, settings=None, registry=None, policies=None,
            decisions=decisions, models=models, checkpointer=checkpointer, store=store
        )
        graph = build_orchestrator_graph(deps, AGENT_SPECS)
        
        result = await graph.ainvoke(Command(resume=answers), config={"configurable": {"thread_id": client_id}})
        response_text = result.get("summary", "Done processing.")
    except Exception as e:
        response_text = f"Orchestrator error: {str(e)}"
        
    if isinstance(response_text, list):
        if len(response_text) > 0 and isinstance(response_text[0], dict) and "text" in response_text[0]:
            response_text = response_text[0]["text"]
        else:
            response_text = str(response_text)
    elif not isinstance(response_text, str):
        response_text = str(response_text)
    
    tokens = response_text.split(" ")
    for i, token in enumerate(tokens):
        await bus.publish(client_id, "agent_token", {"text": token + (" " if i < len(tokens)-1 else "")})
        import asyncio
        await asyncio.sleep(0.05)
        
    await bus.publish(client_id, "agent_done", {"status": "success"})
    return {"status": "success"}

class WorkerSettings:
"""

new_content = content.replace("class WorkerSettings:", resume_task_code + "\n    functions = [process_task, resume_task]\n    on_startup = startup\n    on_shutdown = shutdown\n    redis_settings = RedisSettings.from_dsn(os.getenv(\"REDIS_URL\", \"redis://localhost:6379/0\"))\n")
# remove old functions line
new_content = re.sub(r'class WorkerSettings:\n    functions = \[process_task\]\n    on_startup = startup\n    on_shutdown = shutdown\n    redis_settings = RedisSettings\.from_dsn\(os\.getenv\("REDIS_URL", "redis://localhost:6379/0"\)\)', '', new_content)


with open('backend/apps/worker/main.py', 'w') as f:
    f.write(new_content)
