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
Example implementation of a custom downloader for a hypothetical platform.

This demonstrates how to extend ABEDL to support new video platforms.
"""

import re
import requests
from typing import List
from pathlib import Path

from abedl.base import BaseDownloader, VideoInfo, DownloadOptions, DownloadError


class ExamplePlatformDownloader(BaseDownloader):
    """
    Example downloader for a hypothetical video platform.
    
    This shows the basic structure and required methods for implementing
    a new platform downloader.
    """
    
    # Define URL patterns that this downloader can handle
    PLATFORM_PATTERNS = [
        r'(?:https?://)?(?:www\.)?example\.com/video/[\w-]+',
        r'(?:https?://)?(?:www\.)?example\.com/playlist/[\w-]+',
    ]
    
    def can_handle(self, url: str) -> bool:
        """Check if this downloader can handle the given URL"""
        return any(re.match(pattern, url, re.IGNORECASE) for pattern in self.PLATFORM_PATTERNS)
    
    def get_video_info(self, url: str) -> VideoInfo:
        """Extract video information from the platform's API or page"""
        try:
            # In a real implementation, you would:
            # 1. Make HTTP requests to get video metadata
            # 2. Parse HTML or JSON responses
            # 3. Extract video information
            
            # Example implementation (mock):
            video_id = self._extract_video_id(url)
            
            # Simulate API call
            response = self._make_api_request(f"/api/video/{video_id}")
            
            return VideoInfo(
                title=response.get('title', 'Unknown Title'),
                url=url,
                duration=response.get('duration'),
                description=response.get('description'),
                uploader=response.get('uploader'),
                view_count=response.get('view_count')
            )
            
        except Exception as e:
            raise DownloadError(f"Failed to extract video info: {str(e)}")
    
    def get_playlist_info(self, url: str) -> List[VideoInfo]:
        """Extract playlist information"""
        try:
            playlist_id = self._extract_playlist_id(url)
            response = self._make_api_request(f"/api/playlist/{playlist_id}")
            
            videos = []
            for video_data in response.get('videos', []):
                videos.append(VideoInfo(
                    title=video_data.get('title', 'Unknown Title'),
                    url=video_data.get('url', ''),
                    duration=video_data.get('duration'),
                    uploader=video_data.get('uploader')
                ))
            
            return videos
            
        except Exception as e:
            raise DownloadError(f"Failed to extract playlist info: {str(e)}")
    
    def download_video(self, url: str) -> str:
        """Download a single video"""
        try:
            # Get video information and download URL
            video_info = self.get_video_info(url)
            download_url = self._get_download_url(url)
            
            # Create filename
            filename = self._sanitize_filename(video_info.title) + ".mp4"
            filepath = Path(self.options.output_dir) / filename
            
            # Download the file
            self._download_file(download_url, filepath)
            
            return str(filepath)
            
        except Exception as e:
            raise DownloadError(f"Failed to download video: {str(e)}")
    
    def download_playlist(self, url: str) -> List[str]:
        """Download all videos in a playlist"""
        try:
            videos = self.get_playlist_info(url)
            downloaded_files = []
            
            for video in videos:
                try:
                    filepath = self.download_video(video.url)
                    downloaded_files.append(filepath)
                except DownloadError as e:
                    print(f"Warning: Failed to download '{video.title}': {e}")
                    continue
            
            return downloaded_files
            
        except Exception as e:
            raise DownloadError(f"Failed to download playlist: {str(e)}")
    
    def is_playlist(self, url: str) -> bool:
        """Check if the URL is a playlist"""
        return "/playlist/" in url
    
    # Helper methods
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from URL"""
        match = re.search(r'/video/([\w-]+)', url)
        if match:
            return match.group(1)
        raise DownloadError("Invalid video URL")
    
    def _extract_playlist_id(self, url: str) -> str:
        """Extract playlist ID from URL"""
        match = re.search(r'/playlist/([\w-]+)', url)
        if match:
            return match.group(1)
        raise DownloadError("Invalid playlist URL")
    
    def _make_api_request(self, endpoint: str) -> dict:
        """Make a request to the platform's API"""
        # In a real implementation, this would make actual HTTP requests
        # to the platform's API endpoints
        
        # Mock response for demonstration
        if "/video/" in endpoint:
            return {
                'title': 'Example Video Title',
                'duration': 300,
                'description': 'Example video description',
                'uploader': 'Example User',
                'view_count': 1000
            }
        elif "/playlist/" in endpoint:
            return {
                'videos': [
                    {
                        'title': 'Video 1',
                        'url': 'https://example.com/video/1',
                        'duration': 180
                    },
                    {
                        'title': 'Video 2',
                        'url': 'https://example.com/video/2',
                        'duration': 240
                    }
                ]
            }
        
        return {}
    
    def _get_download_url(self, video_url: str) -> str:
        """Get the direct download URL for a video"""
        # In a real implementation, this would:
        # 1. Parse the video page or make API calls
        # 2. Extract the direct download links
        # 3. Select the appropriate quality/format
        
        # Mock implementation
        return "https://example.com/download/video.mp4"
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def _download_file(self, url: str, filepath: Path) -> None:
        """Download a file from URL to filepath"""
        # In a real implementation, you would use requests or similar
        # to download the file with proper progress tracking
        
        # Mock implementation
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text("Mock video content")


# Example of how to register the custom downloader
if __name__ == "__main__":
    from abedl.registry import register_downloader
    from abedl.base import DownloadOptions
    
    # Register the custom downloader
    register_downloader('example', ExamplePlatformDownloader)
    
    # Test the downloader
    options = DownloadOptions(output_dir="./test_downloads")
    downloader = ExamplePlatformDownloader(options)
    
    print("Testing custom downloader...")
    print(f"Can handle example.com URL: {downloader.can_handle('https://example.com/video/test123')}")
    print(f"Can handle YouTube URL: {downloader.can_handle('https://youtube.com/watch?v=test')}")
