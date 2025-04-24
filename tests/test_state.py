import pytest
import os
from spotify_syncer.state import State

def test_state_persistence(tmp_path):
    db_file = tmp_path / "test.db"
    state = State(str(db_file))
    # initial state is empty
    assert state.downloaded == set()
    # add a track id
    state.add('abc123')
    assert 'abc123' in state.downloaded
    # new instance loads existing data
    state2 = State(str(db_file))
    assert 'abc123' in state2.downloaded

def test_clear(tmp_path):
    db_file = tmp_path / "test_clear.db"
    state = State(str(db_file))
    state.add('abc123')
    state.add('def456')
    assert 'abc123' in state.downloaded
    assert 'def456' in state.downloaded
    state.clear()
    assert state.downloaded == set()
    # New instance should also see empty
    state2 = State(str(db_file))
    assert state2.downloaded == set()

def test_thread_safety(tmp_path):
    import threading
    db_file = tmp_path / "test_thread.db"
    state = State(str(db_file))
    def add_many():
        for i in range(100):
            state.add(f"id{i}")
    threads = [threading.Thread(target=add_many) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # Should have 100 unique IDs
    assert len(state.downloaded) == 100
