import pytest
import os
import tempfile
from src.dedup_store import DedupStore

@pytest.fixture
def dedup_store():
    """Create a temporary dedup store for testing"""
    # Create temp database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    store = DedupStore(temp_db.name)
    
    yield store
    
    # Cleanup
    os.unlink(temp_db.name)

def test_dedup_store_initialization(dedup_store):
    """Test that dedup store initializes correctly"""
    assert dedup_store is not None
    assert os.path.exists(dedup_store.db_path)

def test_no_duplicate_on_first_insert(dedup_store):
    """Test that first insert is not considered duplicate"""
    is_dup = dedup_store.is_duplicate("test.topic", "evt-001")
    assert is_dup == False

def test_store_event_success(dedup_store):
    """Test storing an event successfully"""
    success = dedup_store.store_event(
        topic="user.signup",
        event_id="evt-001",
        timestamp="2025-10-22T10:00:00Z",
        source="test",
        payload='{"user_id": 123}'
    )
    assert success == True

def test_duplicate_detection(dedup_store):
    """Test that duplicate events are detected"""
    # Store first event
    dedup_store.store_event(
        topic="user.signup",
        event_id="evt-001",
        timestamp="2025-10-22T10:00:00Z",
        source="test",
        payload='{"user_id": 123}'
    )
    
    # Check if duplicate
    is_dup = dedup_store.is_duplicate("user.signup", "evt-001")
    assert is_dup == True

def test_duplicate_insert_fails(dedup_store):
    """Test that inserting duplicate returns False"""
    # First insert
    success1 = dedup_store.store_event(
        topic="user.signup",
        event_id="evt-001",
        timestamp="2025-10-22T10:00:00Z",
        source="test",
        payload='{"user_id": 123}'
    )
    
    # Second insert (duplicate)
    success2 = dedup_store.store_event(
        topic="user.signup",
        event_id="evt-001",
        timestamp="2025-10-22T10:00:00Z",
        source="test",
        payload='{"user_id": 123}'
    )
    
    assert success1 == True
    assert success2 == False

def test_different_topics_not_duplicate(dedup_store):
    """Test that same event_id but different topic is not duplicate"""
    # Store in topic1
    dedup_store.store_event(
        topic="topic1",
        event_id="evt-001",
        timestamp="2025-10-22T10:00:00Z",
        source="test",
        payload='{}'
    )
    
    # Check in topic2 (should not be duplicate)
    is_dup = dedup_store.is_duplicate("topic2", "evt-001")
    assert is_dup == False

def test_get_events_by_topic(dedup_store):
    """Test retrieving events filtered by topic"""
    # Store events in different topics
    dedup_store.store_event("topic1", "evt-001", "2025-10-22T10:00:00Z", "test", '{}')
    dedup_store.store_event("topic2", "evt-002", "2025-10-22T10:00:00Z", "test", '{}')
    
    # Get events from topic1
    events = dedup_store.get_events("topic1")
    assert len(events) == 1
    assert events[0][0] == "topic1"

def test_get_all_topics(dedup_store):
    """Test getting list of unique topics"""
    # Store events in different topics
    dedup_store.store_event("topic1", "evt-001", "2025-10-22T10:00:00Z", "test", '{}')
    dedup_store.store_event("topic2", "evt-002", "2025-10-22T10:00:00Z", "test", '{}')
    dedup_store.store_event("topic1", "evt-003", "2025-10-22T10:00:00Z", "test", '{}')
    
    topics = dedup_store.get_all_topics()
    assert len(topics) == 2
    assert "topic1" in topics
    assert "topic2" in topics