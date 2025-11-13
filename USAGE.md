# ABEDL Usage Examples

This document shows examples of how to use ABEDL for various video download scenarios.

## Table of Contents
- [Basic Downloads](#basic-downloads)
- [Keys for Kids Devotional Downloads](#keys-for-kids-devotional-downloads)
- [Audio Downloads](#audio-downloads-requires-ffmpeg)
- [Bot Detection and Cookie Authentication](#bot-detection-and-cookie-authentication)
- [Format Conversion](#format-conversion-requires-ffmpeg)
- [Playlist Downloads](#playlist-downloads)
- [Playlist Range Selection](#playlist-range-selection)
- [Advanced Options](#advanced-options)
- [Playlist Range Parameters Reference](#playlist-range-parameters-reference)
- [Custom Output Directory](#custom-output-directory)
- [Information Only](#information-only-no-download)
- [ffmpeg Features](#why-ffmpeg-is-important)
- [Troubleshooting](#troubleshooting)

## Basic Downloads

### Download best quality video
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download specific quality
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID" --quality 720p
```

## Keys for Kids Devotional Downloads

ABEDL supports downloading daily devotional audio files from Keys for Kids (keysforkids.org).

### Quick Command Reference
```bash
# Download today's devotional
python main.py keysforkids

# Download specific date
python main.py keysforkids --date 2025-11-09

# Download last 7 days
python main.py keysforkids --last-days 7

# Download date range
python main.py keysforkids --start-date 2025-11-07 --end-date 2025-11-09
```

### Download today's devotional
```bash
python main.py keysforkids
```

### Download specific devotional by URL
```bash
python main.py download "https://www.keysforkids.org/podcast/keys-for-kids/forgive-us-our-diets-2/"
```

### Download to custom directory
```bash
python main.py download "https://www.keysforkids.org/devotional/" --output-dir ~/Music/Devotionals
```

### Download by date (easy CLI commands)
```bash
# Download today's devotional
python main.py keysforkids

# Download devotional from a specific date
python main.py keysforkids --date 2025-11-09

# Download devotionals from last 7 days
python main.py keysforkids --last-days 7

# Download devotionals for a date range
python main.py keysforkids --start-date 2025-11-07 --end-date 2025-11-09

# Download to a custom directory
python main.py keysforkids --date 2025-11-09 --output-dir ~/Music/Devotionals
```

### Advanced: Python API for date-based downloads
```bash
# Download devotional from a specific date using Python directly
python -c "
from abedl.keysforkids import KeysForKidsDownloader
from datetime import datetime

# Download devotional from November 9, 2025
date = datetime(2025, 11, 9)
KeysForKidsDownloader.download_by_date(date)
"

# Download devotionals for a date range using Python directly
python -c "
from abedl.keysforkids import KeysForKidsDownloader
from datetime import datetime

# Download devotionals from Nov 7-9, 2025
start = datetime(2025, 11, 7)
end = datetime(2025, 11, 9)
KeysForKidsDownloader.download_date_range(start, end)
"

# Get devotional URL for a specific date
python -c "
from abedl.keysforkids import KeysForKidsDownloader
from datetime import datetime

date = datetime(2025, 11, 9)
url = KeysForKidsDownloader.get_devotional_url_by_date(date)
print(url)
"
```

### Get devotional information without downloading
```bash
python main.py info "https://www.keysforkids.org/podcast/keys-for-kids/forgive-us-our-diets-2/"
```

**Output format**: Files are automatically named with the date and title:
```
November 10, 2025_Forgive_Us_Our_Diets.mp3
```

**Supported URL formats**:
- Today's devotional: `https://www.keysforkids.org/devotional/`
- Specific devotional: `https://www.keysforkids.org/podcast/keys-for-kids/{devotional-title}/`
- Archive pages: `https://www.keysforkids.org/podcast/default/{devotional-title}/`

**Audio format**: MP3 files are downloaded directly from the Keys for Kids CDN (typically 3-4 MB per devotional).

**Metadata extracted**:
- Title of the devotional
- Publication date
- Bible verse reference
- Devotional content

## Audio Downloads (requires ffmpeg)

### Download audio only as MP3
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only --audio-format mp3
```

### Download audio only as WAV
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only --audio-format wav
```

## Bot Detection and Cookie Authentication

### Using browser cookies (recommended)
```bash
# Chrome cookies
python main.py download --cookies-from-browser chrome "https://www.youtube.com/watch?v=VIDEO_ID"

# Firefox cookies  
python main.py download --cookies-from-browser firefox "https://www.youtube.com/watch?v=VIDEO_ID"

# Safari cookies (macOS)
python main.py download --cookies-from-browser safari "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Using exported cookie file
```bash
python main.py download --cookies ./youtube_cookies.txt "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Format Conversion (requires ffmpeg)

### Download and convert to specific format
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID" --video-format mp4
```

## Playlist Downloads

### Download entire playlist
```bash
python main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Download playlist with cookies
```bash
python main.py download --cookies-from-browser chrome "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Download playlist as audio only
```bash
python main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID" --audio-only --audio-format mp3
```

## Playlist Range Selection

### Download specific range of videos
```bash
# Download videos 1-5
python main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID" --playlist-start 1 --playlist-end 5

# Download videos 3-8
python main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID" --playlist-start 3 --playlist-end 8
```

### Download specific videos by index
```bash
# Download videos 1, 3, and 5
python main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID" --playlist-items "1,3,5"

# Download videos 1-3 and 8-10
python main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID" --playlist-items "1-3,8-10"

# Complex selection: videos 1, 3, 5-8, and 10
python main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID" --playlist-items "1,3,5-8,10"
```

### Combined playlist range with other options
```bash
# Download first 3 videos as MP3 with cookies
python main.py download \
  --cookies-from-browser chrome \
  --playlist-items "1-3" \
  --audio-only --audio-format mp3 \
  --output-dir ~/Music/Playlist \
  "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

## Advanced Options

### Download with subtitles
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID" --subtitles
```

### Download with embedded subtitles (requires ffmpeg)
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID" --embed-subtitles
```

### Download with metadata and thumbnail
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID" --write-info --write-thumbnail
```

### Advanced playlist range filtering
```bash
# Skip first 5 videos, download next 10
python main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID" --playlist-start 6 --playlist-end 15

# Download only odd-numbered videos from 1-20
python main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID" --playlist-items "1,3,5,7,9,11,13,15,17,19"

# Download videos in chunks: 1-5, 10-15, 20-25
python main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID" --playlist-items "1-5,10-15,20-25"
```

## Custom Output Directory

### Specify download location
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir ~/Downloads/Videos
```

## Information Only (No Download)

### Get video information
```bash
python main.py info "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Get playlist information
```bash
python main.py info "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

## Playlist Range Parameters Reference

### Parameter Priority
When both range parameters and playlist items are specified, `--playlist-items` takes priority over `--playlist-start` and `--playlist-end`.

### Syntax Examples
- **`--playlist-start N`**: Start downloading from video N (default: 1)
- **`--playlist-end N`**: Stop downloading at video N (default: last video)
- **`--playlist-items "SPEC"`**: Download specific videos using flexible syntax

### Playlist Items Syntax
- **Single videos**: `"1,3,5"` downloads videos 1, 3, and 5
- **Ranges**: `"1-3"` downloads videos 1, 2, and 3
- **Mixed**: `"1,3,5-8,10"` downloads videos 1, 3, 5, 6, 7, 8, and 10
- **Complex**: `"1-5,10-15,20,25-30"` downloads multiple ranges

### Error Handling
- Invalid indices are skipped with warnings
- Out-of-range indices are ignored with messages
- If all indices are invalid, no videos are downloaded
- Clear feedback is provided about filtering results

### Examples by Use Case
```bash
# Download first 10 videos
python main.py download "PLAYLIST_URL" --playlist-start 1 --playlist-end 10

# Download last 5 videos (if playlist has 50 videos)
python main.py download "PLAYLIST_URL" --playlist-start 46 --playlist-end 50

# Download every 5th video from first 20
python main.py download "PLAYLIST_URL" --playlist-items "5,10,15,20"

# Download beginning, middle, and end samples
python main.py download "PLAYLIST_URL" --playlist-items "1-3,25-27,48-50"
```

## Why ffmpeg is Important

ffmpeg enables:
- **Format conversion**: Convert between different video/audio formats
- **Audio extraction**: Extract audio from video files
- **Post-processing**: Merge video and audio streams for better quality
- **Subtitle embedding**: Embed subtitles directly into video files
- **Metadata handling**: Better handling of video metadata

## ffmpeg Features Used by yt-dlp

1. **Best Quality Downloads**: yt-dlp can download separate video and audio streams and merge them with ffmpeg for the highest quality
2. **Format Conversion**: Automatically convert to your preferred format
3. **Audio Processing**: Extract and convert audio to various formats
4. **Subtitle Processing**: Handle subtitle files and embedding

## Troubleshooting

### If ffmpeg is not found
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **Windows**: Download from https://ffmpeg.org or use `choco install ffmpeg`

### Check if ffmpeg is working
```bash
python main.py test
```

This will show if ffmpeg is properly installed and detected.
