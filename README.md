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
- [soulseek-cli](https://github.com/aeyoll/soulseek-cli) installed (e.g., `brew install soulseek-cli`) for Soulseek searcher support

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

# install dependencies
pip install -e .
```

This installs the `spotify-torrent-menu` script into your PATH.

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
   TORRENT_SEARCHER=soulseek    # set to 'soulseek' to use SoulseekSearcher (default is piratebay if not set)
   # Soulseek CLI credentials (when using SOULSEEK searcher)
   SOULSEEK_ACCOUNT=YOUR_SOULSEEK_USERNAME
   SOULSEEK_PASSWORD=YOUR_SOULSEEK_PASSWORD
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

## ▶️ Running

Before running, ensure you are using the latest source and not a stale macOS build:
1. Delete any previous build/bundle directories (`rm -rf build/`).
2. Run from the repository root, so `python-dotenv` loads your updated `.env`.
3. Launch via source script, not a packaged app.
```bash
python spotify-torrent-menu.py
```
Or, if a shim is installed in your PATH:
```bash
spotify-torrent-menu
```

The app will launch a menu-bar icon. Use **Sync Now** or wait for auto-sync. Notifications appear for each download or error.

## 🕹️ Launch on Login

To start SpotifyTorrent automatically when you log in on macOS:

1. Ensure the `spotify-torrent-menu` script is installed in your PATH (e.g., via `pip install -e .`).
2. Open **System Settings → General → Login Items**.
3. Under **Open at Login**, click the **+** button and select the `spotify-torrent-menu` executable (usually in `/usr/local/bin/spotify-torrent-menu` or your virtualenv's bin folder).
4. (Optional) Check **Hide** to launch the app hidden on startup.

Alternatively, you can wrap the script in an Automator application:

1.  Open **Automator** and create a new **Application**.
2.  Add a **Run Shell Script** action with the command:
    ```bash
    spotify-torrent-menu
    ```
3.  Save the Automator app (e.g., `SpotifyTorrentLauncher.app`) and add it to **Login Items** instead of the script.

---

## 🧪 Testing & Extensibility

- To add another torrent site: create a new `TorrentSearcher` in `torrent_searchers.py`, register it in `_searcher_registry`, and set `TORRENT_SEARCHER` accordingly.
- Core logic is thread‑safe, event‑driven, and easy to unit‑test by mocking facades and events.

---

## 📄 License

[MIT](LICENSE)
