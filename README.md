# SpotifyTorrent Menu Bar

A macOS menu-bar app that automatically downloads new tracks from a Spotify playlist via torrent, removes them from the playlist, and notifies you of success or errors.

---

## 🚀 Features

- **Auto-sync** every 5 minutes
- **Manual “Sync Now”** button in the menu bar
- **macOS notifications** for downloads ✅ and errors ❌
- **Logging** to `~/spotifytorrent.log`
- **Lightweight**—built with [rumps](https://github.com/jaredks/rumps)

---

## 🛠️ Prerequisites

1. **macOS**
2. **Python 3.9+**
3. **qBittorrent** with WebUI enabled (Preferences → Web UI)
4. **Spotify Developer App** (Client ID & Secret)

---

## ⚙️ Configuration

Create a `.env` file next to `spotify_torrent_menu.py` with:

```dotenv
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
SPOTIFY_PLAYLIST_ID=your_playlist_id
QB_HOST=localhost
QB_PORT=8080
QB_USER=your_qbittorrent_username
QB_PASS=your_qbittorrent_password
DOWNLOAD_DIR=/Users/youruser/Music/Downloaded
```
