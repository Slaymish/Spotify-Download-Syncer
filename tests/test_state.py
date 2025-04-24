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
