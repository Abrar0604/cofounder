from dataclasses import dataclass

@dataclass
class FounderIntentState:
    message: str
    context: str

D6_OPTIONS = ('set_goal', 'ask_question', 'provide_feedback', 'approve', 'reject')
