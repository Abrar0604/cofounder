from typing import Literal
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel

class PolicyViolation(Exception):
    pass

class ModelRouter:
    def __init__(self, settings):
        self.settings = settings
        # Defaults if not provided in settings
        self.strong_model = getattr(settings, 'strong_model', 'claude-3-5-sonnet-20240620')
        self.cheap_model = getattr(settings, 'cheap_model', 'claude-3-haiku-20240307')
        
    def get_model(self, tier: Literal['strong', 'cheap'], temperature: float = 0.0) -> BaseChatModel:
        if tier == 'strong':
            model_name = self.strong_model
        elif tier == 'cheap':
            model_name = self.cheap_model
        else:
            raise PolicyViolation(f"Unknown model tier: {tier}")
            
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens=4096,
            timeout=60.0,
            max_retries=2
        )
