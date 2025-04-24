"""
container.py: Dependency Injection container for core services.
"""
from spotify_syncer.spotify_client import SpotifyClient
from spotify_syncer.qb_client import QbClient
from spotify_syncer.state import State
from spotify_syncer.torrent_searchers import create_searcher
from spotify_syncer.config import TORRENT_SEARCHER
import logging

class Container:
    """Holds singleton instances of application services."""
    def __init__(self) -> None:
        self.spotify_client = SpotifyClient()
        self.qb_client = QbClient()
        self.state = State()
        self.searcher = create_searcher(TORRENT_SEARCHER)
        # confirm which searcher key was selected
        logging.getLogger(__name__).info(f"Using torrent searcher: {self.searcher.__class__.__name__} (env: '{TORRENT_SEARCHER}')")
