from dataclasses import dataclass

@dataclass
class AssessBurnRateState:
    total_spent: float
    budget: float
    burn_rate_per_week: float

D9_OPTIONS = ('safe', 'warning', 'critical', 'depleted')
