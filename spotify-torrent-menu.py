"""
spotify-torrent-menu.py: Main Rumps app for Spotify-to-Torrent menu bar synchronization.
"""
import threading
import rumps
from spotify_syncer.events import event_bus
from spotify_syncer.container import Container
from spotify_syncer.config import PLAYLIST_ID, DOWNLOAD_DIR, validate_env, DELETE_AFTER_DOWNLOADED
import logging

logging.basicConfig(
    filename='spotifytorrent.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

class SpotifyTorrentApp(rumps.App):
    def __init__(self):
        """Initialize the menu bar UI and services via DI container."""
        super().__init__("🎶", quit_button=None)
        self.title = "🎧 idle"
        self.menu = ["Sync Now", "Open Logs", "Clear State", None, "Quit"]
        container = Container()
        self.sp = container.spotify_client
        self.qb = container.qb_client
        self.state = container.state
        self.searcher = container.searcher

    @rumps.clicked("Open Logs")
    def open_logs(self, sender):
        import subprocess, os
        log_path = os.path.expanduser('~/spotifytorrent.log')
        subprocess.Popen(["open", log_path])

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

    @rumps.clicked("Clear State")
    def clear_state(self, sender) -> None:
        """Handler to clear all downloaded state records."""
        self.state.clear()
        logging.info("Downloaded state cleared via menu")
        rumps.notification("SpotifyTorrent", None, "Cleared downloaded state database.")

    def sync_all(self):
        """Spawn a background thread to perform sync."""
        threading.Thread(target=self._sync, daemon=True).start()

    def _sync(self):
        """Core synchronization logic: fetch tracks, download and remove with error handling."""
        logging.info("Sync started")
        try:
            self.title = "🔄 syncing..."
            tracks = self.sp.get_tracks()
            for track in tracks:
                if track.id not in self.state.downloaded:
                    self._process_one(track)
                else:
                    logging.info(f"Skipping already downloaded track: {track.name} by {track.artist}")
            self.title = "🎧 idle"
            logging.info("Sync finished")
        except Exception:
            logging.exception("Exception occurred during sync")

    def _process_one(self, track):
        """Process a single track: search, download, notify, and remove."""
        query = f"{track.name} {track.artist}"
        logging.info(f"Searching torrent for: '{query}'")
        magnet = self.searcher.search(query)
        if not magnet:
            logging.warning(f"No torrent for {query}")
            event_bus.publish('torrent_not_found', query, track_name=track.name)
            return
        # attempt to add torrent and only proceed on success
        added = self.qb.add_torrent(magnet, DOWNLOAD_DIR)
        if not added:
            logging.error(f"Failed to add torrent, missing info-hash from URI: {magnet}")
            # do not remove track or mark as downloaded
            event_bus.publish('download_failed', track)
            return
        # on success, optionally remove from playlist and persist state
        if DELETE_AFTER_DOWNLOADED:
            self.sp.remove_tracks([track.uri])
        self.state.add(track.id)
        msg = f"✔️ {track.name} by {track.artist}"
        logging.info(msg)
        event_bus.publish('download_success', track)

if __name__ == "__main__":
    validate_env()
    SpotifyTorrentApp().run()
