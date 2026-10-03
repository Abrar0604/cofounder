import json
from typing import Any, List, Optional
from pydantic import PrivateAttr
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

class FakeChatModel(GenericFakeChatModel):
    _received_messages: List[Any] = PrivateAttr(default_factory=list)

    def __init__(self, responses: Optional[List[Any]] = None):
        super().__init__(messages=iter(responses) if responses else iter([]))
        
    @property
    def received_messages(self):
        return self._received_messages
        
    def _generate(self, messages: List[Any], stop: Optional[List[str]] = None, run_manager: Optional[Any] = None, **kwargs: Any) -> Any:
        self._received_messages.append(messages)
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
        
    def bind_tools(self, tools: Any, **kwargs: Any) -> "FakeChatModel":
        return self
        
    def with_structured_output(self, schema: Any, **kwargs: Any) -> Any:
        def _parse(messages: Any) -> Any:
            self._received_messages.append(messages)
            try:
                msg = next(self.messages)
            except StopIteration:
                raise ValueError("No more scripted responses in FakeChatModel.")
            if isinstance(msg, AIMessage):
                content = msg.content
            else:
                content = msg
            
            # Simple JSON parse for structured output mapping
            data = json.loads(content)
            
            # If the schema is a pydantic model, instantiate it
            if hasattr(schema, "parse_obj"):
                return schema.parse_obj(data)
            elif hasattr(schema, "model_validate"):
                return schema.model_validate(data)
            return data
            
        return RunnableLambda(_parse)
