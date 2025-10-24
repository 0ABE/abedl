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
Test script for playlist range functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from abedl.base import DownloadOptions
from abedl.youtube import YouTubeDownloader

def test_playlist_items_parsing():
    """Test the _parse_playlist_items method"""
    options = DownloadOptions()
    downloader = YouTubeDownloader(options)
    
    # Test cases
    test_cases = [
        ("1,3,5", [1, 3, 5]),
        ("1-3", [1, 2, 3]),
        ("1,3,5-7,10", [1, 3, 5, 6, 7, 10]),
        ("5-8,1,3", [1, 3, 5, 6, 7, 8]),  # Should be sorted and deduplicated
        ("", []),
        ("1,invalid,3", [1, 3]),  # Should skip invalid entries
    ]
    
    print("Testing playlist items parsing:")
    for input_str, expected in test_cases:
        result = downloader._parse_playlist_items(input_str)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_str}' -> {result} (expected: {expected})")

def test_playlist_filtering():
    """Test playlist filtering with mock video data"""
    from abedl.base import VideoInfo
    
    # Create mock videos
    videos = [
        VideoInfo(f"https://youtube.com/watch?v=video{i}", f"Video {i}", f"Mock video {i}")
        for i in range(1, 11)  # 10 videos
    ]
    
    print(f"\nTesting playlist filtering with {len(videos)} mock videos:")
    
    # Test different filtering options
    test_cases = [
        {"playlist_start": 3, "playlist_end": 6, "playlist_items": None, "expected_count": 4},
        {"playlist_start": 1, "playlist_end": None, "playlist_items": "1,3,5", "expected_count": 3},
        {"playlist_start": 1, "playlist_end": None, "playlist_items": "1-3,8-10", "expected_count": 6},
        {"playlist_start": 5, "playlist_end": 8, "playlist_items": None, "expected_count": 4},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        options = DownloadOptions(
            playlist_start=test_case["playlist_start"],
            playlist_end=test_case["playlist_end"],
            playlist_items=test_case["playlist_items"]
        )
        downloader = YouTubeDownloader(options)
        
        filtered = downloader._filter_playlist_by_range(videos)
        actual_count = len(filtered)
        expected_count = test_case["expected_count"]
        
        status = "✓" if actual_count == expected_count else "✗"
        print(f"  {status} Test {i}: Got {actual_count} videos (expected: {expected_count})")
        
        if test_case["playlist_items"]:
            print(f"      Items: {test_case['playlist_items']}")
        else:
            print(f"      Range: {test_case['playlist_start']}-{test_case['playlist_end'] or 'end'}")
        
        if filtered:
            titles = [v.title for v in filtered[:3]]  # Show first 3
            if len(filtered) > 3:
                titles.append("...")
            print(f"      Videos: {', '.join(titles)}")

if __name__ == "__main__":
    test_playlist_items_parsing()
    test_playlist_filtering()
    print("\nPlaylist range functionality test completed!")
