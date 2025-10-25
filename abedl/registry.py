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
Downloader registry for managing multiple video platform downloaders.
"""

from typing import Dict, List, Type, Optional
from .base import BaseDownloader, DownloadOptions, DownloadError


class DownloaderRegistry:
    """Registry for managing different video platform downloaders"""
    
    def __init__(self):
        self._downloaders: Dict[str, Type[BaseDownloader]] = {}
    
    def register(self, name: str, downloader_class: Type[BaseDownloader]) -> None:
        """
        Register a downloader class.
        
        Args:
            name: Name identifier for the downloader
            downloader_class: The downloader class to register
        """
        self._downloaders[name] = downloader_class
    
    def unregister(self, name: str) -> None:
        """
        Unregister a downloader.
        
        Args:
            name: Name identifier of the downloader to remove
        """
        if name in self._downloaders:
            del self._downloaders[name]
    
    def get_downloader_for_url(self, url: str, options: DownloadOptions) -> BaseDownloader:
        """
        Get the appropriate downloader for a given URL.
        
        Args:
            url: The video or playlist URL
            options: Download configuration options
            
        Returns:
            BaseDownloader: An instance of the appropriate downloader
            
        Raises:
            DownloadError: If no suitable downloader is found
        """
        for name, downloader_class in self._downloaders.items():
            downloader = downloader_class(options)
            if downloader.can_handle(url):
                return downloader
        
        raise DownloadError(f"No downloader found for URL: {url}")
    
    def list_downloaders(self) -> List[str]:
        """
        Get a list of registered downloader names.
        
        Returns:
            List[str]: Names of registered downloaders
        """
        return list(self._downloaders.keys())
    
    def get_supported_platforms(self) -> Dict[str, List[str]]:
        """
        Get information about supported platforms and their URL patterns.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping downloader names to example URLs
        """
        platforms = {}
        for name, downloader_class in self._downloaders.items():
            # Create a temporary instance to check URL patterns
            temp_downloader = downloader_class(DownloadOptions())
            
            # Add some example URLs based on the downloader name
            if name.lower() == 'youtube':
                platforms[name] = [
                    'https://www.youtube.com/watch?v=VIDEO_ID',
                    'https://www.youtube.com/playlist?list=PLAYLIST_ID',
                    'https://youtu.be/VIDEO_ID'
                ]
            elif name.lower() == 'cbn':
                platforms[name] = [
                    'https://cbn.com/video/flying-house-episode-1',
                    'https://cbn.com/video/flying-house-episode-number',
                ]
            else:
                platforms[name] = ['Platform-specific URLs']
        
        return platforms


# Global registry instance
registry = DownloaderRegistry()


def register_downloader(name: str, downloader_class: Type[BaseDownloader]) -> None:
    """
    Convenience function to register a downloader with the global registry.
    
    Args:
        name: Name identifier for the downloader
        downloader_class: The downloader class to register
    """
    registry.register(name, downloader_class)


def get_downloader_for_url(url: str, options: DownloadOptions) -> BaseDownloader:
    """
    Convenience function to get a downloader from the global registry.
    
    Args:
        url: The video or playlist URL
        options: Download configuration options
        
    Returns:
        BaseDownloader: An instance of the appropriate downloader
    """
    return registry.get_downloader_for_url(url, options)


# Register built-in downloaders
def _register_builtin_downloaders():
    """Register all built-in downloaders"""
    try:
        from .youtube import YouTubeDownloader
        register_downloader('youtube', YouTubeDownloader)
    except ImportError:
        print("Warning: YouTube downloader not available (yt-dlp not installed)")
    
    try:
        from .cbn import CBNDownloader
        register_downloader('cbn', CBNDownloader)
    except ImportError:
        print("Warning: CBN downloader not available (yt-dlp not installed)")


# Auto-register built-in downloaders when module is imported
_register_builtin_downloaders()
