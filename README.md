[![CI](https://github.com/hamishmb/spotify-torrent/actions/workflows/ci.yml/badge.svg)](https://github.com/hamishmb/spotify-torrent/actions/workflows/ci.yml)

# SpotifyTorrent Tray App

A cross-platform (macOS/Linux) tray application that syncs a Spotify playlist to Soulseek downloads.

## Prerequisites

- macOS or Linux with Python 3.9+
- On Linux, you may need system tray and notify dependencies:
- On Arch Linux, you may need to install the following dependencies:
    ```bash
    sudo pacman -S python-gobject libappindicator-gtk3 libnotify
    ```
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
   DOWNLOAD_DIR=/Users/you/Music/Downloads
   # Soulseek mode (default): no TORRENT_SEARCHER needed

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
   Use **Settings** to open a GUI for editing your `.env` configuration options. After saving, restart the app for changes to take effect.

## Updating

To pull the latest changes and reinstall dependencies, run:

```bash
./update.sh
```
You will need to restart the app for updates to take effect.

Alternatively, use the **Check for Updates** option in the app menu to pull the latest version, reinstall dependencies, and automatically restart the application.

## Auto-start at Login

To start SpotifyTorrent when you log in:

1. Open **System Settings → General → Login Items**
2. Click **+** and select the `spotify-torrent-menu` script or create an Automator app that runs the script

## Logs & Troubleshooting

- Check `~/spotifytorrent.log` for detailed logs
- Downloaded track state is stored in `~/.spotifytorrent.db`
- To clear downloaded history: click **Clear State** in the menu

## CI/CD

This project uses GitHub Actions to automate testing, building, and releases:

- **Testing**: Unit tests are automatically run against multiple Python versions on both Linux and macOS for every push and pull request to the `main` branch. You can see the status of these tests with the badge at the top of this README.
- **Building**: Executable versions for Linux and macOS are built automatically.
- **Releases**: When a new version is tagged (e.g., `v0.2.0`), a GitHub Release is automatically created, and the compiled applications for Linux and macOS are attached as assets for download.

## License

[MIT](LICENSE)
