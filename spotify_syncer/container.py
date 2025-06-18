"""
container.py: Dependency Injection container for core services.
"""
import logging
import os
import subprocess
import sys

from spotify_syncer.spotify_client import SpotifyClient
from spotify_syncer.state import State
from spotify_syncer.torrent_searchers import SoulseekSearcher
from spotify_syncer.config import SOULSEEK_ACCOUNT, SOULSEEK_PASSWORD

class Container:
    """Holds singleton instances of application services."""
    def __init__(self) -> None:
        self.spotify_client = SpotifyClient()
        self.state = State()
        self.searcher = SoulseekSearcher()
        logging.getLogger(__name__).info("Using SoulseekSearcher for torrent downloads")

        # Attempt Soulseek CLI login
        if not SOULSEEK_ACCOUNT or not SOULSEEK_PASSWORD:
            logging.getLogger(__name__).error(
                "Soulseek account/password not set. Please set SOULSEEK_ACCOUNT and SOULSEEK_PASSWORD in your .env."
            )
        else:
            try:
                result = subprocess.run(
                    ["soulseek", "login", SOULSEEK_ACCOUNT, SOULSEEK_PASSWORD],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    msg = (result.stderr or result.stdout or "").strip()
                    logging.getLogger(__name__).error(f"Soulseek login failed: {msg}")
                else:
                    logging.getLogger(__name__).info("Successfully logged in to Soulseek CLI.")
            except Exception as e:
                logging.getLogger(__name__).error(f"Could not login to Soulseek: {e}")
                sys.exit(1)
