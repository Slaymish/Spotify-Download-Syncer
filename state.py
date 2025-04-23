import os, json, logging

class State:
    def __init__(self, path=None):
        self.path = path or os.path.expanduser('~/.spotify_downloaded.json')
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    self.downloaded = set(json.load(f))
            except Exception as e:
                logging.error(f"Error loading state from {self.path}: {e}")
                self.downloaded = set()
        else:
            self.downloaded = set()

    def add(self, track_id: str):
        self.downloaded.add(track_id)
        self.save()

    def save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump(list(self.downloaded), f)
        except Exception as e:
            logging.error(f"Error saving state to {self.path}: {e}")