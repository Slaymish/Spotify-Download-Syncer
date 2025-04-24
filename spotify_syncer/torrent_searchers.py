"""
torrent_searchers.py: Defines the TorrentSearcher interface and implementations.
"""

import logging
import re
import requests
from abc import ABC, abstractmethod
from typing import Optional, Type, Dict
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import subprocess, os, shutil
from spotify_syncer.config import DOWNLOAD_DIR
 
class AbstractTorrentSearcher(ABC):
    """Template method pattern: search flow for torrent providers."""
    def search(self, query: str) -> Optional[str]:
        """Execute the full search: sanitize, fetch, parse, fallback, notify."""
        sanitized = self.sanitize(query)
        url = self.build_url(sanitized)
        content = self.fetch(url)
        if not content:
            return None
        primary = self.parse_primary(content)
        if primary:
            return primary
        fallback = self.parse_fallback(content)
        if fallback:
            return fallback
        self.notify_not_found(query, url)
        return None

    def sanitize(self, query: str) -> str:
        """Remove problematic punctuation from the query."""
        sanitized = re.sub(r"[\"',.\-()]", "", query)
        if sanitized != query:
            logging.getLogger(__name__).info(f"Sanitized query: '{query}' → '{sanitized}'")
        return sanitized

    def fetch(self, url: str) -> Optional[str]:
        """Fetch the page content, returning text or None on error."""
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            logging.getLogger(__name__).error(f"Network error searching '{url}': {e}")
            try:
                from pync import Notifier
                Notifier.notify("Network error finding torrent", title="SpotifyTorrent")
            except ImportError:
                pass
            return None

    @abstractmethod
    def build_url(self, query: str) -> str:
        """Construct the search URL for the provider."""
        ...

    @abstractmethod
    def parse_primary(self, content: str) -> Optional[str]:
        """Parse the primary magnet link from page content."""
        ...

    def parse_fallback(self, content: str) -> Optional[str]:
        """Fallback: return first magnet link found, if any."""
        soup = BeautifulSoup(content, "html.parser")
        link = soup.select_one('a[href^="magnet:"]')
        if link and link.has_attr('href'):
            logging.getLogger(__name__).warning("Fallback magnet link used")
            return link['href']
        return None

    def notify_not_found(self, query: str, url: str) -> None:
        """Log and notify when no magnet link is found."""
        logging.getLogger(__name__).warning(f"No magnet link found for '{query}' at {url}")
        try:
            from pync import Notifier
            Notifier.notify(f"No torrent found for '{query}'", title="SpotifyTorrent")
        except ImportError:
            pass

class PirateBayTorrentSearcher(AbstractTorrentSearcher):
    """Concrete TorrentSearcher for The Pirate Bay (music category)."""
    def __init__(self, category: str = "101") -> None:
        self.base_url = "https://thepiratebay.org/search.php"
        self.category = category

    def search(self, query: str) -> Optional[str]:
        """Search via HTML first, then fallback to JSON API if no magnet found."""
        sanitized = self.sanitize(query)
        url = self.build_url(sanitized)
        content = self.fetch(url)
        if not content:
            return None
        # Try HTML parsing
        primary = self.parse_primary(content)
        if primary:
            return primary
        # Fallback to JSON API (apibay.org)
        api_url = f"https://apibay.org/q.php?q={quote_plus(sanitized)}&cat={self.category}"
        try:
            r = requests.get(api_url, timeout=10)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list) and data:
                info_hash = data[0].get('info_hash')
                if info_hash:
                    return f"magnet:?xt=urn:btih:{info_hash}"
        except requests.RequestException as e:
            logging.getLogger(__name__).warning(f"JSON API error searching '{api_url}': {e}")
        # HTML fallback
        fallback = self.parse_fallback(content)
        if fallback:
            return fallback
        self.notify_not_found(query, url)
        return None

    def build_url(self, query: str) -> str:
        return f"{self.base_url}?q={quote_plus(query)}&cat={self.category}"

    def parse_primary(self, content: str) -> Optional[str]:
        soup = BeautifulSoup(content, "html.parser")
        link = soup.select_one('ol#torrents li.list-entry span.item-icons a[href^="magnet:"]')
        return link['href'] if link and link.has_attr('href') else None

class SoulseekSearcher(AbstractTorrentSearcher):
    """Search and download via Soulseek network using soulseek-cli."""
    def build_url(self, query: str) -> str:
        # Not used for Soulseek CLI
        return ''

    def parse_primary(self, content: str) -> Optional[str]:
        # Not applicable
        return None

    def search(self, query: str) -> Optional[str]:
        # verify soulseek CLI is available
        if not shutil.which("soulseek"):
            logging.getLogger(__name__).error(
                "Soulseek CLI not found. Please install with 'npm install -g soulseek-cli'"
            )
            return None
        sanitized = self.sanitize(query)
        # snapshot directory before download
        def try_download(q):
            try:
                before = set(os.listdir(DOWNLOAD_DIR))
            except OSError:
                before = set()
            cmd = ["soulseek", "download", q, "--destination", DOWNLOAD_DIR]
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except Exception as e:
                return None
            try:
                after = set(os.listdir(DOWNLOAD_DIR))
                new_files = after - before
                if new_files:
                    fname = sorted(new_files)[0]
                    filepath = os.path.join(DOWNLOAD_DIR, fname)
                    logging.getLogger(__name__).info(f"Soulseek downloaded file: {filepath}")
                    return f"file://{filepath}"
            except OSError as e:
                logging.getLogger(__name__).error(f"Error scanning download directory: {e}")
            return None
        # Try full query first
        result = try_download(sanitized)
        if result:
            return result
        # Fallback: try only the track name (before artist)
        # Heuristic: split on ' by ', ' - ', or last space
        fallback_query = sanitized
        for sep in [' by ', ' - ', ' – ', ' — ']:
            if sep in sanitized:
                fallback_query = sanitized.split(sep)[0]
                break
        else:
            # fallback to first 3 words if no separator
            fallback_query = ' '.join(sanitized.split()[:3])
        if fallback_query != sanitized:
            logging.getLogger(__name__).info(f"Soulseek fallback search with: {fallback_query}")
            result = try_download(fallback_query)
            if result:
                return result
        return None

 # Registry of available searchers

_searcher_registry: Dict[str, Type[AbstractTorrentSearcher]] = {
    'piratebay': PirateBayTorrentSearcher,
    'soulseek': SoulseekSearcher,
    # add new searchers here
}

def create_searcher(name: str) -> AbstractTorrentSearcher:
     """Factory: instantiate a TorrentSearcher by key."""
     key = name.lower().strip()
     if key not in _searcher_registry:
         raise ValueError(f"Unknown torrent searcher '{name}'")
     return _searcher_registry[key]()