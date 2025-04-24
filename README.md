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

1. Clone this repo:
   ```bash
   git clone https://github.com/yourname/Spotify-Download-Syncer.git
   cd Spotify-Download-Syncer
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
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
config.py             # Loads env, config normalization, logging setup
domain.py             # Domain models (Track)
events.py             # Simple in-memory EventBus
notifications.py      # Event handlers for macOS notifications
spotify_client.py     # Spotify Web API facade
qb_client.py          # qBittorrent Web UI facade
torrent_searchers.py  # TorrentSearcher interface + PirateBay impl + factory
state.py              # SQLite persistence of downloaded track IDs
spotify-torrent-menu.py  # Main Rumps menu-bar app wiring everything
README.md             # Project documentation
requirements.txt      # Python dependencies
```

---

## 🏛️ Architecture Overview

1. **Dependency Injection & Factory**  
   - `TORRENT_SEARCHER` env var picks desired searcher via `create_searcher()`  
2. **Template Method Pattern**  
   - `AbstractTorrentSearcher` defines the search workflow; providers implement `build_url` & `parse_primary`  
3. **Observer Pattern**  
   - Components communicate via `EventBus` (`download_success`, `torrent_not_found`, `manual_sync`)  
4. **Facade Pattern**  
   - `SpotifyClient` & `QbClient` abstract external APIs behind clean interfaces  
5. **Domain Models**  
   - `Track` dataclass ensures type safety and clarity  
6. **State Repository**  
   - `state.py` uses SQLite for durable, efficient storage  
7. **Logging & Monitoring**  
   - Rotating logs with clear prefixes per module  

---

## ▶️ Running

```bash
python spotify-torrent-menu.py
```

The app will launch a menu-bar icon. Use **Sync Now** or wait for auto-sync. Notifications appear for each download or error.

---

## 🧪 Testing & Extensibility

- To add another torrent site: create a new `TorrentSearcher` in `torrent_searchers.py`, register it in `_searcher_registry`, and set `TORRENT_SEARCHER` accordingly.
- Core logic is thread‑safe, event‑driven, and easy to unit‑test by mocking facades and events.

---

## 📄 License

[MIT](LICENSE)
