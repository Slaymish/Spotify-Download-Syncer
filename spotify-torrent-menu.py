"""
spotify-torrent-menu.py: Main Rumps app for Spotify-to-Torrent menu bar synchronization.
"""
import threading
import rumps
from events import event_bus

from config import REDIRECT_URI, PLAYLIST_ID, DOWNLOAD_DIR, TORRENT_SEARCHER as SEARCHER_NAME
from spotify_client import SpotifyClient
from qb_client import QbClient
from torrent_searchers import create_searcher
from state import State
import logging

logging.basicConfig(
    filename='spotifytorrent.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

class SpotifyTorrentApp(rumps.App):
    def __init__(self):
        """Initialize the menu bar UI and services."""
        super().__init__("🎶", quit_button=None)
        self.title = "🎧 idle"
        self.menu = ["Sync Now", None, "Quit"]
        self.sp = SpotifyClient()
        self.qb = QbClient()
        self.state = State()
        # instantiate torrent searcher based on config
        self.searcher = create_searcher(SEARCHER_NAME)

    @rumps.timer(300)
    def auto_sync(self, sender) -> None:
        """Triggered every 5 minutes to perform auto-sync."""
        self.sync_all()

    @rumps.clicked("Sync Now")
    def manual_sync(self, sender) -> None:
        """Handler for manual sync menu item."""
        self.sync_all()
        event_bus.publish('manual_sync')

    @rumps.clicked("Quit")
    def quit_app(self, sender) -> None:
        """Handler for Quit menu item."""
        rumps.quit_application()

    def sync_all(self):
        """Spawn a background thread to perform sync."""
        threading.Thread(target=self._sync, daemon=True).start()

    def _sync(self):
        """Core synchronization logic: fetch tracks, download and remove."""
        self.title = "🔄 syncing..."
        tracks = self.sp.get_tracks()
        for track in tracks:
            if track.id not in self.state.downloaded:
                self._process_one(track)
        self.title = "🎧 idle"

    def _process_one(self, track):
        """Process a single track: search, download, notify, and remove."""
        query = f"{track.name} {track.artist}"
        logging.info(f"Searching torrent for: '{query}'")
        magnet = self.searcher.search(query)
        if not magnet:
            logging.warning(f"No torrent for {query}")
            event_bus.publish('torrent_not_found', query, track_name=track.name)
            return
        self.qb.add_torrent(magnet, DOWNLOAD_DIR)
        self.sp.remove_tracks([track.uri])
        self.state.add(track.id)
        msg = f"✔️ {track.name} by {track.artist}"
        logging.info(msg)
        event_bus.publish('download_success', track)

if __name__ == "__main__":
    SpotifyTorrentApp().run()
