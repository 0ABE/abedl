#
#        d8888 888888b.   8888888888 8888888b.  888      
#       d88888 888  "88b  888        888  "Y88b 888      
#      d88P888 888  .88P  888        888    888 888      
#     d88P 888 8888888K.  8888888    888    888 888      
#    d88P  888 888  "Y88b 888        888    888 888      
#   d88P   888 888    888 888        888    888 888      
#  d8888888888 888   d88P 888        888  .d88P 888      
# d88P     888 8888888P"  8888888888 8888888P"  88888888 
#                                                        
# Copyright (c) 2025, Abe Mishler
# Licensed under the Universal Permissive License v 1.0
# as shown at https://oss.oracle.com/licenses/upl/. 
# 

"""
CBN (Christian Broadcasting Network) downloader implementation using yt-dlp.
Handles videos from cbn.com including Flying House episodes.
"""

import re
import os
from typing import List, Optional
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    raise ImportError("yt-dlp is required for CBN downloads. Install with: pip install yt-dlp")

from .base import BaseDownloader, VideoInfo, DownloadOptions, DownloadError


class CBNDownloader(BaseDownloader):
    """CBN video downloader using yt-dlp"""
    
    # CBN URL patterns
    CBN_PATTERNS = [
        r'(?:https?://)?(?:www\.)?cbn\.com/video/[\w-]+',
        r'(?:https?://)?(?:www\.)?cbn\.com/video/flying-house-episode-\d+',
        r'(?:https?://)?(?:www\.)?cbn\.com/shows/[\w-]+/[\w-]+',
    ]
    
    def __init__(self, options: DownloadOptions):
        super().__init__(options)
        self._setup_ydl_opts()
    
    def _setup_ydl_opts(self) -> None:
        """Setup yt-dlp options based on download options"""
        # Use a custom output template that will be overridden in download_video
        self.ydl_opts = {
            'outtmpl': os.path.join(self.options.output_dir, 'temp_%(id)s.%(ext)s'),
            'format': self._get_format_string(),
            'writeinfojson': self.options.write_info_json,
            'writethumbnail': self.options.write_thumbnail,
            'writesubtitles': self.options.subtitles,
            'embedsubtitles': self.options.embed_subtitles,
            'ignoreerrors': False,  # We want to handle errors ourselves
            'no_warnings': False,  # Show warnings for debugging
            'extract_flat': False,  # Don't extract playlist info only
            # Anti-bot detection measures
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'extractor_retries': 3,
            'fragment_retries': 3,
            'retry_sleep_functions': {'extractor': lambda n: 2 + n, 'fragment': lambda n: 2 + n},
        }
        
        # Add audio-only options if specified
        if self.options.audio_only:
            self.ydl_opts['format'] = 'bestaudio/best'
            if self.options.audio_format:
                self.ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.options.audio_format,
                }]
            else:
                self.ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'best',
                }]
        
        # Add cookie support
        if self.options.cookies_from_browser:
            self.ydl_opts['cookiesfrombrowser'] = (self.options.cookies_from_browser,)
        elif self.options.cookies:
            self.ydl_opts['cookiefile'] = self.options.cookies
    
    def _get_format_string(self) -> str:
        """Generate yt-dlp format string based on options"""
        if self.options.audio_only:
            return 'bestaudio/best'
        
        if self.options.quality == 'best':
            return 'best'
        elif self.options.quality == 'worst':
            return 'worst'
        else:
            # Custom quality (e.g., "720p", "1080p")
            height = self.options.quality.replace("p", "")
            return f'best[height<={height}]/best[height<={int(height)+100}]/best'
    
    def can_handle(self, url: str) -> bool:
        """Check if this downloader can handle CBN URLs"""
        return any(re.match(pattern, url, re.IGNORECASE) for pattern in self.CBN_PATTERNS)
    
    def _parse_episode_info(self, url: str, title: str, description: str = None) -> tuple[str, str, str]:
        """
        Parse episode information from URL, title, and description to create Netflix-style naming.
        Returns: (series_name, episode_number, episode_title)
        """
        series_name = "CBN Video"
        episode_number = ""
        episode_title = title
        
        # Use description as episode title if available and meaningful
        if description and description.strip() and len(description.strip()) > 3:
            # Use description instead of title for cleaner episode names
            episode_title = description.strip()
        
        # Check if it's a Flying House episode
        if "flying-house-episode-" in url:
            series_name = "Flying House"
            # Extract episode number from URL
            episode_match = re.search(r'flying-house-episode-(\d+)', url)
            if episode_match:
                ep_num = int(episode_match.group(1))
                episode_number = f"E{ep_num:02d}"  # Format as E01, E02, etc.
        
        # Try to extract episode number from title if not found in URL
        if not episode_number:
            title_episode_match = re.search(r'episode\s*(\d+)', title, re.IGNORECASE)
            if title_episode_match:
                ep_num = int(title_episode_match.group(1))
                episode_number = f"E{ep_num:02d}"
        
        # Clean the episode title by removing redundant series/episode info
        clean_title = re.sub(r'flying\s*house\s*-?\s*', '', episode_title, flags=re.IGNORECASE)
        clean_title = re.sub(r'episode\s*\d+\s*-?\s*', '', clean_title, flags=re.IGNORECASE)
        clean_title = clean_title.strip(' -')
        
        # If clean_title is empty after cleaning, use the original title or description
        if not clean_title:
            clean_title = episode_title
        
        return series_name, episode_number, clean_title
    
    def _create_netflix_filename(self, url: str, title: str, ext: str, description: str = None) -> str:
        """
        Create a Netflix-style filename: 'Series Name - S01E01 - Episode Title.ext'
        For single episodes without season info: 'Series Name - E01 - Episode Title.ext'
        """
        series_name, episode_number, episode_title = self._parse_episode_info(url, title, description)
        
        # Sanitize components for filename safety
        safe_series = re.sub(r'[^\w\-_\. ]', '', series_name)
        safe_title = re.sub(r'[^\w\-_\. ]', '', episode_title)
        
        if episode_number:
            # Netflix format: Series Name - E01 - Episode Title
            filename = f"{safe_series} - {episode_number} - {safe_title}.{ext}"
        else:
            # Fallback for non-episode content
            filename = f"{safe_series} - {safe_title}.{ext}"
        
        # Clean up any double spaces or dashes
        filename = re.sub(r'\s+', ' ', filename)
        filename = re.sub(r'-\s*-', '-', filename)
        
        return filename
    
    def get_video_info(self, url: str) -> VideoInfo:
        """Extract video information using yt-dlp"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return VideoInfo(
                    title=info.get('title', 'Unknown Title'),
                    url=url,
                    duration=info.get('duration'),
                    description=info.get('description'),
                    uploader=info.get('uploader', 'CBN'),
                    upload_date=info.get('upload_date'),
                    view_count=info.get('view_count'),
                    thumbnail_url=info.get('thumbnail')
                )
        except Exception as e:
            raise DownloadError(f"Failed to extract CBN video info: {str(e)}")
    
    def get_playlist_info(self, url: str) -> List[VideoInfo]:
        """
        Extract playlist information. CBN doesn't typically have playlists,
        but this method is required by the base class.
        """
        # CBN videos are typically individual, not playlists
        # Return single video info as a list
        try:
            video_info = self.get_video_info(url)
            return [video_info]
        except Exception as e:
            raise DownloadError(f"Failed to extract CBN playlist info: {str(e)}")
    
    def download_video(self, url: str) -> str:
        """Download a single CBN video with Netflix-style naming"""
        try:
            # First, extract info to get the title, description, and other metadata
            info_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'CBN Video')
                description = info.get('description', '')
                ext = info.get('ext', 'mp4')
                
                # Create Netflix-style filename using title and description
                netflix_filename = self._create_netflix_filename(url, title, ext, description)
                final_path = os.path.join(self.options.output_dir, netflix_filename)
                
                # Update output template to use our custom filename
                download_opts = self.ydl_opts.copy()
                download_opts['outtmpl'] = final_path
                
                # Handle audio-only downloads
                if self.options.audio_only:
                    if self.options.audio_format:
                        ext = self.options.audio_format
                        # Update filename with correct audio extension
                        netflix_filename = self._create_netflix_filename(url, title, ext, description)
                        final_path = os.path.join(self.options.output_dir, netflix_filename)
                        download_opts['outtmpl'] = final_path
                    else:
                        # Let yt-dlp determine the best audio format
                        # Update filename to remove video extension
                        base_name = netflix_filename.rsplit('.', 1)[0]
                        download_opts['outtmpl'] = os.path.join(self.options.output_dir, f"{base_name}.%(ext)s")
                
                print(f"Downloading: {title}")
                if description and len(description.strip()) > 3:
                    print(f"Description: {description[:50]}{'...' if len(description) > 50 else ''}")
                print(f"Saving as: {os.path.basename(final_path)}")
                
                # Download the video
                with yt_dlp.YoutubeDL(download_opts) as download_ydl:
                    download_ydl.download([url])
                
                return final_path
                
        except Exception as e:
            raise DownloadError(f"Failed to download CBN video: {str(e)}")
    
    def download_playlist(self, url: str) -> List[str]:
        """
        Download playlist. For CBN, this typically means downloading a single video.
        """
        return [self.download_video(url)]
    
    def is_playlist(self, url: str) -> bool:
        """
        Check if the URL is a playlist. CBN typically doesn't have playlists,
        so this usually returns False.
        """
        # CBN URLs are typically individual videos
        return False
    
    def get_available_formats(self, url: str) -> List[dict]:
        """Get available video formats for the given URL"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'listformats': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                # Return simplified format info
                simplified_formats = []
                for fmt in formats:
                    simplified_formats.append({
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'resolution': fmt.get('resolution'),
                        'filesize': fmt.get('filesize'),
                        'fps': fmt.get('fps'),
                        'vcodec': fmt.get('vcodec'),
                        'acodec': fmt.get('acodec'),
                    })
                
                return simplified_formats
        except Exception as e:
            raise DownloadError(f"Failed to get CBN video formats: {str(e)}")