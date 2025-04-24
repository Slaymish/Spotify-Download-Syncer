from setuptools import setup, find_packages
# Conditional py2app setup for macOS application bundle
import sys

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

if sys.platform == 'darwin':
    try:
        from py2app.build_app import py2app
    except ImportError:
        pass  # py2app not installed; fallback to script install
    else:
        APP = ['spotify-torrent-menu.py']
        # Include all core packages and external dependencies for the macOS bundle
        OPTIONS = {
            'argv_emulation': True,
            'packages': [
                'spotify_syncer',
                'spotipy',
                'qbittorrentapi',
                'requests',
                'bs4',
                'dotenv',
                'rumps',
                'pync',
            ],
            'includes': [
                'spotify_syncer.config',
                'spotify_syncer.spotify_client',
                'spotify_syncer.qb_client',
                'spotify_syncer.torrent_searchers',
            ],
        }
        setup_kwargs.update(
            app=APP,
            options={'py2app': OPTIONS},
            setup_requires=['py2app'],
        )
        # remove scripts when bundling

# Fallback to installing script as script
if 'app' not in setup_kwargs:
    setup_kwargs['scripts'] = ['spotify-torrent-menu.py']

setup(**setup_kwargs)
