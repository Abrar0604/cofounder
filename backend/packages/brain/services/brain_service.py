from typing import Dict, Any, List
from packages.core.events import DomainEvent

class BrainService:
    def __init__(self):
        self.ventures: Dict[str, Any] = {}
        self.constraints: Dict[str, Any] = {}
        self.events: List[DomainEvent] = []

    def create_venture(self, venture_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        self.ventures[venture_id] = data
        event = DomainEvent(
            event_type="venture.created",
            payload={"venture_id": venture_id, "data": data}
        )
        self.events.append(event)
        return self.ventures[venture_id]

    def update_venture(self, venture_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if venture_id in self.ventures:
            self.ventures[venture_id].update(data)
            event = DomainEvent(
                event_type="venture.updated",
                payload={"venture_id": venture_id, "data": data}
            )
            self.events.append(event)
        return self.ventures.get(venture_id, {})

    def add_constraint(self, constraint_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        self.constraints[constraint_id] = data
        event = DomainEvent(
            event_type="constraint.added",
            payload={"constraint_id": constraint_id, "data": data}
        )
        self.events.append(event)
        return self.constraints[constraint_id]

    def get_events(self) -> List[DomainEvent]:
        return self.events
