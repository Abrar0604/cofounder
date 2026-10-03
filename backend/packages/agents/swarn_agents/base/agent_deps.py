from dataclasses import dataclass
from typing import Any

# Forward references for type hinting since some modules are built in later phases
@dataclass(frozen=True)
class AgentDeps:
    engine: Any  # sqlalchemy.ext.asyncio.AsyncEngine
    redis: Any   # redis.asyncio.Redis
    settings: Any # packages.core.config.Settings
    registry: Any # ToolRegistry
    policies: Any # PolicyChain
    decisions: Any # DecisionRuntime
    models: Any   # ModelRouter
    checkpointer: Any
    store: Any
