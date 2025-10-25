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
        self.ydl_opts = {
            'outtmpl': os.path.join(self.options.output_dir, '%(title)s.%(ext)s'),
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
        """Download a single CBN video"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract info to get the title for the filename
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'cbn_video')
                
                # Sanitize title for filename
                safe_title = re.sub(r'[^\w\-_\. ]', '', title)
                
                # Download the video
                ydl.download([url])
                
                # Determine the downloaded file path
                ext = info.get('ext', 'mp4')
                if self.options.audio_only and self.options.audio_format:
                    ext = self.options.audio_format
                elif self.options.audio_only:
                    # yt-dlp will determine the best audio format
                    ext = 'webm'  # Common audio format from yt-dlp
                
                output_path = os.path.join(self.options.output_dir, f"{safe_title}.{ext}")
                
                return output_path
                
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