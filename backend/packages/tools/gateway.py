from typing import Any, Dict
from packages.tools.registry import ToolRegistry

class ToolGateway:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def call_tool(self, name: str, params: Dict[str, Any]) -> Any:
        try:
            result = self.registry.execute_tool(name, params)
            return {"status": "success", "data": result}
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
