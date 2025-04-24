"""notifications.py: Event-driven notification handlers for SpotifyTorrent."""

import logging
from typing import Optional
from events import event_bus
from pync import Notifier
from domain import Track


def handle_download_success(track: Track) -> None:
    """Notify user of a successful download."""
    title = "SpotifyTorrent"
    message = f"✔️ {track.name} by {track.artist}"
    Notifier.notify(message, title=title)


def handle_torrent_not_found(query: str, track_name: Optional[str] = None) -> None:
    """Notify user when no torrent is found for a track."""
    title = "SpotifyTorrent"
    message = f"❌ {track_name or query} not found"
    Notifier.notify(message, title=title)


def handle_manual_sync() -> None:
    """Notify user when a manual sync is triggered."""
    Notifier.notify("Manual sync started", title="SpotifyTorrent")

# Register event handlers
_event_pairs = [
    ('download_success', handle_download_success),
    ('torrent_not_found', handle_torrent_not_found),
    ('manual_sync', handle_manual_sync),
]
for event, handler in _event_pairs:
    event_bus.subscribe(event, handler)
