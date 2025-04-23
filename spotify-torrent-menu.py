#!/usr/bin/env python3
import os, time, json, threading, logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import qbittorrentapi
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from dotenv import load_dotenv
import rumps
from pync import Notifier

# ——— Setup ———
load_dotenv()
logging.basicConfig(
    filename=os.path.expanduser('~/spotifytorrent.log'),
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Spotify auth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
    scope="playlist-read-private playlist-modify-private"
))
PLAYLIST_ID = os.getenv('SPOTIFY_PLAYLIST_ID')
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')

# qBittorrent
qb = qbittorrentapi.Client(
    host=f"{os.getenv('QB_HOST')}:{os.getenv('QB_PORT')}",
    username=os.getenv('QB_USER'),
    password=os.getenv('QB_PASS')
)
qb.auth_log_in()

# track processed
DL_JSON = os.path.expanduser('~/.spotify_downloaded.json')
downloaded = set(json.load(open(DL_JSON))) if os.path.exists(DL_JSON) else set()

def save_downloaded():
    with open(DL_JSON, 'w') as f:
        json.dump(list(downloaded), f)

def get_tracks():
    res = sp.playlist_items(PLAYLIST_ID)
    return [{
        'id': i['track']['id'],
        'uri': i['track']['uri'],
        'name': i['track']['name'],
        'artist': i['track']['artists'][0]['name']
    } for i in res['items']]

def search_torrent(query):
    url = f"https://thepiratebay.org/search/{quote_plus(query)}/1/99/0"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    link = soup.select_one('#searchResult tr .detName a')
    if not link: return None
    mag = link.find_previous('a', href=True, title="Download this torrent using magnet")
    return mag['href'] if mag else None

def process_one(track):
    q = f"{track['name']} {track['artist']}"
    magnet = search_torrent(q)
    if not magnet:
        logging.warning(f"No torrent for {q}")
        Notifier.notify(f"❌ {track['name']} not found", title="SpotifyTorrent")
        return
    qb.torrents_add(urls=magnet, save_path=DOWNLOAD_DIR)
    sp.playlist_remove_all_occurrences_of_items(PLAYLIST_ID, [track['uri']])
    downloaded.add(track['id']); save_downloaded()
    msg = f"✔️ {track['name']} by {track['artist']}"
    logging.info(msg); Notifier.notify(msg, title="SpotifyTorrent")

def sync_all(_=None):
    threading.Thread(target=_sync).start()

def _sync():
    app.title = "🔄 syncing..."
    for t in get_tracks():
        if t['id'] not in downloaded:
            process_one(t)
    app.title = "🎧 idle"

# ——— rumps App ———
app = rumps.App("🎶")
app.title = "🎧 idle"
app.menu = ["Sync Now", None, "Quit"]

@app.timer(300)  # every 5m
def auto_sync(_): sync_all()

@rumps.clicked("Sync Now")
def manual_sync(_: rumps.MenuItem):
    sync_all()
    rumps.notification("SpotifyTorrent", None, "Manual sync started")

@rumps.clicked("Quit")
def quit_app(_: rumps.MenuItem):
    rumps.quit_application()

if __name__ == "__main__":
    app.run()
