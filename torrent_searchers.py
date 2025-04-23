import logging, re, requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from pync import Notifier
from abc import ABC, abstractmethod
from typing import Optional

class TorrentSearcher(ABC):
    @abstractmethod
    def search(self, query: str) -> Optional[str]:
        """Return a magnet URI for the given query, or None if not found."""
        pass

class PirateBayTorrentSearcher(TorrentSearcher):
    def __init__(self, category: str = "101"):
        self.base_url = "https://thepiratebay.org/search.php"
        self.category = category

    def search(self, query: str) -> Optional[str]:
        sanitized = re.sub(r"[\"',\.\-()]", "", query)
        if sanitized != query:
            logging.info(f"Sanitized query: '{query}' → '{sanitized}'")
        url = f"{self.base_url}?q={quote_plus(sanitized)}&cat={self.category}"
        logging.info(f"Searching TPB URL: {url}")
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error searching TPB for '{query}': {e}")
            Notifier.notify(f"Network error finding torrent for '{query}'", title="SpotifyTorrent")
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        mag = soup.select_one('ol#torrents li.list-entry span.item-icons a[href^="magnet:"]')
        if mag and mag.has_attr('href'):
            return mag['href']
        fallback = soup.select_one('a[href^="magnet:"]')
        if fallback and fallback.has_attr('href'):
            logging.warning(f"Fallback magnet link used for '{query}'")  
            return fallback['href']
        logging.warning(f"No magnet link found for '{query}' at {url}")
        Notifier.notify(f"No torrent found for '{query}'", title="SpotifyTorrent")
        return None

# default instance, swap this out to use another searcher implementation
default_searcher = PirateBayTorrentSearcher()