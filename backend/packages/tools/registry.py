from typing import Any, Callable, Dict
from pydantic import BaseModel, ValidationError

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: Dict[str, type[BaseModel]] = {}
        self.pending_approvals: Dict[str, str] = {} # approval_id -> tool_name

    def register_tool(self, name: str, schema: type[BaseModel], func: Callable) -> None:
        self.tools[name] = func
        self.schemas[name] = schema

    def execute_tool(self, name: str, kwargs: Dict[str, Any], approval_id: str | None = None) -> Any:
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")

        if approval_id is not None:
            # Validate against pending approvals
            if self.pending_approvals.get(approval_id) != name:
                raise ValueError(f"Invalid or mismatched approval_id for tool {name}")
            # Clear it after successful validation
            del self.pending_approvals[approval_id]

        schema = self.schemas[name]
        try:
            validated_input = schema(**kwargs)
        except ValidationError as e:
            raise ValueError(f"Invalid input for tool {name}: {e}")

        # The tool itself might raise ApprovalRequired, at which point the caller 
        # (call_tool_node) handles it. If the tool needs to register a pending approval,
        # it should ideally populate self.pending_approvals in the registry.
        return self.tools[name](**validated_input.model_dump())
