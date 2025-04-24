"""
container.py: Dependency Injection container for core services.
"""
from spotify_client import SpotifyClient
from qb_client import QbClient
from state import State
from torrent_searchers import create_searcher
from config import TORRENT_SEARCHER

class Container:
    """Holds singleton instances of application services."""
    def __init__(self) -> None:
        self.spotify_client = SpotifyClient()
        self.qb_client = QbClient()
        self.state = State()
        self.searcher = create_searcher(TORRENT_SEARCHER)
