import pytest
import os
import tempfile
from src.dedup_store import DedupStore

def test_persistence_after_restart():
    """Test that dedup store persists data after restart"""
    # Create temp database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_db.name
    temp_db.close()
    
    # First session: store event
    store1 = DedupStore(temp_db_path)
    store1.store_event(
        topic="persist.test",
        event_id="persist-001",
        timestamp="2025-10-22T10:00:00Z",
        source="test",
        payload='{"data": "test"}'
    )
    
    # Simulate restart by creating new instance
    store2 = DedupStore(temp_db_path)
    
    # Check if event is still marked as processed
    is_dup = store2.is_duplicate("persist.test", "persist-001")
    assert is_dup == True
    
    # Cleanup
    os.unlink(temp_db_path)

def test_persistence_prevents_reprocessing():
    """Test that persisted dedup prevents reprocessing"""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_db.name
    temp_db.close()
    
    # First session
    store1 = DedupStore(temp_db_path)
    success1 = store1.store_event(
        topic="reprocess.test",
        event_id="reprocess-001",
        timestamp="2025-10-22T10:00:00Z",
        source="test",
        payload='{}'
    )
    assert success1 == True
    
    # Second session (after restart)
    store2 = DedupStore(temp_db_path)
    success2 = store2.store_event(
        topic="reprocess.test",
        event_id="reprocess-001",
        timestamp="2025-10-22T10:00:00Z",
        source="test",
        payload='{}'
    )
    assert success2 == False  # Should fail because it's duplicate
    
    # Cleanup
    os.unlink(temp_db_path)

def test_multiple_restarts():
    """Test dedup store survives multiple restarts"""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_db.name
    temp_db.close()
    
    # Store events across multiple sessions
    for i in range(3):
        store = DedupStore(temp_db_path)
        store.store_event(
            topic="multi.restart",
            event_id=f"evt-{i}",
            timestamp="2025-10-22T10:00:00Z",
            source="test",
            payload='{}'
        )
    
    # Final session: verify all events
    final_store = DedupStore(temp_db_path)
    events = final_store.get_events("multi.restart")
    assert len(events) == 3
    
    # Cleanup
    os.unlink(temp_db_path)