from dataclasses import dataclass
from typing import Literal

@dataclass
class RouteModelState:
    step_name: str
    task_summary_redacted: str
    expected_output: Literal['classification','short_text','long_text','structured_analysis','legal_or_financial']

D4_OPTIONS = ('haiku', 'sonnet', 'no_llm_needed', 'other')
