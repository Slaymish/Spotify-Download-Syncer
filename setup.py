from setuptools import setup, find_packages

setup(
    name="spotify-syncer",
    version="0.1.0",
    author="Hamish Burke",
    description="Sync Spotify playlist tracks to torrent downloads via a menu-bar app",
    packages=find_packages(include=["spotify_syncer", "spotify_syncer.*"]),
    install_requires=[
        "spotipy",
        "qbittorrent-api",
        "requests",
        "beautifulsoup4",
        "python-dotenv",
        "rumps",
        "pync",
    ],
    scripts=["spotify-torrent-menu.py"],
)
