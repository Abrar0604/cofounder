from dataclasses import dataclass
from typing import Literal

@dataclass
class ContextItemState:
    kind: Literal['human', 'ai', 'tool']
    age_index: int
    length_chars: int
    excerpt: str  # truncated to 600 chars

D10_OPTIONS = ('keep', 'drop', 'other')
