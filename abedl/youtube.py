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
YouTube downloader implementation using yt-dlp.
"""

import re
import os
from typing import List, Optional
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    raise ImportError("yt-dlp is required for YouTube downloads. Install with: pip install yt-dlp")

from .base import BaseDownloader, VideoInfo, DownloadOptions, DownloadError


class YouTubeDownloader(BaseDownloader):
    """YouTube video and playlist downloader using yt-dlp"""
    
    # YouTube URL patterns
    YOUTUBE_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
        r'(?:https?://)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/channel/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/@[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/c/[\w-]+',
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
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'extractor_retries': 3,
            'fragment_retries': 3,
            'retry_sleep_functions': {'extractor': lambda n: 2 + n, 'fragment': lambda n: 2 + n},
        }
        
        # Add audio-only options if specified
        if self.options.audio_only:
            self.ydl_opts['format'] = 'bestaudio/best'
            # If audio_format is specified, use FFmpeg to extract/convert
            if self.options.audio_format:
                self.ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.options.audio_format,
                }]
            else:
                # Default to extracting audio as webm/m4a (native audio formats)
                # This ensures we get pure audio files, not video containers
                self.ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'best',  # Keep the best native audio codec
                }]
        
        # Add cookie support to avoid bot detection
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
            # Use a more robust format selector that falls back if exact height isn't available
            height = self.options.quality.replace("p", "")
            return f'best[height<={height}]/best[height<={int(height)+100}]/best'
    
    def can_handle(self, url: str) -> bool:
        """Check if this downloader can handle YouTube URLs"""
        return any(re.match(pattern, url, re.IGNORECASE) for pattern in self.YOUTUBE_PATTERNS)
    
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
                    uploader=info.get('uploader'),
                    upload_date=info.get('upload_date'),
                    view_count=info.get('view_count'),
                    thumbnail_url=info.get('thumbnail')
                )
        except Exception as e:
            raise DownloadError(f"Failed to extract video info: {str(e)}")
    
    def get_playlist_info(self, url: str) -> List[VideoInfo]:
        """Extract playlist information using yt-dlp"""
        try:
            # Clean the URL to focus on the playlist - remove video-specific parameters
            # if both video and playlist are present
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            
            playlist_url = url
            if 'list' in params and 'v' in params:
                # If both video and playlist are present, create a clean playlist URL
                list_id = params['list'][0]
                playlist_url = f"https://www.youtube.com/playlist?list={list_id}"
                print(f"Detected combined URL, using playlist URL: {playlist_url}")
            
            # Use extract_flat for playlist info to avoid format listing issues
            playlist_opts = {
                'quiet': True, 
                'extract_flat': True,
                'no_warnings': True,
                'ignoreerrors': True,  # Continue if some videos fail
                'playlistend': 100,    # Increased limit for range selection
            }
            
            with yt_dlp.YoutubeDL(playlist_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                
                if not info or 'entries' not in info:
                    raise DownloadError("No entries found in playlist")
                
                videos = []
                for entry in info['entries']:
                    if entry:  # Skip None entries
                        # Build full URL if only ID is provided
                        video_url = entry.get('url', '')
                        if not video_url and entry.get('id'):
                            video_url = f"https://www.youtube.com/watch?v={entry.get('id')}"
                        
                        videos.append(VideoInfo(
                            title=entry.get('title', 'Unknown Title'),
                            url=video_url,
                            duration=entry.get('duration'),
                            uploader=entry.get('uploader'),
                            view_count=entry.get('view_count')
                        ))
                
                return videos
        except Exception as e:
            raise DownloadError(f"Failed to extract playlist info: {str(e)}")
    
    def _normalize_playlist_url(self, url: str) -> str:
        """Normalize playlist URL to ensure it's properly formatted"""
        # If it's already a playlist URL, return as-is
        if 'list=' in url:
            return url
        
        # If it's a video URL that might be part of a playlist, try to extract playlist ID
        # For now, just return the URL as-is
        return url
    
    def _parse_playlist_items(self, playlist_items: str) -> List[int]:
        """Parse playlist items string into list of indices"""
        indices = []
        if not playlist_items:
            return indices
        
        for part in playlist_items.split(','):
            part = part.strip()
            if '-' in part:
                # Handle range like "5-8"
                try:
                    start, end = map(int, part.split('-'))
                    indices.extend(range(start, end + 1))
                except ValueError:
                    print(f"Warning: Invalid range '{part}', skipping")
            else:
                # Handle single number
                try:
                    indices.append(int(part))
                except ValueError:
                    print(f"Warning: Invalid number '{part}', skipping")
        
        return sorted(set(indices))  # Remove duplicates and sort
    
    def _filter_playlist_by_range(self, videos: List[VideoInfo]) -> List[VideoInfo]:
        """Filter playlist videos based on options"""
        if not videos:
            return videos
        
        # If specific items are requested, use those
        if self.options.playlist_items:
            indices = self._parse_playlist_items(self.options.playlist_items)
            if indices:
                filtered_videos = []
                for i in indices:
                    if 1 <= i <= len(videos):
                        filtered_videos.append(videos[i - 1])  # Convert to 0-based index
                    else:
                        print(f"Warning: Index {i} is out of range (playlist has {len(videos)} videos)")
                return filtered_videos
        
        # Otherwise use start/end range
        start = max(1, self.options.playlist_start) - 1  # Convert to 0-based
        end = min(len(videos), self.options.playlist_end or len(videos))
        
        if start >= len(videos):
            print(f"Warning: Start index {self.options.playlist_start} is beyond playlist length ({len(videos)})")
            return []
        
        if start >= end:
            print(f"Warning: Start index ({self.options.playlist_start}) is >= end index ({self.options.playlist_end})")
            return []
        
        return videos[start:end]
    
    def download_video(self, url: str) -> str:
        """Download a single video using yt-dlp"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract info and download in one step
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Handle post-processing filename changes
                if self.options.audio_only and self.options.audio_format:
                    # Update extension for audio files
                    base_name = os.path.splitext(filename)[0]
                    filename = f"{base_name}.{self.options.audio_format}"
                
                return filename
                
        except yt_dlp.DownloadError as e:
            # Handle specific yt-dlp errors, including format selection issues and bot detection
            error_msg = str(e)
            
            # Check for bot detection error
            if "bot" in error_msg.lower() or "sign in" in error_msg.lower():
                print("\n🤖 YouTube bot detection triggered!")
                print("This can happen with frequent downloads or certain videos.")
                print("\nSolutions:")
                print("1. Try again in a few minutes")
                print("2. Use cookies from your browser:")
                print("   --cookies-from-browser chrome")
                print("   --cookies-from-browser firefox") 
                print("   --cookies-from-browser safari")
                print("3. Export cookies manually:")
                print("   - Install a browser extension like 'Get cookies.txt'")
                print("   - Export YouTube cookies to a file")
                print("   - Use: --cookies /path/to/cookies.txt")
                print("\nFor more help: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp")
                raise DownloadError(f"YouTube bot detection: {error_msg}")
            
            # Handle format selection errors
            if "format" in error_msg.lower() or "list" in error_msg.lower():
                # Try with fallback format if format selection fails
                try:
                    fallback_opts = self.ydl_opts.copy()
                    # Preserve audio-only setting in fallback
                    if self.options.audio_only:
                        fallback_opts['format'] = 'bestaudio'  # Use audio-only fallback
                    else:
                        fallback_opts['format'] = 'best'  # Use simple best format for video
                    
                    with yt_dlp.YoutubeDL(fallback_opts) as ydl_fallback:
                        info = ydl_fallback.extract_info(url, download=True)
                        filename = ydl_fallback.prepare_filename(info)
                        return filename
                except Exception:
                    raise DownloadError(f"Failed to download video with fallback format: {error_msg}")
            else:
                raise DownloadError(f"Failed to download video: {error_msg}")
        except Exception as e:
            raise DownloadError(f"Failed to download video: {str(e)}")
    
    def download_playlist(self, url: str) -> List[str]:
        """Download all videos from a YouTube playlist with range filtering"""
        try:
            # Normalize playlist URL
            normalized_url = self._normalize_playlist_url(url)
            
            # Get playlist information
            videos = self.get_playlist_info(normalized_url)
            
            if not videos:
                print("No videos found in playlist")
                return []
            
            print(f"Found {len(videos)} videos in playlist")
            
            # Apply range filtering
            filtered_videos = self._filter_playlist_by_range(videos)
            
            if not filtered_videos:
                print("No videos to download after applying filters")
                return []
            
            print(f"Downloading {len(filtered_videos)} videos (filtered from {len(videos)} total)")
            
            downloaded_files = []
            
            for i, video in enumerate(filtered_videos, 1):
                try:
                    print(f"\nDownloading video {i}/{len(filtered_videos)}: {video.title}")
                    filename = self.download_video(video.url)
                    downloaded_files.append(filename)
                except Exception as e:
                    print(f"Failed to download video '{video.title}': {str(e)}")
                    continue
            
            return downloaded_files
            
        except Exception as e:
            raise DownloadError(f"Failed to download playlist: {str(e)}")
    
    def is_playlist(self, url: str) -> bool:
        """Check if the URL is a YouTube playlist"""
        playlist_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=',
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*list=',
        ]
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in playlist_patterns)
