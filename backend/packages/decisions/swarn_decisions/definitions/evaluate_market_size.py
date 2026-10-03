from dataclasses import dataclass
from typing import Literal

@dataclass
class EvaluateMarketSizeState:
    market_data_summary: str
    target_demographic: str

D1_OPTIONS = ('large_tam', 'niche', 'too_small', 'unknown')
