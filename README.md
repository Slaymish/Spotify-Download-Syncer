# SpotifyTorrent Menu Bar

A modular, extensible macOS menu-bar app that syncs a Spotify playlist to torrent downloads via any supported torrent provider.

---

## 🚀 Features

- **Auto-sync** every 5 minutes (configurable)
- **Manual “Sync Now”** via menu
- **Event-driven notifications** for download success, errors, and manual sync
- **SQLite-backed state** (`~/.spotifytorrent.db`) for robust persistence
- **Plugin‑style searchers**: switch between torrent search providers via env var
- **Rotating logs** (`~/spotifytorrent.log`) with max file size and backups

---

## 🛠️ Prerequisites

- macOS with Python 3.9+
- [qBittorrent](https://www.qbittorrent.org/) with Web UI enabled
- A Spotify Developer App (Client ID & Secret)

---

## ⚙️ Installation

You can install the app either by cloning and installing locally, or via PyPI (once published).

### From source (editable)

```bash
# clone and enter directory
git clone https://github.com/yourname/Spotify-Download-Syncer.git
cd Spotify-Download-Syncer

# create venv
python3 -m venv venv
source venv/bin/activate

# install with dev dependencies
pip install -e .[dev]
```

This installs the `spotify-torrent-menu` script into your PATH.

### From PyPI (future)

```bash
pip install spotify-syncer
```

---

## ⚙️ Configuration

1. Create a `.env` file next to `spotify-torrent-menu.py`:
   ```dotenv
   SPOTIPY_CLIENT_ID=YOUR_SPOTIFY_CLIENT_ID
   SPOTIPY_CLIENT_SECRET=YOUR_SPOTIFY_CLIENT_SECRET
   SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
   SPOTIFY_PLAYLIST_ID=YOUR_PLAYLIST_ID
   QB_HOST=localhost
   QB_PORT=8080
   QB_USER=YOUR_QBITTORRENT_USER
   QB_PASS=YOUR_QBITTORRENT_PASS
   DOWNLOAD_DIR=/Users/you/Music/Downloads
   TORRENT_SEARCHER=piratebay  # choose searcher, default is piratebay
   ```
2. Register the exact redirect URI (`http://127.0.0.1:8888/callback`) in your Spotify Developer Dashboard under **Edit Settings → Redirect URIs**.

---

## 📂 Project Structure

```
Spotify-Download-Syncer/
├── LICENSE
├── README.md
├── setup.py
├── spotify-torrent-menu.py        # entry-point script
├── spotify_syncer/                # core package
│   ├── __init__.py
│   ├── config.py
│   ├── container.py
│   ├── domain.py
│   ├── events.py
│   ├── notifications.py
│   ├── qb_client.py
│   ├── spotify_client.py
│   ├── state.py
│   └── torrent_searchers.py
├── tests/                         # pytest suite
│   ├── test_event_bus.py
│   ├── test_qb_client.py
│   ├── test_spotify_client.py
│   ├── test_state.py
│   └── test_torrent_searchers.py
└── requirements.txt               # base deps (for non-editable installs)
``` 

---

## 🏷️ Packaging & Distribution

Build source and wheel distributions:

```bash
python setup.py sdist bdist_wheel
``` 

Install locally for testing:

```bash
pip install dist/spotify_syncer-0.1.0-py3-none-any.whl
```

Submit to PyPI once ready.

---

## ▶️ Running

```bash
spotify-torrent-menu
```

The app will launch a menu-bar icon. Use **Sync Now** or wait for auto-sync. Notifications appear for each download or error.

---

## 🧪 Testing & Extensibility

- To add another torrent site: create a new `TorrentSearcher` in `torrent_searchers.py`, register it in `_searcher_registry`, and set `TORRENT_SEARCHER` accordingly.
- Core logic is thread‑safe, event‑driven, and easy to unit‑test by mocking facades and events.

---

## 📄 License

[MIT](LICENSE)
