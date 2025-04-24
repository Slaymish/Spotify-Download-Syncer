"""
qb_client.py: Wrapper for qBittorrent Web API operations.
"""

import logging
try:
    import qbittorrentapi
except ImportError:
    import logging
    logging.getLogger(__name__).warning("qbittorrentapi not found, using dummy implementation")
    # Dummy module with minimal interface for testing
    class _DummyQBModule:
        class LoginFailed(Exception):
            pass
        class Client:
            def __init__(self, *args, **kwargs):
                pass
            def auth_log_in(self):
                pass
            def torrents_add(self, *args, **kwargs):
                pass
    qbittorrentapi = _DummyQBModule

from spotify_syncer.config import QB_HOST, QB_PORT, QB_USER, QB_PASS

class QbClient:
    def __init__(self) -> None:
        """Initialize and authenticate with qBittorrent Web UI."""
        self.client = qbittorrentapi.Client(
            host=f"{QB_HOST}:{QB_PORT}",
            username=QB_USER,
            password=QB_PASS
        )
        try:
            self.client.auth_log_in()
            logging.getLogger(__name__).info("Logged in to qBittorrent Web UI")
        except qbittorrentapi.LoginFailed as e:
            logging.getLogger(__name__).error(f"Authentication failed for qBittorrent: {e}")
            raise

    def add_torrent(self, magnet_uri: str, save_path: str) -> None:
        """Add a torrent via magnet URI and specify the save path."""
        try:
            self.client.torrents_add(urls=magnet_uri, save_path=save_path)
            logging.getLogger(__name__).info(f"Added torrent: {magnet_uri}")
        except Exception as e:
            logging.getLogger(__name__).error(f"Error adding torrent {magnet_uri}: {e}")