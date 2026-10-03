from dataclasses import dataclass

@dataclass
class ScoreViabilityState:
    market_size: str
    compliance_complexity: str
    competitor_density: str

D7_OPTIONS = ('high', 'medium', 'low', 'unviable')
