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


class SoulseekSearcher(AbstractTorrentSearcher):
    """Search and download via Soulseek network using soulseek-cli with progressive fallback and fast query check."""
    def build_url(self, query: str) -> str:
        return ''

    def parse_primary(self, content: str) -> Optional[str]:
        return None

    def notify_authentication_error(self):
        """Provide helpful guidance when Soulseek authentication fails"""
        logging.getLogger(__name__).error("=" * 60)
        logging.getLogger(__name__).error("🚨 SOULSEEK AUTHENTICATION REQUIRED")
        logging.getLogger(__name__).error("=" * 60)
        logging.getLogger(__name__).error("To use Soulseek search, you need to:")
        logging.getLogger(__name__).error("1. Run: soulseek login")
        logging.getLogger(__name__).error("2. Enter your Soulseek username and password")
        logging.getLogger(__name__).error("3. Ensure stable internet connection")
        logging.getLogger(__name__).error("4. Try again")
        logging.getLogger(__name__).error("=" * 60)

    def search(self, query: str) -> Optional[str]:
        """Search and download from Soulseek with improved error handling and timeouts"""
        soulseek_path = shutil.which("soulseek")
        if not soulseek_path:
            logging.getLogger(__name__).error(
                "Soulseek CLI not found. Please install with 'npm install -g soulseek-cli'"
            )
            try:
                from pync import Notifier
                Notifier.notify("Soulseek CLI not found. Install with: npm install -g soulseek-cli", 
                               title="SpotifyTorrent Error")
            except ImportError:
                pass
            return None
        
        logging.getLogger(__name__).info(f"Using soulseek-cli at: {soulseek_path}")
        
        # Test authentication with a quick query
        try:
            logging.getLogger(__name__).info("Testing Soulseek authentication...")
            test_result = subprocess.run(
                ["soulseek", "query", "test"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            output_text = (test_result.stdout + " " + test_result.stderr).lower()
            if any(error in output_text for error in ['timeout login', 'econnreset', 'not logged in', 'authentication failed', 'error: read']):
                self.notify_authentication_error()
                return None
            logging.getLogger(__name__).info("Soulseek authentication test passed.")
        except subprocess.TimeoutExpired:
            logging.getLogger(__name__).warning("Soulseek authentication test timed out, proceeding anyway...")
        except Exception as e:
            logging.getLogger(__name__).warning(f"Soulseek authentication test failed: {e}, proceeding anyway...")
        
        # Ensure download directory exists
        if not os.path.exists(DOWNLOAD_DIR):
            try:
                os.makedirs(DOWNLOAD_DIR, exist_ok=True)
                logging.getLogger(__name__).info(f"Created download directory: {DOWNLOAD_DIR}")
            except OSError as e:
                logging.getLogger(__name__).error(f"Failed to create download directory: {e}")
                return None
        
        logging.getLogger(__name__).info(f"Starting Soulseek search for: '{query}'")
        
        sanitized = self.sanitize(query)
        raw = query.strip()
        
        # Generate search variants (improved logic)
        variants = [raw, sanitized]
        
        # Handle common patterns
        if '(' in raw:
            variants.append(raw.split('(')[0].strip())
        if '-' in raw:
            parts = raw.split('-', 1)
            if len(parts) == 2:
                variants.append(parts[0].strip())
                variants.append(parts[1].strip())
        if ' by ' in raw.lower():
            artist_song = raw.lower().split(' by ')
            if len(artist_song) == 2:
                variants.append(artist_song[1].strip())  # Just the song
                variants.append(f"{artist_song[1].strip()} {artist_song[0].strip()}")  # Song Artist
        if ':' in raw:
            variants.append(raw.split(':', 1)[0].strip())
        
        # Remove featuring/feat variations
        lower_raw = raw.lower()
        for key in ['feat.', 'feat', 'ft.', 'ft', 'featuring']:
            if key in lower_raw:
                idx = lower_raw.find(key)
                if idx != -1:
                    variants.append(raw[:idx].strip())
        
        # Remove quality indicators
        for qual in ['official video', 'official', 'video', 'lyrics', 'audio', 'hd', 'live', 'remastered']:
            if qual in lower_raw:
                idx = lower_raw.find(qual)
                if idx != -1:
                    variants.append(raw[:idx].strip())
        
        # Generate final queries list
        queries = []
        seen = set()
        
        # Add variants in order of priority
        for v in variants:
            sv = self.sanitize(v).strip()
            if sv and len(sv) > 2 and sv not in seen:  # Minimum length check
                seen.add(sv)
                queries.append(sv)
        
        # Add word-based variations for longer queries
        words = sanitized.split()
        if len(words) > 2:
            # First few words
            for i in range(2, min(len(words), 4)):
                partial = ' '.join(words[:i+1])
                if partial not in seen:
                    queries.append(partial)
                    seen.add(partial)
        
        # Limit total queries to prevent excessive searching
        queries = queries[:8]  # Maximum 8 query variants
        
        logging.getLogger(__name__).info(f"Generated {len(queries)} search variants: {queries}")
        
        modes = ['mp3', 'flac']
        qualities = ['320', '256', '192', None]
        
        def has_results(q, mode, quality, timeout=30):
            """Check if query has results with timeout"""
            cmd = ["soulseek", "query", q]
            if mode:
                cmd += ["--mode", mode]
            if quality:
                cmd += ["--quality", quality]
            
            try:
                logging.getLogger(__name__).debug(f"Running query: {' '.join(cmd)}")
                
                # Use Popen for better control over the process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line buffered
                    universal_newlines=True
                )
                
                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    
                    # Log the output for debugging
                    if stdout:
                        logging.getLogger(__name__).debug(f"Query stdout: {stdout.strip()}")
                    if stderr:
                        logging.getLogger(__name__).debug(f"Query stderr: {stderr.strip()}")
                    
                    # Check for authentication/connection errors
                    output_text = (stdout + " " + stderr).lower()
                    if any(error in output_text for error in ['timeout login', 'econnreset', 'not logged in', 'authentication failed', 'error: read']):
                        logging.getLogger(__name__).error(f"Soulseek authentication/connection error for '{q}'.")
                        return False
                    
                    # Check if the query was successful and found results
                    success = process.returncode == 0
                    has_content = stdout and len(stdout.strip()) > 0
                    has_results_text = stdout and ("results" in stdout.lower() or "result:" in stdout.lower())
                    no_results = "no results" in output_text or "0 results" in output_text
                    
                    return success and has_content and has_results_text and not no_results
                    
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()  # Clean up zombie process
                    logging.getLogger(__name__).warning(f"Soulseek query timed out for '{q}' after {timeout}s")
                    return False
                    
            except Exception as e:
                logging.getLogger(__name__).error(f"Soulseek query failed for '{q}': {e}")
                return False
        
        def try_download(q, mode, quality, timeout=90):
            """Try to download with timeout and better error handling"""
            def get_all_files_recursive(directory):
                """Get all files recursively from a directory"""
                all_files = set()
                try:
                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            all_files.add(os.path.join(root, file))
                except OSError:
                    pass
                return all_files
            
            try:
                before = get_all_files_recursive(DOWNLOAD_DIR)
            except OSError:
                before = set()
            
            cmd = ["soulseek", "download", q, "--destination", DOWNLOAD_DIR]
            if mode:
                cmd += ["--mode", mode]
            if quality:
                cmd += ["--quality", quality]
            
            try:
                logging.getLogger(__name__).debug(f"Running download: {' '.join(cmd)}")
                
                # Use Popen to handle interactive input
                process = subprocess.Popen(
                    cmd, 
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Send "1" and Enter to automatically select the first result
                try:
                    stdout, stderr = process.communicate(input="1\n", timeout=timeout)
                    
                    # Log output for debugging
                    if stdout:
                        logging.getLogger(__name__).debug(f"Download stdout: {stdout.strip()}")
                    if stderr:
                        logging.getLogger(__name__).debug(f"Download stderr: {stderr.strip()}")
                    
                    if process.returncode != 0:
                        logging.getLogger(__name__).warning(
                            f"Soulseek download failed for '{q}' (exit code {process.returncode})"
                        )
                        # Check if it failed due to no search results
                        if stdout and "No search results" in stdout:
                            return None
                        # Check if it failed due to user cancellation or timeout
                        if stderr and ("cancelled" in stderr.lower() or "timeout" in stderr.lower()):
                            return None
                            
                except subprocess.TimeoutExpired:
                    process.kill()
                    logging.getLogger(__name__).warning(f"Soulseek download timed out for '{q}' after {timeout}s")
                    return None
                    
            except Exception as e:
                logging.getLogger(__name__).error(
                    f"Soulseek download failed for '{q}' mode={mode} quality={quality}: {e}"
                )
                return None
            
            # Check for downloaded files (including in subdirectories)
            try:
                after = get_all_files_recursive(DOWNLOAD_DIR)
                new_files = after - before
                if new_files:
                    # Filter for audio files and sort by modification time
                    audio_extensions = {'.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac'}
                    audio_files = [f for f in new_files if any(f.lower().endswith(ext) for ext in audio_extensions)]
                    
                    if audio_files:
                        # Sort by modification time to get the most recent file
                        audio_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                        filepath = audio_files[0]
                        
                        # Verify the file is not empty
                        if os.path.getsize(filepath) > 0:
                            logging.getLogger(__name__).info(f"Soulseek downloaded: {filepath} ({os.path.getsize(filepath)} bytes)")
                            return f"file://{filepath}"
                        else:
                            logging.getLogger(__name__).warning(f"Downloaded file is empty: {filepath}")
                            os.remove(filepath)  # Clean up empty file
                            return None
                    else:
                        logging.getLogger(__name__).warning(f"New files found but none are audio files: {new_files}")
                else:
                    logging.getLogger(__name__).warning(f"No new files found after download attempt for '{q}'")
            except OSError as e:
                logging.getLogger(__name__).error(f"Error scanning download directory: {e}")
            return None
        # Try a fast search strategy: start with highest quality and most likely queries
        high_priority_queries = queries[:3]  # First 3 queries are usually best
        low_priority_queries = queries[3:]
        
        # First pass: try high-priority queries with high quality
        for q in high_priority_queries:
            for mode in ['mp3', 'flac']:  # Prioritize mp3 first
                for quality in ['320', '256']:  # Only try high quality first
                    logging.getLogger(__name__).info(
                        f"Soulseek search (priority): '{q}' mode={mode} quality={quality}"
                    )
                    if has_results(q, mode, quality, timeout=20):  # 20 second timeout for query
                        result = try_download(q, mode, quality, timeout=60)  # 60 second timeout for download
                        if result:
                            return result
                    else:
                        logging.getLogger(__name__).debug(f"No results found for '{q}' mode={mode} quality={quality}")
        
        # Second pass: try remaining combinations if nothing found
        all_remaining = [(q, mode, quality) for q in low_priority_queries 
                        for mode in modes for quality in qualities]
        
        # Add lower quality searches for high-priority queries
        for q in high_priority_queries:
            for mode in modes:
                for quality in ['192', None]:
                    all_remaining.append((q, mode, quality))
        
        for q, mode, quality in all_remaining:
            logging.getLogger(__name__).info(
                f"Soulseek search (extended): '{q}' mode={mode} quality={quality}"
            )
            if has_results(q, mode, quality, timeout=25):  # Slightly longer timeout for extended search
                result = try_download(q, mode, quality, timeout=90)  # Longer download timeout
                if result:
                    return result
        
        logging.getLogger(__name__).info(f"No results found for any variant of: {query}")
        return None
