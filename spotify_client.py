"""
spotify_client.py: Wrapper around Spotify Web API for playlist operations.
"""

import logging
from typing import List
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, REDIRECT_URI, SPOTIFY_SCOPE, PLAYLIST_ID
from domain import Track

class SpotifyClient:
    def __init__(self) -> None:
        try:
            auth_manager = SpotifyOAuth(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=SPOTIFY_SCOPE
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
        except SpotifyException as e:
            logging.error(f"Spotify auth error: {e}")
            raise

    def get_tracks(self) -> List[Track]:
        """Fetch current playlist items and return a list of Track objects."""
        try:
            res = self.sp.playlist_items(PLAYLIST_ID)
        except SpotifyException as e:
            logging.error(f"Spotify API error fetching tracks: {e}")
            return []
        items: List[Track] = []
        for entry in res.get('items', []):
            t = entry.get('track', {}) or {}
            items.append(Track(
                id=t.get('id', ''),
                uri=t.get('uri', ''),
                name=t.get('name', ''),
                artist=(t.get('artists', [{}])[0].get('name') if t.get('artists') else '')
            ))
        logging.info(f"Found {len(items)} tracks in playlist")
        return items

    def remove_tracks(self, uris: List[str]) -> None:
        """Remove tracks (by URI) from the configured playlist."""
        try:
            self.sp.playlist_remove_all_occurrences_of_items(PLAYLIST_ID, uris)
            logging.info(f"Removed {len(uris)} tracks from playlist")
        except SpotifyException as e:
            logging.error(f"Spotify API error removing tracks: {e}")
