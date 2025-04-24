"""state.py: Persistence for downloaded track IDs using SQLite."""

import os
import sqlite3, logging

type OptionalSet = set[str]

class State:
    def __init__(self, db_path: str | None = None) -> None:
        """Initialize SQLite DB and load processed track IDs into memory."""
        self.db_path = db_path or os.path.expanduser('~/.spotifytorrent.db')
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()
        self.downloaded: OptionalSet = set(self._load_ids())

    def _create_table(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS downloaded(id TEXT PRIMARY KEY)")
        self.conn.commit()

    def _load_ids(self) -> list[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM downloaded")
        return [row[0] for row in cursor.fetchall()]

    def add(self, track_id: str) -> None:
        """Add a track ID to the database and in-memory set."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO downloaded(id) VALUES(?)", (track_id,))
            self.conn.commit()
            self.downloaded.add(track_id)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error saving state to {self.db_path}: {e}")

    def __del__(self) -> None:
        """Close the database connection on object deletion."""
        try:
            self.conn.close()
        except Exception:
            pass