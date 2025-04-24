"""
container.py: Dependency Injection container for core services.
"""
from spotify_syncer.spotify_client import SpotifyClient
from spotify_syncer.state import State
from spotify_syncer.torrent_searchers import create_searcher
from spotify_syncer.config import TORRENT_SEARCHER
import logging
import sys

class Container:
    """Holds singleton instances of application services."""
    def __init__(self) -> None:
        self.spotify_client = SpotifyClient()
        self.state = State()
        self.searcher = create_searcher(TORRENT_SEARCHER)
        # confirm which searcher key was selected
        logging.getLogger(__name__).info(f"Using torrent searcher: {self.searcher.__class__.__name__} (env: '{TORRENT_SEARCHER}')")
        # Only load qbittorrent if using PirateBay
        if self.searcher.__class__.__name__ == "PirateBayTorrentSearcher":
            from spotify_syncer.qb_client import QbClient
            self.qb_client = QbClient()
        else:
            self.qb_client = None
        # For Soulseek, check login
        if self.searcher.__class__.__name__ == "SoulseekSearcher":
            import subprocess, os
            account = os.getenv("SOULSEEK_ACCOUNT")
            password = os.getenv("SOULSEEK_PASSWORD")
            try:
                result = subprocess.run([
                    "soulseek", "login", "--check" # this doesn't exist
                ], capture_output=True, text=True)
                if result.returncode != 0:
                    logging.getLogger(__name__).error(
                        "Soulseek CLI is not logged in. Please run 'soulseek login' or set SOULSEEK_ACCOUNT and SOULSEEK_PASSWORD in your .env."
                    )
            except Exception as e:
                logging.getLogger(__name__).error(f"Could not check Soulseek login: {e}")
                sys.exit(1)
