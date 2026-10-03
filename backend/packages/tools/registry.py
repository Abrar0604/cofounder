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
            
            # Temporarily remove from pending to prevent concurrent reuse
            del self.pending_approvals[approval_id]

        schema = self.schemas[name]
        try:
            validated_input = schema(**kwargs)
        except ValidationError as e:
            # Restore approval_id on validation failure so it can be retried
            if approval_id is not None:
                self.pending_approvals[approval_id] = name
            raise ValueError(f"Invalid input for tool {name}: {e}")

        import inspect
        call_kwargs = validated_input.model_dump()
        
        # Define how the tool observes the approval: pass _approved=True if the tool accepts it
        sig = inspect.signature(self.tools[name])
        if approval_id is not None and "_approved" in sig.parameters:
            call_kwargs["_approved"] = True

        try:
            result = self.tools[name](**call_kwargs)
            return result
        except Exception:
            # Restore approval_id on execution failure
            if approval_id is not None:
                self.pending_approvals[approval_id] = name
            raise
