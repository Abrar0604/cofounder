from packages.agents.swarn_agents.base.agent_deps import AgentDeps

class FakeModelRouter:
    def __init__(self, scripted_models):
        self.scripted_models = scripted_models or {}
        
    def get_model(self, tier: str, temperature: float = 0.0):
        # returns the pre-populated FakeChatModel for the tier
        return self.scripted_models.get(tier)

class FakeDecisionRuntime:
    def __init__(self, script):
        self.script = script or {}
        
    async def run(self, use_case: str, state: Any):
        return self.script.get(use_case)
        
    async def run_batch(self, use_case: str, states: list):
        return [self.script.get(use_case) for _ in states]

def build_test_deps(
    engine, 
    redis, 
    scripted_models: dict = None, 
    jev_script: dict = None
) -> AgentDeps:
    return AgentDeps(
        engine=engine,
        redis=redis,
        settings=None,
        registry=None,
        policies=None,
        decisions=FakeDecisionRuntime(jev_script),
        models=FakeModelRouter(scripted_models),
        checkpointer=None,
        store=None
    )
