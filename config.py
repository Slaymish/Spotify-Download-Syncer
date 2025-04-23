import os, sys, logging
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse
from pync import Notifier

# Load .env
load_dotenv()

# Required vars
required_vars = ['SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET', 'SPOTIPY_REDIRECT_URI', 'SPOTIFY_PLAYLIST_ID', 'DOWNLOAD_DIR', 'QB_HOST', 'QB_PORT', 'QB_USER', 'QB_PASS']
missing = [v for v in required_vars if not os.getenv(v)]
if missing:
    msg = "Missing environment variables: " + ", ".join(missing)
    logging.error(msg)
    Notifier.notify(msg, title="SpotifyTorrent")
    sys.exit(1)

# Normalize redirect URI: use loopback IP for Spotify
raw_redirect = os.getenv('SPOTIPY_REDIRECT_URI')
parsed = urlparse(raw_redirect)
if parsed.hostname == 'localhost':
    netloc = parsed.netloc.replace('localhost', '127.0.0.1')
    REDIRECT_URI = urlunparse(parsed._replace(scheme='http', netloc=netloc))
    logging.warning(f"Redirect URI hostname 'localhost' replaced with loopback IP: {REDIRECT_URI}")
else:
    REDIRECT_URI = raw_redirect

# Normalize playlist ID
raw_id = os.getenv('SPOTIFY_PLAYLIST_ID')
if raw_id.startswith('spotify:'):
    PLAYLIST_ID = raw_id.split(':')[-1]
elif raw_id.startswith('http'):
    PLAYLIST_ID = raw_id.rstrip('/').split('/')[-1]
else:
    PLAYLIST_ID = raw_id

# Other config values
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIFY_SCOPE = "playlist-read-private playlist-modify-private"
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')
QB_HOST = os.getenv('QB_HOST')
QB_PORT = os.getenv('QB_PORT')
QB_USER = os.getenv('QB_USER')
QB_PASS = os.getenv('QB_PASS')
# Torrent searcher selection (supports 'piratebay', etc.)
TORRENT_SEARCHER = os.getenv('TORRENT_SEARCHER', 'piratebay')
