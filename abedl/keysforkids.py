"""
Keys for Kids devotional downloader.

Downloads daily devotional audio files from keysforkids.org.
"""

import re
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from datetime import datetime, timedelta

from .base import BaseDownloader, DownloadOptions, VideoInfo, DownloadError


class KeysForKidsDownloader(BaseDownloader):
    """Downloader for Keys for Kids daily devotional audio files."""
    
    def __init__(self, options: Optional[DownloadOptions] = None):
        """Initialize the downloader with options."""
        if options is None:
            options = DownloadOptions()
        super().__init__(options)
    
    def can_handle(self, url: str) -> bool:
        """Check if this downloader can handle the given URL."""
        parsed = urlparse(url)
        return 'keysforkids.org' in parsed.netloc
    
    def download_video(self, url: str) -> str:
        """
        Download audio from a Keys for Kids devotional page.
        
        Args:
            url: URL of the devotional page
            
        Returns:
            Path to the downloaded file
            
        Raises:
            DownloadError: If download fails
        """
        options = self.options
            
        # Fetch the page HTML
        print(f"Fetching devotional page: {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        # Extract audio URL from page
        audio_url = self._find_audio_url(response.text)
        if not audio_url:
            raise ValueError(f"No audio file found on page: {url}")
        
        print(f"Found audio URL: {audio_url}")
        
        # Extract metadata for filename
        metadata = self._extract_metadata(response.text, url)
        
        # Create filename from metadata
        date_str = metadata.get('date', 'unknown')
        title = metadata.get('title', 'devotional')
        # Sanitize title for filename
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        filename = f"{date_str}_{safe_title}.mp3"
        output_file = Path(options.output_dir) / filename
        
        # Create output directory if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Download the audio file (follow redirects to Castos CDN)
        print(f"Downloading audio to: {output_file}")
        audio_response = requests.get(audio_url, stream=True, allow_redirects=True)
        audio_response.raise_for_status()
        
        # Write file with progress indication
        total_size = int(audio_response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_file, 'wb') as f:
            for chunk in audio_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end='', flush=True)
        
        if total_size > 0:
            print()  # New line after progress
        
        print(f"Download complete: {output_file}")
        return str(output_file)
    
    def get_video_info(self, url: str) -> VideoInfo:
        """
        Get metadata about a devotional.
        
        Args:
            url: URL of the devotional page
            
        Returns:
            VideoInfo object containing metadata
            
        Raises:
            DownloadError: If unable to extract metadata
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            metadata = self._extract_metadata(response.text, url)
            
            return VideoInfo(
                title=metadata.get('title', 'Unknown Title'),
                url=url,
                description=metadata.get('verse', ''),
                upload_date=metadata.get('date', '')
            )
        except Exception as e:
            raise DownloadError(f"Error fetching metadata: {e}")
    
    def get_playlist_info(self, url: str) -> list[VideoInfo]:
        """
        Get metadata about a playlist (not implemented for Keys for Kids).
        
        Args:
            url: URL of the devotional page
            
        Returns:
            List containing single VideoInfo (devotionals don't have playlists)
        """
        return [self.get_video_info(url)]
    
    def download_playlist(self, url: str) -> list[str]:
        """
        Download playlist (not implemented for Keys for Kids).
        
        Args:
            url: URL of the devotional page
            
        Returns:
            List containing single download path
        """
        return [self.download_video(url)]
    
    def _find_audio_url(self, html: str) -> Optional[str]:
        """
        Extract audio URL from devotional page HTML.
        
        Args:
            html: HTML content of the page
            
        Returns:
            URL to the MP3 file, or None if not found
        """
        # Look for MP3 URLs in the format:
        # https://www.keysforkids.org/podcast-player/{post_id}/{slug}.mp3
        mp3_pattern = r'https?://[^\s<>"]+\.mp3'
        matches = re.findall(mp3_pattern, html)
        
        # Filter for Keys for Kids podcast player URLs
        for url in matches:
            if 'keysforkids.org/podcast-player/' in url:
                return url
        
        # Return first mp3 URL if no podcast-player URL found
        return matches[0] if matches else None
    
    def _extract_metadata(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract metadata from devotional page.
        
        Args:
            html: HTML content of the page
            url: URL of the page
            
        Returns:
            Dictionary containing title, date, verse, etc.
        """
        metadata = {'url': url}
        
        # Extract title (from h1 or title tag)
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = re.sub(r'<[^>]+>', '', title_match.group(1))  # Remove HTML tags
            metadata['title'] = title.strip()
        
        # Extract date (look for patterns like "NOVEMBER 10, 2025" or date in URL)
        date_match = re.search(r'(\w+ \d+, \d{4})', html)
        if date_match:
            metadata['date'] = date_match.group(1)
        else:
            # Try to extract from URL slug
            slug_match = re.search(r'/([^/]+)/?$', url)
            if slug_match:
                metadata['slug'] = slug_match.group(1)
        
        # Extract Bible verse reference
        verse_match = re.search(r'<a[^>]*>([^<]*\d+:\d+[^<]*)</a>', html)
        if verse_match:
            metadata['verse'] = verse_match.group(1).strip()
        
        return metadata
    
    @staticmethod
    def get_devotional_url_by_date(date: datetime, max_pages: int = 324) -> Optional[str]:
        """
        Get the devotional URL for a specific date.
        
        Uses a smart search algorithm that estimates which page to check based on
        how old the date is, then searches nearby pages.
        
        Args:
            date: Date to search for
            max_pages: Maximum number of archive pages to search (default: 324)
            
        Returns:
            URL to the devotional page, or None if not found
        """
        date_pattern = date.strftime('%B %-d, %Y')
        
        def check_page(page_num: int) -> Optional[str]:
            """Helper function to check a specific page for the date."""
            if page_num == 1:
                archive_url = 'https://www.keysforkids.org/podcasts/keys-for-kids/'
            else:
                archive_url = f'https://www.keysforkids.org/podcasts/keys-for-kids/page/{page_num}/'
            
            try:
                response = requests.get(archive_url, timeout=10)
                response.raise_for_status()
                
                # Look for the date in the HTML
                idx = response.text.find(date_pattern)
                
                if idx != -1:
                    # Found the date on this page
                    context = response.text[idx:idx+1000]
                    
                    # Find the first devotional URL after the date
                    url_match = re.search(
                        r'href="(https://www\.keysforkids\.org/podcast/(?:keys-for-kids|default)/[^/"]+/)"',
                        context
                    )
                    
                    if url_match:
                        return url_match.group(1)
            except Exception:
                pass
            
            return None
        
        try:
            # First try the date search
            search_url = f'https://www.keysforkids.org/podcasts/keys-for-kids/?date={date.strftime("%Y-%m-%d")}'
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
            
            idx = response.text.find(date_pattern)
            if idx != -1:
                # Get context after the date
                context = response.text[idx:idx+1000]
                
                # Find the first devotional URL after the date
                url_match = re.search(
                    r'href="(https://www\.keysforkids\.org/podcast/(?:keys-for-kids|default)/[^/"]+/)"',
                    context
                )
                
                if url_match:
                    return url_match.group(1)
            
            # Estimate which page the date might be on
            # Assume ~10 devotionals per page (7 days/week)
            today = datetime.now()
            days_ago = (today - date).days
            
            # Estimate page number (10 devotionals per page)
            estimated_page = max(1, days_ago // 10)
            
            # Cap the estimated page at max_pages
            estimated_page = min(estimated_page, max_pages)
            
            print(f"Date is ~{days_ago} days old, estimating page {estimated_page}")
            
            # Search strategy: check estimated page, then expand outward
            # This finds the devotional faster for old dates
            pages_to_check = [estimated_page]
            
            # Add nearby pages in expanding radius
            for offset in range(1, 6):  # Check 5 pages on each side
                if estimated_page - offset >= 1:
                    pages_to_check.append(estimated_page - offset)
                if estimated_page + offset <= max_pages:
                    pages_to_check.append(estimated_page + offset)
            
            # Check each page in order
            for page in pages_to_check:
                result = check_page(page)
                if result:
                    return result
            
            # If still not found and we haven't checked page 1, check it
            if 1 not in pages_to_check:
                result = check_page(1)
                if result:
                    return result
            
            return None
        except Exception as e:
            print(f"Error searching for devotional by date: {e}")
            return None
    
    @staticmethod
    def download_by_date(date: datetime, output_dir: str = "./downloads") -> Optional[str]:
        """
        Download a devotional by date.
        
        Args:
            date: Date of the devotional to download
            output_dir: Directory to save the file
            
        Returns:
            Path to the downloaded file, or None if not found
        """
        url = KeysForKidsDownloader.get_devotional_url_by_date(date)
        
        if not url:
            print(f"No devotional found for {date.strftime('%Y-%m-%d')}")
            return None
        
        print(f"Found devotional for {date.strftime('%Y-%m-%d')}: {url}")
        
        options = DownloadOptions(output_dir=output_dir)
        downloader = KeysForKidsDownloader(options)
        
        return downloader.download_video(url)
    
    @staticmethod
    def download_date_range(start_date: datetime, end_date: datetime, 
                           output_dir: str = "./downloads") -> list[str]:
        """
        Download devotionals for a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            output_dir: Directory to save the files
            
        Returns:
            List of paths to downloaded files
        """
        downloaded_files = []
        current_date = start_date
        
        while current_date <= end_date:
            print(f"\n--- Downloading devotional for {current_date.strftime('%Y-%m-%d')} ---")
            file_path = KeysForKidsDownloader.download_by_date(current_date, output_dir)
            
            if file_path:
                downloaded_files.append(file_path)
            
            current_date += timedelta(days=1)
        
        return downloaded_files
