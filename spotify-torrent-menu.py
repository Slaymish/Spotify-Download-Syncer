#!/usr/bin/env python3
import threading, logging
import rumps
from pync import Notifier

from config import REDIRECT_URI, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIFY_SCOPE, PLAYLIST_ID, DOWNLOAD_DIR
from spotify_client import SpotifyClient
from qb_client import QbClient
from torrent_searchers import default_searcher as TorrentSearcher
from state import State

logging.basicConfig(
    filename='spotifytorrent.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

class SpotifyTorrentApp(rumps.App):
    def __init__(self):
        super().__init__("🎶", quit_button=None)
        self.title = "🎧 idle"
        self.menu = ["Sync Now", None, "Quit"]
        self.sp = SpotifyClient()
        self.qb = QbClient()
        self.state = State()
        self.searcher = TorrentSearcher

    @rumps.timer(300)
    def auto_sync(self, _):
        self.sync_all()

    @rumps.clicked("Sync Now")
    def manual_sync(self, _):
        self.sync_all()
        rumps.notification("SpotifyTorrent", None, "Manual sync started")

    @rumps.clicked("Quit")
    def quit_app(self, _):
        rumps.quit_application()

    def sync_all(self):
        threading.Thread(target=self._sync).start()

    def _sync(self):
        self.title = "🔄 syncing..."
        tracks = self.sp.get_tracks()
        for t in tracks:
            if t['id'] not in self.state.downloaded:
                self._process_one(t)
        self.title = "🎧 idle"

    def _process_one(self, track):
        query = f"{track['name']} {track['artist']}"
        logging.info(f"Searching torrent for: '{query}'")
        magnet = self.searcher.search(query)
        if not magnet:
            logging.warning(f"No torrent for {query}")
            Notifier.notify(f"❌ {track['name']} not found", title="SpotifyTorrent")
            return
        self.qb.add_torrent(magnet, DOWNLOAD_DIR)
        self.sp.remove_tracks([track['uri']])
        self.state.add(track['id'])
        msg = f"✔️ {track['name']} by {track['artist']}"
        logging.info(msg)
        Notifier.notify(msg, title="SpotifyTorrent")

if __name__ == "__main__":
    logging.basicConfig(
        filename='spotifytorrent.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )
    SpotifyTorrentApp().run()
