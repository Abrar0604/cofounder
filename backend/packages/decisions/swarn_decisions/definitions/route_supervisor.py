from dataclasses import dataclass
from typing import Literal

@dataclass
class RouteSupervisorState:
    task: str
    active_agent: str
    available_agents: list[str]

D3_OPTIONS = ('market_intel', 'validation', 'financial', 'legal', 'web', 'marketing', 'sales', 'support', 'operations', 'end')
