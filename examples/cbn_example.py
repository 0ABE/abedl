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
Example usage of ABEDL with CBN downloader.
Demonstrates how to download videos from cbn.com using the plugin architecture.
"""

import sys
import os

# Add the abedl package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abedl.base import DownloadOptions, DownloadError
from abedl.registry import get_downloader_for_url

def download_cbn_video(url, output_dir="./downloads"):
    """
    Example function to download a CBN video.
    
    Args:
        url: CBN video URL (e.g., https://cbn.com/video/flying-house-episode-1)
        output_dir: Directory to save the downloaded video
    """
    print(f"Downloading CBN video: {url}")
    
    try:
        # Create download options
        options = DownloadOptions(
            output_dir=output_dir,
            quality="best",
            write_info_json=True,  # Save video metadata
            write_thumbnail=True   # Save video thumbnail
        )
        
        # Get the appropriate downloader (should be CBN downloader)
        downloader = get_downloader_for_url(url, options)
        print(f"Using downloader: {type(downloader).__name__}")
        
        # Get video information first
        print("Extracting video information...")
        video_info = downloader.get_video_info(url)
        print(f"Title: {video_info.title}")
        print(f"Uploader: {video_info.uploader}")
        if video_info.duration:
            print(f"Duration: {video_info.duration} seconds")
        
        # Download the video
        print("Starting download...")
        downloaded_files = downloader.download(url)
        
        print("Download completed!")
        for file_path in downloaded_files:
            print(f"Downloaded: {file_path}")
            
    except DownloadError as e:
        print(f"Download failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    print("CBN Downloader Example")
    print("=" * 30)
    
    # Example CBN URLs
    example_urls = [
        "https://cbn.com/video/flying-house-episode-1",
        # Add more example URLs here
    ]
    
    print("\nExample CBN URLs you can try:")
    for url in example_urls:
        print(f"  {url}")
    
    print("\nNote: This example uses placeholder URLs.")
    print("Replace with actual CBN video URLs to test downloads.")
    
    # Uncomment the following lines to test with a real URL
    # test_url = "https://cbn.com/video/flying-house-episode-1"
    # download_cbn_video(test_url)

if __name__ == "__main__":
    main()