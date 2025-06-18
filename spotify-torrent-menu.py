"""
spotify-torrent-menu.py: Main Rumps app for Spotify-to-Torrent menu bar synchronization.
"""
#!/usr/bin/env python3
"""
spotify-torrent-menu.py: Cross-platform tray app for Spotify-to-Torrent synchronization.
"""
import sys
import os
import threading
import time
import subprocess
import logging

from spotify_syncer.events import event_bus
from spotify_syncer.container import Container
from spotify_syncer.config import DOWNLOAD_DIR, validate_env, DELETE_AFTER_DOWNLOADED

# Logging setup: write to ~/spotifytorrent.log with rotation handled elsewhere
LOG_PATH = os.path.expanduser('~/spotifytorrent.log')
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

if sys.platform == 'darwin':
    import rumps

    class SpotifyTorrentApp(rumps.App):
        def __init__(self):
            super().__init__("🎶", quit_button=None)
            self.title = "🎧 idle"
            self.menu = ["Sync Now", "Settings", "Check for Updates", "Open Logs", "Clear State", None, "Quit"]
            container = Container()
            self.sp = container.spotify_client
            self.state = container.state
            self.searcher = container.searcher

        @rumps.clicked("Sync Now")
        def manual_sync(self, _):
            self.sync_all()
            event_bus.publish('manual_sync')

        @rumps.clicked("Settings")
        def open_settings(self, _):
            script = os.path.join(os.path.dirname(__file__), "spotify_env_gui.py")
            if not os.path.exists(script):
                rumps.alert("Settings script not found.")
                return

            try:
                subprocess.Popen([sys.executable, script])
            except Exception as e:
                rumps.alert(f"Failed to open settings: {e}")

        @rumps.clicked("Check for Updates")
        def check_updates(self, _):
            script = os.path.join(os.path.dirname(__file__), "update.sh")
            if not os.path.exists(script):
                rumps.alert("Update script not found.")
                return
            try:
                rumps.notification("SpotifyTorrent", None, "Checking for updates...")
                subprocess.check_call([script])
                rumps.notification("SpotifyTorrent", None, "Update complete, restarting...")
                os.execv(sys.executable, [sys.executable, os.path.abspath(__file__)])
            except Exception as e:
                rumps.alert(f"Update failed: {e}")

        @rumps.clicked("Open Logs")
        def open_logs(self, _):
            subprocess.Popen(["open", LOG_PATH])

        @rumps.clicked("Clear State")
        def clear_state(self, _):
            self.state.clear()
            logging.info("Downloaded state cleared via menu")
            rumps.notification("SpotifyTorrent", None, "Cleared downloaded state database.")

        @rumps.clicked("Quit")
        def quit_app(self, _):
            rumps.quit_application()

        @rumps.timer(300)
        def auto_sync(self, _):
            self.sync_all()

        def sync_all(self):
            threading.Thread(target=self._sync, daemon=True).start()

        def _sync(self):
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
        """Process a single track: search via Soulseek, notify, and remove."""
        query = f"{track.name} {track.artist}"
        logging.info(f"Searching Soulseek for: '{query}'")
        result = self.searcher.search(query)
        if not result:
            logging.warning(f"No download for {query}")
            event_bus.publish('torrent_not_found', query, track_name=track.name)
            return
        if DELETE_AFTER_DOWNLOADED:
            self.sp.remove_tracks([track.uri])
        self.state.add(track.id)
        msg = f"✔️ {track.name} by {track.artist}"
        logging.info(msg)
        event_bus.publish('download_success', track)

    def main():
        validate_env()
        SpotifyTorrentApp().run()

