from typing import Any, Callable, Dict
from pydantic import BaseModel, ValidationError

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: Dict[str, type[BaseModel]] = {}

    def register_tool(self, name: str, schema: type[BaseModel], func: Callable) -> None:
        self.tools[name] = func
        self.schemas[name] = schema

    def execute_tool(self, name: str, kwargs: Dict[str, Any]) -> Any:
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")

        schema = self.schemas[name]
        try:
            validated_input = schema(**kwargs)
        except ValidationError as e:
            raise ValueError(f"Invalid input for tool {name}: {e}")

        return self.tools[name](**validated_input.model_dump())
