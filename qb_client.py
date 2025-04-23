import logging
import qbittorrentapi
from config import QB_HOST, QB_PORT, QB_USER, QB_PASS

class QbClient:
    def __init__(self):
        # Initialize and authenticate with qBittorrent Web UI
        self.client = qbittorrentapi.Client(
            host=f"{QB_HOST}:{QB_PORT}",
            username=QB_USER,
            password=QB_PASS
        )
        try:
            self.client.auth_log_in()
            logging.info("Logged in to qBittorrent Web UI")
        except Exception as e:
            logging.error(f"Failed to authenticate to qBittorrent: {e}")
            raise

    def add_torrent(self, magnet_uri: str, save_path: str):
        try:
            self.client.torrents_add(urls=magnet_uri, save_path=save_path)
            logging.info(f"Added torrent: {magnet_uri}")
        except Exception as e:
            logging.error(f"Error adding torrent {magnet_uri}: {e}")