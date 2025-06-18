import os, sys, logging
from urllib.parse import urlparse, urlunparse
try:
    from dotenv import load_dotenv, find_dotenv
except ImportError:
    load_dotenv = lambda *args, **kwargs: None
    find_dotenv = lambda *args, **kwargs: ''
    logging.getLogger(__name__).warning(
        "python-dotenv not installed; .env files will not be loaded."
    )
# Lazy import Notifier for notifications

# --- Logging configuration ---
from logging.handlers import RotatingFileHandler

# log file with rotation
LOG_FILE = os.path.expanduser('~/spotifytorrent.log')
handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s:%(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Load .env now that logging is configured
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
    logging.getLogger(__name__).info(f"Loaded environment variables from {dotenv_path}")
else:
    logging.getLogger(__name__).warning("No .env file found; defaults and shell env will be used.")
 # --- end logging configuration ---

# Required environment variables for application configuration
REQUIRED_ENV_VARS = [
    'SPOTIPY_CLIENT_ID',
    'SPOTIPY_CLIENT_SECRET',
    'SPOTIPY_REDIRECT_URI',
    'SPOTIFY_PLAYLIST_ID',
    'DOWNLOAD_DIR',
    'SOULSEEK_ACCOUNT',
    'SOULSEEK_PASSWORD',
]

def validate_env() -> None:
    """Ensure required environment variables are set; exit if any are missing."""
    missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
    if missing:
        msg = "Missing environment variables: " + ", ".join(missing)
        logging.error(msg)
        try:
            from pync import Notifier
            Notifier.notify(msg, title="SpotifyTorrent")
        except ImportError:
            pass
        sys.exit(1)

# Normalize redirect URI: use loopback IP for Spotify
raw_redirect = os.getenv('SPOTIPY_REDIRECT_URI') or ''
parsed = urlparse(raw_redirect)
if parsed.hostname == 'localhost':
    netloc = parsed.netloc.replace('localhost', '127.0.0.1')
    REDIRECT_URI = urlunparse(parsed._replace(scheme='http', netloc=netloc))
    logging.warning(f"Redirect URI hostname 'localhost' replaced with loopback IP: {REDIRECT_URI}")
else:
    REDIRECT_URI = raw_redirect

raw_id = os.getenv('SPOTIFY_PLAYLIST_ID') or ''
if raw_id.startswith('spotify:'):
    PLAYLIST_ID = raw_id.split(':')[-1]
elif raw_id.startswith('http'):
    PLAYLIST_ID = raw_id.rstrip('/').split('/')[-1]
else:
    PLAYLIST_ID = raw_id

# Other config values
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIFY_SCOPE = "playlist-read-private playlist-modify-private playlist-modify-public"
# Other config values
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR') or os.getcwd()
# Delete after downloaded toggle
DELETE_AFTER_DOWNLOADED = os.getenv('DELETE_AFTER_DOWNLOADED', 'true').strip().lower() in ('1', 'true', 'yes')

# Soulseek credentials
SOULSEEK_ACCOUNT = os.getenv('SOULSEEK_ACCOUNT')
SOULSEEK_PASSWORD = os.getenv('SOULSEEK_PASSWORD')
