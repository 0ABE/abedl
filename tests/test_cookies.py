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
Test script for cookie functionality and bot detection handling
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from abedl.base import DownloadOptions
from abedl.youtube import YouTubeDownloader

def test_cookie_options():
    """Test that cookie options are properly configured"""
    
    print("Testing cookie configuration options...")
    
    # Test with cookies from browser
    options_browser = DownloadOptions(
        output_dir="./test_downloads",
        cookies_from_browser="chrome"
    )
    
    downloader_browser = YouTubeDownloader(options_browser)
    print("✓ Cookies from browser option configured")
    
    # Test with cookies file
    options_file = DownloadOptions(
        output_dir="./test_downloads", 
        cookies="./cookies.txt"
    )
    
    downloader_file = YouTubeDownloader(options_file)
    print("✓ Cookies file option configured")
    
    # Check that ydl_opts contains cookie settings
    if hasattr(downloader_browser, 'ydl_opts'):
        if 'cookiesfrombrowser' in downloader_browser.ydl_opts:
            print("✓ Browser cookies configured in yt-dlp options")
        else:
            print("✗ Browser cookies not found in yt-dlp options")
    
    if hasattr(downloader_file, 'ydl_opts'):
        if 'cookiefile' in downloader_file.ydl_opts:
            print("✓ Cookie file configured in yt-dlp options")
        else:
            print("✗ Cookie file not found in yt-dlp options")

def test_anti_bot_measures():
    """Test that anti-bot measures are configured"""
    
    print("\nTesting anti-bot detection measures...")
    
    options = DownloadOptions(output_dir="./test_downloads")
    downloader = YouTubeDownloader(options)
    
    # Check user agent
    if 'http_headers' in downloader.ydl_opts:
        user_agent = downloader.ydl_opts['http_headers'].get('User-Agent', '')
        if 'Chrome' in user_agent:
            print("✓ Realistic user agent configured")
        else:
            print(f"✗ User agent not realistic: {user_agent}")
    else:
        print("✗ No HTTP headers configured")
    
    # Check retry configuration
    if 'extractor_retries' in downloader.ydl_opts:
        print(f"✓ Extractor retries: {downloader.ydl_opts['extractor_retries']}")
    else:
        print("✗ No extractor retries configured")
    
    if 'fragment_retries' in downloader.ydl_opts:
        print(f"✓ Fragment retries: {downloader.ydl_opts['fragment_retries']}")
    else:
        print("✗ No fragment retries configured")

def print_usage_examples():
    """Print usage examples for cookie authentication"""
    
    print("\n" + "="*50)
    print("USAGE EXAMPLES FOR COOKIE AUTHENTICATION")
    print("="*50)
    
    print("\n1. Browser Cookies (Automatic):")
    print("   python main.py download --cookies-from-browser chrome \"VIDEO_URL\"")
    print("   python main.py download --cookies-from-browser firefox \"VIDEO_URL\"")
    print("   python main.py download --cookies-from-browser safari \"VIDEO_URL\"")
    
    print("\n2. Manual Cookie File:")
    print("   python main.py download --cookies ./youtube_cookies.txt \"VIDEO_URL\"")
    
    print("\n3. Combined with Other Options:")
    print("   python main.py download \\")
    print("     --cookies-from-browser chrome \\")
    print("     --quality 720p \\")
    print("     --playlist-items \"1-5\" \\")
    print("     \"PLAYLIST_URL\"")

if __name__ == "__main__":
    test_cookie_options()
    test_anti_bot_measures()
    print_usage_examples()
    print("\n✅ Cookie functionality test completed!")
