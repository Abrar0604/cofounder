from typing import Any, Dict
from langgraph.types import Command
from langgraph.graph.state import CompiledStateGraph
import logging

logger = logging.getLogger(__name__)

class ApprovalService:
    def __init__(self, graph: CompiledStateGraph):
        self.graph = graph
        self.checkpointer = graph.checkpointer
        
    async def get_pending_approvals(self, thread_id: str) -> Dict[str, Any]:
        if not self.checkpointer:
            return {"thread_id": thread_id, "status": "no_checkpointer"}
            
        config = {"configurable": {"thread_id": thread_id}}
        state = await self.graph.aget_state(config)
        
        if state and state.next:
            return {"thread_id": thread_id, "status": "pending_approval", "pending_nodes": state.next}
        return {"thread_id": thread_id, "status": "not_found"}

    async def approve(self, thread_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.checkpointer:
            return {"status": "error", "message": "persistence unavailable"}
            
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Resume graph with approval data
            await self.graph.ainvoke(Command(resume={"action": "approve", "data": data}), config=config)
            return {"status": "approved", "thread_id": thread_id, "data": data}
        except Exception as e:
            logger.error(f"Failed to resume graph: {e}")
            return {"status": "error", "message": "resumption failed"}

    async def reject(self, thread_id: str, reason: str) -> Dict[str, Any]:
        if not self.checkpointer:
            return {"status": "error", "message": "persistence unavailable"}
            
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Resume graph with rejection reason
            await self.graph.ainvoke(Command(resume={"action": "reject", "reason": reason}), config=config)
            return {"status": "rejected", "thread_id": thread_id, "reason": reason}
        except Exception as e:
            logger.error(f"Failed to resume graph: {e}")
            return {"status": "error", "message": "resumption failed"}
