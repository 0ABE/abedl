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
Base downloader class that defines the interface for all video platform downloaders.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VideoInfo:
    """Data class to hold video information"""
    title: str
    url: str
    duration: Optional[int] = None
    description: Optional[str] = None
    uploader: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    thumbnail_url: Optional[str] = None


@dataclass
class DownloadOptions:
    """Data class to hold download configuration"""
    output_dir: str = "./downloads"
    quality: str = "best"  # best, worst, or specific format
    audio_only: bool = False
    video_format: Optional[str] = None  # mp4, webm, etc.
    audio_format: Optional[str] = None  # mp3, wav, etc.
    subtitles: bool = False
    embed_subtitles: bool = False
    write_info_json: bool = False
    write_thumbnail: bool = False
    playlist_start: int = 1
    playlist_end: Optional[int] = None
    playlist_items: Optional[str] = None
    cookies_from_browser: Optional[str] = None  # chrome, firefox, safari, etc.
    cookies: Optional[str] = None  # path to cookies file


class BaseDownloader(ABC):
    """
    Abstract base class for all video platform downloaders.
    
    Each platform-specific downloader should inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, options: DownloadOptions):
        self.options = options
        self._ensure_output_dir()
    
    def _ensure_output_dir(self) -> None:
        """Ensure the output directory exists"""
        Path(self.options.output_dir).mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """
        Check if this downloader can handle the given URL.
        
        Args:
            url: The video or playlist URL
            
        Returns:
            bool: True if this downloader can handle the URL
        """
        pass
    
    @abstractmethod
    def get_video_info(self, url: str) -> VideoInfo:
        """
        Extract video information from the URL.
        
        Args:
            url: The video URL
            
        Returns:
            VideoInfo: Information about the video
            
        Raises:
            DownloadError: If unable to extract video information
        """
        pass
    
    @abstractmethod
    def get_playlist_info(self, url: str) -> List[VideoInfo]:
        """
        Extract playlist information from the URL.
        
        Args:
            url: The playlist URL
            
        Returns:
            List[VideoInfo]: List of videos in the playlist
            
        Raises:
            DownloadError: If unable to extract playlist information
        """
        pass
    
    @abstractmethod
    def download_video(self, url: str) -> str:
        """
        Download a single video.
        
        Args:
            url: The video URL
            
        Returns:
            str: Path to the downloaded file
            
        Raises:
            DownloadError: If download fails
        """
        pass
    
    @abstractmethod
    def download_playlist(self, url: str) -> List[str]:
        """
        Download all videos in a playlist.
        
        Args:
            url: The playlist URL
            
        Returns:
            List[str]: Paths to the downloaded files
            
        Raises:
            DownloadError: If download fails
        """
        pass
    
    def is_playlist(self, url: str) -> bool:
        """
        Check if the URL is a playlist.
        
        Args:
            url: The URL to check
            
        Returns:
            bool: True if the URL is a playlist
        """
        # Default implementation - subclasses can override
        return "playlist" in url.lower() or "list=" in url
    
    def download(self, url: str) -> List[str]:
        """
        Download video(s) from the given URL.
        
        This is the main entry point that determines whether to download
        a single video or a playlist.
        
        Args:
            url: The video or playlist URL
            
        Returns:
            List[str]: Paths to the downloaded files
        """
        if self.is_playlist(url):
            return self.download_playlist(url)
        else:
            return [self.download_video(url)]


class DownloadError(Exception):
    """Exception raised when download operations fail"""
    pass
