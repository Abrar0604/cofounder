import os
from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel

class PolicyViolation(Exception):
    pass

class ModelRouter:
    def __init__(self, settings):
        self.settings = settings
        # Defaults if not provided in settings
        self.strong_model = getattr(settings, 'strong_model', None) or 'gemini-1.5-pro'
        self.cheap_model = getattr(settings, 'cheap_model', None) or 'gemini-1.5-flash'
        
    def get_model(self, tier: Literal['strong', 'cheap'], temperature: float = 0.0) -> BaseChatModel:
        if tier == 'strong':
            model_name = self.strong_model
        elif tier == 'cheap':
            model_name = self.cheap_model
        else:
            raise PolicyViolation(f"Unknown model tier: {tier}")
            
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=getattr(self.settings, 'google_api_key', None) or os.getenv("GOOGLE_API_KEY"),
            temperature=temperature,
            max_tokens=4096,
            timeout=60.0,
            max_retries=2
        )
