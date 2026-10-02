import pytest
from packages.brain.services.brain_service import BrainService
from packages.core.events import DomainEvent

def test_create_venture():
    service = BrainService()
    result = service.create_venture("v1", {"name": "Test Venture"})
    
    assert result == {"name": "Test Venture"}
    assert "v1" in service.ventures
    
    events = service.get_events()
    assert len(events) == 1
    assert isinstance(events[0], DomainEvent)
    assert events[0].event_type == "venture.created"
    assert events[0].payload == {"venture_id": "v1", "data": {"name": "Test Venture"}}

def test_update_venture():
    service = BrainService()
    service.create_venture("v1", {"name": "Test Venture"})
    
    result = service.update_venture("v1", {"status": "active"})
    assert result == {"name": "Test Venture", "status": "active"}
    
    events = service.get_events()
    assert len(events) == 2
    assert events[1].event_type == "venture.updated"
    assert events[1].payload["data"] == {"status": "active"}

def test_add_constraint():
    service = BrainService()
    result = service.add_constraint("c1", {"type": "budget"})
    
    assert result == {"type": "budget"}
    assert "c1" in service.constraints
    
    events = service.get_events()
    assert len(events) == 1
    assert events[0].event_type == "constraint.added"
