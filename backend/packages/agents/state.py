from typing import Annotated, Dict, Any, List, TypedDict
import operator

class AgentState(TypedDict):
    task: str
    messages: Annotated[List[Any], operator.add]
    context: Dict[str, Any]
    current_agent: str
    status: str
    error: str | None