elif sys.platform.startswith('linux'):
    import pystray
    from pystray import MenuItem as Item, Menu
    from PIL import Image, ImageDraw, ImageFont

    class SpotifyTorrentApp:
        def __init__(self):
            validate_env()
            container = Container()
            self.sp = container.spotify_client
            self.state = container.state
            self.searcher = container.searcher
            self.icon = pystray.Icon(
                "SpotifyTorrent",
                self._create_image(),
                "SpotifyTorrent",
                menu=Menu(
                    Item("Sync Now", self.manual_sync),
                    Item("Settings", self.open_settings),
                    Item("Check for Updates", self.check_updates),
                    Item("Open Logs", self.open_logs),
                    Item("Clear State", self.clear_state),
                    Item("Quit", self.quit_app),
                ),
            )

        def _create_image(self):
            # Create a 64x64 icon with the 🎶 emoji
            size = 64
            image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()
            text = "🎶"
            w, h = draw.textsize(text, font=font)
            draw.text(((size - w) / 2, (size - h) / 2), text, fill="white", font=font)
            return image

        def run(self):
            # Start periodic sync
            threading.Thread(target=self._auto_sync_loop, daemon=True).start()
            self.icon.run()

        def _auto_sync_loop(self):
            while True:
                time.sleep(300)
                self.manual_sync()

        def manual_sync(self, icon=None, item=None):
            threading.Thread(target=self._sync, daemon=True).start()
            event_bus.publish('manual_sync')

        def _sync(self):
            logging.info("Sync started")
            try:
                self.icon.title = "🔄 syncing..."
                tracks = self.sp.get_tracks()
                for track in tracks:
                    if track.id not in self.state.downloaded:
                        self._process_one(track)
                    else:
                        logging.info(f"Skipping already downloaded track: {track.name} by {track.artist}")
                self.icon.title = "idle"
                logging.info("Sync finished")
            except Exception:
                logging.exception("Exception occurred during sync")

        def _process_one(self, track):
            query = f"{track.name} {track.artist}"
            logging.info(f"Searching Soulseek for: '{query}'")
            result = self.searcher.search(query)
            if not result:
                logging.warning(f"No download for {query}")
                event_bus.publish('torrent_not_found', query, track_name=track.name)
                return
            if DELETE_AFTER_DOWNLOADED:
                self.sp.remove_tracks([track.uri])
            self.state.add(track.id)
            msg = f"✔️ {track.name} by {track.artist}"
            logging.info(msg)
            event_bus.publish('download_success', track)

        def clear_state(self, icon=None, item=None):
            self.state.clear()
            logging.info("Downloaded state cleared via menu")
            try:
                subprocess.call(["notify-send", "SpotifyTorrent", "Cleared downloaded state database."])
            except Exception:
                pass

        def open_logs(self, icon=None, item=None):
            opener = "xdg-open"
            subprocess.Popen([opener, LOG_PATH])

        def open_settings(self, icon=None, item=None):
            script = os.path.join(os.path.dirname(__file__), "spotify_env_gui.py")
            if not os.path.exists(script):
                print("Settings script not found.")
                return
            try:
                subprocess.Popen([sys.executable, script])
            except Exception as e:
                print(f"Failed to open settings: {e}")

        def check_updates(self, icon=None, item=None):
            script = os.path.join(os.path.dirname(__file__), "update.sh")
            if not os.path.exists(script):
                subprocess.call(["notify-send", "SpotifyTorrent", "Update script not found."])
                return
            try:
                subprocess.call(["notify-send", "SpotifyTorrent", "Checking for updates..."])
                subprocess.check_call([script])
                subprocess.call(["notify-send", "SpotifyTorrent", "Update complete, restarting..."])
                os.execv(sys.executable, [sys.executable, os.path.abspath(__file__)])
            except Exception as e:
                subprocess.call(["notify-send", "SpotifyTorrent", f"Update failed: {e}"])

        def quit_app(self, icon=None, item=None):
            self.icon.stop()

    def main():
        SpotifyTorrentApp().run()

else:
    print(f"Unsupported platform: {sys.platform}")
    sys.exit(1)

if __name__ == '__main__':
    main()
