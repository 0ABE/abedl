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
Command-line interface for ABEDL video downloader.
"""

import click
import sys
from pathlib import Path
from typing import List

from .base import DownloadOptions, DownloadError
from .registry import get_downloader_for_url, registry


@click.group()
@click.version_option(version='1.0.0', prog_name='ABEDL')
def cli():
    """ABEDL - Abe's Extensible Downloader
    
    A modular video downloader supporting multiple platforms.
    """
    pass


@cli.command()
@click.argument('url')
@click.option('--output-dir', '-o', default='./downloads', 
              help='Output directory for downloaded files')
@click.option('--quality', '-q', default='best',
              help='Video quality (best, worst, 720p, 1080p, etc.)')
@click.option('--audio-only', '-a', is_flag=True,
              help='Download audio only')
@click.option('--audio-format', default=None,
              help='Audio format for audio-only downloads (mp3, wav, etc.)')
@click.option('--video-format', default=None,
              help='Preferred video format (mp4, webm, etc.)')
@click.option('--subtitles', '-s', is_flag=True,
              help='Download subtitles')
@click.option('--embed-subtitles', is_flag=True,
              help='Embed subtitles in video file')
@click.option('--write-info', is_flag=True,
              help='Write video info to JSON file')
@click.option('--write-thumbnail', is_flag=True,
              help='Write thumbnail image')
@click.option('--playlist-start', type=int, default=1,
              help='Playlist video to start at (default: 1)')
@click.option('--playlist-end', type=int, default=None,
              help='Playlist video to end at (default: last video)')
@click.option('--playlist-items', default=None,
              help='Playlist video indices to download (e.g., "1,3,5-8,10")')
@click.option('--cookies-from-browser', default=None,
              help='Extract cookies from browser (e.g., "chrome", "firefox", "safari")')
@click.option('--cookies', default=None,
              help='Path to cookies file in Netscape format')
def download(url: str, output_dir: str, quality: str, audio_only: bool,
             audio_format: str, video_format: str, subtitles: bool,
             embed_subtitles: bool, write_info: bool, write_thumbnail: bool,
             playlist_start: int, playlist_end: int, playlist_items: str,
             cookies_from_browser: str, cookies: str):
    """Download a video or playlist from a URL"""
    
    # Create download options
    options = DownloadOptions(
        output_dir=output_dir,
        quality=quality,
        audio_only=audio_only,
        audio_format=audio_format,
        video_format=video_format,
        subtitles=subtitles,
        embed_subtitles=embed_subtitles,
        write_info_json=write_info,
        write_thumbnail=write_thumbnail,
        playlist_start=playlist_start,
        playlist_end=playlist_end,
        playlist_items=playlist_items,
        cookies_from_browser=cookies_from_browser,
        cookies=cookies
    )
    
    try:
        # Get appropriate downloader
        click.echo(f"Finding downloader for URL: {url}")
        downloader = get_downloader_for_url(url, options)
        
        # Download the content
        click.echo(f"Starting download to: {output_dir}")
        downloaded_files = downloader.download(url)
        
        # Report results
        if downloaded_files:
            click.echo(f"\n✓ Successfully downloaded {len(downloaded_files)} file(s):")
            for file_path in downloaded_files:
                click.echo(f"  • {file_path}")
        else:
            click.echo(f"\n⚠️  No files were downloaded. Check the URL and try again.")
            sys.exit(1)
            
    except DownloadError as e:
        click.echo(f"❌ Download failed: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('url')
def info(url: str):
    """Get information about a video or playlist without downloading"""
    
    try:
        # Create minimal options for info extraction
        options = DownloadOptions()
        downloader = get_downloader_for_url(url, options)
        
        if downloader.is_playlist(url):
            click.echo("📋 Playlist Information:")
            videos = downloader.get_playlist_info(url)
            click.echo(f"Total videos: {len(videos)}")
            click.echo("\nVideos:")
            for i, video in enumerate(videos, 1):
                duration = f" ({video.duration}s)" if video.duration else ""
                click.echo(f"  {i:2d}. {video.title}{duration}")
                if video.uploader:
                    click.echo(f"      by {video.uploader}")
        else:
            click.echo("🎥 Video Information:")
            video = downloader.get_video_info(url)
            click.echo(f"Title: {video.title}")
            if video.uploader:
                click.echo(f"Uploader: {video.uploader}")
            if video.duration:
                click.echo(f"Duration: {video.duration} seconds")
            if video.view_count:
                click.echo(f"Views: {video.view_count:,}")
            if video.upload_date:
                click.echo(f"Upload Date: {video.upload_date}")
            if video.description:
                # Show first 200 characters of description
                desc = video.description[:200] + "..." if len(video.description) > 200 else video.description
                click.echo(f"Description: {desc}")
                
    except DownloadError as e:
        click.echo(f"❌ Failed to get info: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('url')
def formats(url: str):
    """List available formats for a video URL"""
    
    try:
        # Create minimal options for format listing
        options = DownloadOptions()
        downloader = get_downloader_for_url(url, options)
        
        if not downloader.is_playlist(url):
            click.echo("📋 Available Formats:")
            
            # Use yt-dlp directly to list formats
            import yt_dlp
            
            ydl_opts = {
                'listformats': True,
                'quiet': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=False)
        else:
            click.echo("📋 Playlist detected. Use 'info' command to see playlist contents.")
            
    except DownloadError as e:
        click.echo(f"❌ Failed to list formats: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
def platforms():
    """List supported platforms and example URLs"""
    
    click.echo("🌐 Supported Platforms:")
    supported = registry.get_supported_platforms()
    
    if not supported:
        click.echo("No downloaders registered.")
        return
    
    for platform, examples in supported.items():
        click.echo(f"\n{platform.upper()}:")
        for example in examples:
            click.echo(f"  • {example}")


@cli.command()
def test():
    """Test the installation and available downloaders"""
    
    click.echo("🔧 Testing ABEDL Installation...")
    
    # Test registry
    downloaders = registry.list_downloaders()
    click.echo(f"✓ Registry loaded with {len(downloaders)} downloader(s): {', '.join(downloaders)}")
    
    # Test dependencies
    try:
        import yt_dlp
        click.echo("✓ yt-dlp is available")
    except ImportError:
        click.echo("❌ yt-dlp is not installed (required for YouTube downloads)")
    
    try:
        import requests
        click.echo("✓ requests is available")
    except ImportError:
        click.echo("❌ requests is not installed")
    
    # Test ffmpeg
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            click.echo(f"✓ ffmpeg is available: {version_line}")
        else:
            click.echo("⚠️  ffmpeg found but may have issues")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        click.echo("⚠️  ffmpeg not found (recommended for full functionality)")
        click.echo("   Install: brew install ffmpeg (macOS) or apt install ffmpeg (Ubuntu)")
    except Exception as e:
        click.echo(f"⚠️  ffmpeg check failed: {e}")
    
    click.echo("\n🎉 Installation test complete!")


if __name__ == '__main__':
    cli()
