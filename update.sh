#!/usr/bin/env bash
# update.sh: pull latest code and reinstall dependencies

set -euo pipefail

echo "Pulling latest changes from remote..."
git pull --ff-only

echo "Reinstalling application in-place (installing/updating dependencies)..."
pip install -e .

echo "Update complete. Please restart the SpotifyTorrent application."