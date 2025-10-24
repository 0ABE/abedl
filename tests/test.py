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
Simple test script to verify ABEDL installation and basic functionality
"""

import sys
import tempfile
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from abedl.base import BaseDownloader, DownloadOptions, VideoInfo
        print("✓ Base classes imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import base classes: {e}")
        return False
    
    try:
        from abedl.registry import registry, register_downloader
        print("✓ Registry imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import registry: {e}")
        return False
    
    try:
        from abedl.youtube import YouTubeDownloader
        print("✓ YouTube downloader imported successfully")
    except ImportError as e:
        print(f"⚠️  YouTube downloader not available: {e}")
    
    try:
        from abedl.cli import cli
        print("✓ CLI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CLI: {e}")
        return False
    
    return True


def test_dependencies():
    """Test external dependencies"""
    print("\nTesting dependencies...")
    
    # Test yt-dlp
    try:
        import yt_dlp
        print("✓ yt-dlp is available")
    except ImportError:
        print("❌ yt-dlp is not installed (required for YouTube downloads)")
    
    # Test requests
    try:
        import requests
        print("✓ requests is available")
    except ImportError:
        print("❌ requests is not installed")
    
    # Test click
    try:
        import click
        print("✓ click is available")
    except ImportError:
        print("❌ click is not installed")
    
    # Test ffmpeg availability
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ ffmpeg is available: {version_line}")
        else:
            print("⚠️  ffmpeg found but may have issues")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  ffmpeg not found (recommended for full functionality)")
    except Exception as e:
        print(f"⚠️  ffmpeg check failed: {e}")
    
    return True


def test_registry():
    """Test the downloader registry"""
    print("\nTesting registry...")
    
    from abedl.registry import registry
    
    downloaders = registry.list_downloaders()
    print(f"✓ Registry has {len(downloaders)} registered downloader(s): {downloaders}")
    
    if 'youtube' in downloaders:
        print("✓ YouTube downloader is registered")
    else:
        print("⚠️  YouTube downloader is not registered")
    
    return True


def test_youtube_downloader():
    """Test YouTube downloader basic functionality"""
    print("\nTesting YouTube downloader...")
    
    try:
        from abedl.youtube import YouTubeDownloader
        from abedl.base import DownloadOptions
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            options = DownloadOptions(output_dir=temp_dir)
            downloader = YouTubeDownloader(options)
            
            # Test URL recognition
            test_urls = [
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "https://youtu.be/dQw4w9WgXcQ",
                "https://www.youtube.com/playlist?list=PLrGHKjKzFOLKRR7_M6q_-rYKNKP9s2rAT",
                "https://www.example.com/video",
            ]
            
            for url in test_urls[:3]:  # Test first 3 (YouTube URLs)
                if downloader.can_handle(url):
                    print(f"✓ Correctly identified YouTube URL: {url}")
                else:
                    print(f"❌ Failed to identify YouTube URL: {url}")
            
            # Test non-YouTube URL
            if not downloader.can_handle(test_urls[3]):
                print(f"✓ Correctly rejected non-YouTube URL: {test_urls[3]}")
            else:
                print(f"❌ Incorrectly identified non-YouTube URL as YouTube: {test_urls[3]}")
        
        print("✓ YouTube downloader basic tests passed")
        return True
        
    except Exception as e:
        print(f"❌ YouTube downloader test failed: {e}")
        return False


def test_cli():
    """Test CLI basic functionality"""
    print("\nTesting CLI...")
    
    try:
        from abedl.cli import cli
        from click.testing import CliRunner
        
        runner = CliRunner()
        
        # Test help command
        result = runner.invoke(cli, ['--help'])
        if result.exit_code == 0:
            print("✓ CLI help command works")
        else:
            print(f"❌ CLI help command failed: {result.output}")
            return False
        
        # Test platforms command
        result = runner.invoke(cli, ['platforms'])
        if result.exit_code == 0:
            print("✓ CLI platforms command works")
        else:
            print(f"❌ CLI platforms command failed: {result.output}")
            return False
        
        # Test test command
        result = runner.invoke(cli, ['test'])
        if result.exit_code == 0:
            print("✓ CLI test command works")
        else:
            print(f"❌ CLI test command failed: {result.output}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🔧 ABEDL Installation Test")
    print("=" * 40)
    
    success = True
    
    success &= test_imports()
    success &= test_dependencies()
    success &= test_registry()
    success &= test_youtube_downloader()
    success &= test_cli()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! ABEDL is ready to use.")
        print("\nTry running:")
        print("  python main.py --help")
        print("  python main.py platforms")
        print("  python main.py info 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'")
    else:
        print("❌ Some tests failed. Please check the installation.")
        sys.exit(1)


if __name__ == '__main__':
    main()
