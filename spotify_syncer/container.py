"""
container.py: Dependency Injection container for core services.
"""
from spotify_syncer.spotify_client import SpotifyClient
from spotify_syncer.qb_client import QbClient
from spotify_syncer.state import State
from spotify_syncer.torrent_searchers import create_searcher
from spotify_syncer.config import TORRENT_SEARCHER

class Container:
    """Holds singleton instances of application services."""
    def __init__(self) -> None:
        self.spotify_client = SpotifyClient()
        self.qb_client = QbClient()
        self.state = State()
        self.searcher = create_searcher(TORRENT_SEARCHER)
