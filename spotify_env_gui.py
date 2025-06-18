#!/usr/bin/env python3
"""
spotify_env_gui.py: GUI for editing .env configuration for SpotifyTorrent app.
"""

import os
import sys

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("tkinter is required to run this script. Please install tkinter.")
    sys.exit(1)

try:
    from dotenv import dotenv_values, set_key, find_dotenv
except ImportError:
    print("python-dotenv is required to run this script. Please install python-dotenv.")
    sys.exit(1)

# Determine which configuration keys to expose in the GUI
try:
    from spotify_syncer.config import REQUIRED_ENV_VARS
except ImportError:
    REQUIRED_ENV_VARS = [
        'SPOTIPY_CLIENT_ID',
        'SPOTIPY_CLIENT_SECRET',
        'SPOTIPY_REDIRECT_URI',
        'SPOTIFY_PLAYLIST_ID',
        'DOWNLOAD_DIR',
        'SOULSEEK_ACCOUNT',
        'SOULSEEK_PASSWORD',
    ]
# Include optional flags after required variables
DEFAULT_KEYS = REQUIRED_ENV_VARS + ['DELETE_AFTER_DOWNLOADED']


def main():
    dotenv_path = find_dotenv()
    if not dotenv_path:
        dotenv_path = os.path.join(os.getcwd(), '.env')
        if not os.path.exists(dotenv_path):
            open(dotenv_path, 'a').close()

    values = dotenv_values(dotenv_path)
    # Populate default keys first, then preserve any additional existing keys
    keys = list(DEFAULT_KEYS)
    for key in values.keys():
        if key not in keys:
            keys.append(key)

    root = tk.Tk()
    root.title("SpotifyTorrent Settings")
    entries = {}

    for idx, key in enumerate(keys):
        tk.Label(root, text=key).grid(row=idx, column=0, sticky='e', padx=5, pady=2)
        var = tk.StringVar(value=values.get(key, ''))
        entry = tk.Entry(root, textvariable=var, width=50)
        entry.grid(row=idx, column=1, padx=5, pady=2)
        entries[key] = var

    def on_save():
        for key, var in entries.items():
            set_key(dotenv_path, key, var.get())
        messagebox.showinfo(
            title="Settings Saved",
            message="Settings have been saved. Please restart the app for changes to take effect."
        )
        root.destroy()

    def on_cancel():
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.grid(row=len(keys), columnspan=2, pady=10)
    tk.Button(btn_frame, text="Save", command=on_save).pack(side='left', padx=5)
    tk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side='left', padx=5)

    root.mainloop()


if __name__ == '__main__':
    main()