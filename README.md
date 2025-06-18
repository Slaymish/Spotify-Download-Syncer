![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Slaymish/Spotify-Download-Syncer/.github%2Fworkflows%2Fci.yml?branch=main)

# SpotifyTorrent Tray App

A cross-platform (macOS/Linux) tray application that syncs a Spotify playlist to Soulseek downloads.

## Prerequisites

> **Note:** If you downloaded the prebuilt release, you can skip the Python setup below; only `soulseek-cli` is required.

- macOS or Linux with Python 3.9+
- On Linux, you may need system tray and notify dependencies:
- On Arch Linux, you may need to install the following dependencies:
    ```bash
    sudo pacman -S python-gobject libappindicator-gtk3 libnotify
    ```
- Spotify Developer App (Client ID & Secret)
- For Soulseek: `npm install -g soulseek-cli`

## Quick Start

### Download & Run (Prebuilt)

Prebuilt executables are available—no Python or manual .env setup required.

1. Visit the [Releases page](https://github.com/Slaymish/Spotify-Download-Syncer/releases) and download the package for your OS:
   - **macOS**: `spotify-syncer-macos.zip`
   - **Linux**: `spotify-syncer-linux`
2. **macOS**: double-click the downloaded ZIP file (`spotify-syncer-macos.zip`) to unzip it, then double-click `spotify-torrent-menu.app` to launch.
   **Linux**: make the binary executable (`chmod +x spotify-syncer-linux`) and run it (`./spotify-syncer-linux`).
3. On first launch, the Settings dialog will open automatically. Enter your Spotify API credentials, Soulseek account info, download directory, and other options.

### From Source (Advanced)

If you prefer to run from source, ensure Python 3.9+ is installed and then:

```bash
git clone https://github.com/hamishmb/spotify-torrent.git
cd spotify-torrent
python -m venv venv
source venv/bin/activate
pip install -e .
```

Launch the app with:

```bash
python spotify-torrent-menu.py
```

Use **Settings** from the tray/menu icon to configure your credentials and options.

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
