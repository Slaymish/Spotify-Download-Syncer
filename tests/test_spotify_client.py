import pytest
from spotify_syncer.spotify_client import SpotifyClient
from spotify_syncer.domain import Track

class DummySP:
    def __init__(self):
        self.removed = None
    def playlist_items(self, playlist_id):
        # returns one item dict
        return {'items': [
            {'track': {'id': '1', 'uri': 'uri1', 'name': 'TestTrack', 'artists': [{'name': 'TestArtist'}]}}
        ]}
    def playlist_remove_all_occurrences_of_items(self, playlist_id, uris):
        self.removed = uris

@pytest.fixture(autouse=True)
def init_client(monkeypatch):
    # Skip real authentication
    monkeypatch.setattr(SpotifyClient, '__init__', lambda self: None)
    return

def test_get_tracks(monkeypatch):
    client = SpotifyClient()
    dummy_sp = DummySP()
    client.sp = dummy_sp
    tracks = client.get_tracks()
    assert isinstance(tracks, list)
    assert len(tracks) == 1
    t = tracks[0]
    assert isinstance(t, Track)
    assert t.id == '1'
    assert t.uri == 'uri1'
    assert t.name == 'TestTrack'
    assert t.artist == 'TestArtist'

def test_remove_tracks(monkeypatch):
    client = SpotifyClient()
    dummy_sp = DummySP()
    client.sp = dummy_sp
    client.remove_tracks(['uri1', 'uri2'])
    assert dummy_sp.removed == ['uri1', 'uri2']
