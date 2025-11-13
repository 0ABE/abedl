#!/usr/bin/env python3
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
Simple test script for CBN downloader functionality.
"""

import sys
import os

# Add the abedl package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abedl.base import DownloadOptions
from abedl.cbn import CBNDownloader

def test_cbn_url_matching():
    """Test that CBN URLs are properly recognized"""
    print("Testing CBN URL matching...")
    
    options = DownloadOptions()
    downloader = CBNDownloader(options)
    
    # Test URLs
    test_urls = [
        "https://cbn.com/video/flying-house-episode-1",
        "https://www.cbn.com/video/flying-house-episode-25",
        "https://cbn.com/video/some-other-video",
        "https://cbn.com/shows/superbook/episode-1",
        "https://youtube.com/watch?v=test",  # Should NOT match
        "https://example.com/video"  # Should NOT match
    ]
    
    for url in test_urls:
        can_handle = downloader.can_handle(url)
        print(f"  {url} -> {'✓' if can_handle else '✗'}")
        
        # CBN URLs should match, others should not
        expected = "cbn.com" in url
        if can_handle == expected:
            print(f"    PASS")
        else:
            print(f"    FAIL (expected {expected})")

def test_cbn_registry():
    """Test that CBN downloader is registered"""
    print("\nTesting CBN downloader registration...")
    
    from abedl.registry import registry
    
    # Check if CBN is in the registry
    platforms = registry.get_supported_platforms()
    
    if 'cbn' in platforms:
        print("  ✓ CBN downloader is registered")
        print(f"  Example URLs: {platforms['cbn']}")
    else:
        print("  ✗ CBN downloader is NOT registered")
    
    # Test getting downloader for CBN URL
    try:
        options = DownloadOptions()
        downloader = registry.get_downloader_for_url("https://cbn.com/video/test", options)
        print(f"  ✓ Registry returns {type(downloader).__name__} for CBN URL")
    except Exception as e:
        print(f"  ✗ Failed to get downloader: {e}")

if __name__ == "__main__":
    print("CBN Downloader Test Suite")
    print("=" * 40)
    
    test_cbn_url_matching()
    test_cbn_registry()
    
    print("\nTest completed!")