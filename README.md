# SpotifyTorrent Menu Bar

A macOS menu-bar app that syncs a Spotify playlist to Soulseek or torrent downloads.

## Prerequisites

- macOS with Python 3.9+
- [qBittorrent](https://www.qbittorrent.org/) with Web UI enabled
- Spotify Developer App (Client ID & Secret)
- For Soulseek: `npm install -g soulseek-cli`

## Quick Start

1. **Install the app**:

   ```bash
   git clone https://github.com/Slaymish/Spotify-Download-Syncer.git
   cd Spotify-Download-Syncer
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. **Configure the app**:
   Create a `.env` file in the project root:

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
   TORRENT_SEARCHER=soulseek    # Set to 'piratebay' or 'soulseek'

   DELETE_AFTER_DOWNLOADED=false  # (keeps tracks in playlist after download)

   # Only needed for Soulseek
   SOULSEEK_ACCOUNT=YOUR_SOULSEEK_USERNAME
   SOULSEEK_PASSWORD=YOUR_SOULSEEK_PASSWORD
   ```

3. **Register Spotify redirect URI**:
   Add `http://127.0.0.1:8888/callback` to your Spotify Developer Dashboard under **Edit Settings → Redirect URIs**

4. **Run the app**:

   ```bash
   python spotify-torrent-menu.py
   ```

   The app will appear as a menu bar icon. Use **Sync Now** to manually start a sync or wait for the automatic 5-minute sync.

## Auto-start at Login

To start SpotifyTorrent when you log in:

1. Open **System Settings → General → Login Items**
2. Click **+** and select the `spotify-torrent-menu` script or create an Automator app that runs the script

## Logs & Troubleshooting

- Check `~/spotifytorrent.log` for detailed logs
- Downloaded track state is stored in `~/.spotifytorrent.db`
- To clear downloaded history: click **Clear State** in the menu

## License

[MIT](LICENSE)
