from setuptools import setup, find_packages

APP_NAME = "SpotifyTorrent"
VERSION = "0.1.0"

install_requires=[
    "spotipy",
    "qbittorrent-api",
    "requests",
    "beautifulsoup4",
    "python-dotenv",
    "rumps",
    "pync",
]

# Base setup kwargs
setup_kwargs = dict(
    name="spotify-syncer",
    version=VERSION,
    author="Hamish Burke",
    description="Sync Spotify playlist tracks to torrent downloads via a menu-bar app",
    packages=find_packages(include=["spotify_syncer", "spotify_syncer.*"]),
    install_requires=install_requires,
)

# Fallback to installing script as script
if 'app' not in setup_kwargs:
    setup_kwargs['scripts'] = ['spotify-torrent-menu.py']

setup(**setup_kwargs)
