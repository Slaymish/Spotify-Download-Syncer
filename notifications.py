from events import event_bus
from pync import Notifier

def handle_download_success(track):
    title = "SpotifyTorrent"
    message = f"✔️ {track['name']} by {track['artist']}"
    Notifier.notify(message, title=title)

def handle_torrent_not_found(query, track_name=None):
    title = "SpotifyTorrent"
    message = f"❌ {track_name or query} not found"
    Notifier.notify(message, title=title)

def handle_manual_sync():
    Notifier.notify("Manual sync started", title="SpotifyTorrent")

# Register handlers
_event_pairs = [
    ('download_success', handle_download_success),
    ('torrent_not_found', handle_torrent_not_found),
    ('manual_sync', handle_manual_sync),
]
for evt, handler in _event_pairs:
    event_bus.subscribe(evt, handler)
