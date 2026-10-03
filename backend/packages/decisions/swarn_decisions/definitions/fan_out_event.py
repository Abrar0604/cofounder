from dataclasses import dataclass
from typing import Literal

@dataclass
class FanOutEventState:
    event_type: str
    event_payload: str
    available_agents: list[str]

# Determines which agents should be awakened by this event
D5_OPTIONS = ('market_intel', 'validation', 'financial', 'legal', 'web', 'marketing', 'sales', 'support', 'operations', 'none')
