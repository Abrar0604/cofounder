import pytest
from pydantic import BaseModel
from packages.tools.registry import ToolRegistry
from packages.tools.gateway import ToolGateway

class DummySchema(BaseModel):
    x: int
    y: int

def dummy_tool(x: int, y: int) -> int:
    return x + y

@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register_tool("add", DummySchema, dummy_tool)
    return reg

@pytest.fixture
def gateway(registry):
    return ToolGateway(registry)

def test_registry_execute_valid(registry):
    result = registry.execute_tool("add", {"x": 2, "y": 3})
    assert result == 5

def test_registry_execute_invalid_schema(registry):
    with pytest.raises(ValueError, match="Invalid input for tool add"):
        registry.execute_tool("add", {"x": 2, "y": "string"})

def test_registry_execute_not_found(registry):
    with pytest.raises(ValueError, match="Tool sub not found"):
        registry.execute_tool("sub", {"x": 2, "y": 1})

def test_gateway_call_valid(gateway):
    result = gateway.call_tool("add", {"x": 5, "y": 5})
    assert result == {"status": "success", "data": 10}

def test_gateway_call_invalid(gateway):
    result = gateway.call_tool("add", {"x": 5})
    assert result["status"] == "error"
    assert "Invalid input for tool add" in result["message"]

def test_gateway_call_not_found(gateway):
    result = gateway.call_tool("sub", {"x": 5, "y": 5})
    assert result["status"] == "error"
    assert "Tool sub not found" in result["message"]
