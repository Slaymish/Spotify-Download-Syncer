import logging
from typing import List, Dict
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, REDIRECT_URI, SPOTIFY_SCOPE, PLAYLIST_ID

class SpotifyClient:
    def __init__(self):
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

    def get_tracks(self) -> List[Dict]:
        try:
            res = self.sp.playlist_items(PLAYLIST_ID)
        except SpotifyException as e:
            logging.error(f"Spotify API error fetching tracks: {e}")
            return []
        items = []
        for entry in res.get('items', []):
            track = entry.get('track', {})
            items.append({
                'id': track.get('id'),
                'uri': track.get('uri'),
                'name': track.get('name'),
                'artist': track.get('artists', [{}])[0].get('name')
            })
        logging.info(f"Found {len(items)} tracks in playlist")
        return items

    def remove_tracks(self, uris: List[str]):
        try:
            self.sp.playlist_remove_all_occurrences_of_items(PLAYLIST_ID, uris)
            logging.info(f"Removed {len(uris)} tracks from playlist")
        except SpotifyException as e:
            logging.error(f"Spotify API error removing tracks: {e}")
