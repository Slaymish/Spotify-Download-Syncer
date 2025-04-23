import logging, re, requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from pync import Notifier
from abc import ABC, abstractmethod
from typing import Optional

class AbstractTorrentSearcher(ABC):
    """Template Method for torrent searchers."""
    def search(self, query: str) -> Optional[str]:
        sanitized = self.sanitize(query)
        url = self.build_url(sanitized)
        content = self.fetch(url)
        if not content:
            return None
        result = self.parse_primary(content)
        if result:
            return result
        result = self.parse_fallback(content)
        if result:
            return result
        self.notify_not_found(query, url)
        return None

    def sanitize(self, query: str) -> str:
        import re, logging
        sanitized = re.sub(r"[\"',\.\-()]", "", query)
        if sanitized != query:
            logging.info(f"Sanitized query: '{query}' → '{sanitized}'")
        return sanitized

    def fetch(self, url: str) -> Optional[str]:
        import requests, logging
        from requests.exceptions import RequestException
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.text
        except RequestException as e:
            logging.error(f"Network error searching '{url}': {e}")
            from pync import Notifier
            Notifier.notify(f"Network error finding torrent", title="SpotifyTorrent")
            return None

    @abstractmethod
    def build_url(self, query: str) -> str:
        pass

    @abstractmethod
    def parse_primary(self, content: str) -> Optional[str]:
        pass

    def parse_fallback(self, content: str) -> Optional[str]:
        from bs4 import BeautifulSoup
        import logging
        soup = BeautifulSoup(content, "html.parser")
        fallback = soup.select_one('a[href^="magnet:"]')
        if fallback and fallback.has_attr('href'):
            logging.warning("Fallback magnet link used")
            return fallback['href']
        return None

    def notify_not_found(self, query: str, url: str):
        import logging
        from pync import Notifier
        logging.warning(f"No magnet link found for '{query}' at {url}")
        Notifier.notify(f"No torrent found for '{query}'", title="SpotifyTorrent")

class PirateBayTorrentSearcher(AbstractTorrentSearcher):
    def __init__(self, category: str = "101"):
        self.base_url = "https://thepiratebay.org/search.php"
        self.category = category

    def build_url(self, query: str) -> str:
        from urllib.parse import quote_plus
        return f"{self.base_url}?q={quote_plus(query)}&cat={self.category}"

    def parse_primary(self, content: str) -> Optional[str]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        mag = soup.select_one('ol#torrents li.list-entry span.item-icons a[href^="magnet:"]')
        return mag['href'] if mag and mag.has_attr('href') else None

# Searcher registry and factory
_registry = {
    'piratebay': PirateBayTorrentSearcher,
    # add new searcher implementations here, e.g. 'othersite': OtherSiteSearcher
}

def create_searcher(name: str) -> TorrentSearcher:
    """Factory: create a TorrentSearcher by registry key."""
    try:
        cls = _registry[name.lower()]
    except KeyError:
        raise ValueError(f"Unknown torrent searcher '{name}'")
    return cls()