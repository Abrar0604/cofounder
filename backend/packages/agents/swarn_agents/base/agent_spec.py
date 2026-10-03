from dataclasses import dataclass
from typing import Callable, Any, FrozenSet
from .agent_deps import AgentDeps

@dataclass
class AgentSpec:
    name: str
    allowed_tools: FrozenSet[str]
    consumes: FrozenSet[str]
    emits: FrozenSet[str]
    build_graph: Callable[[AgentDeps], Any]
