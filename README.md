# ABEDL - Abe's Extensible Downloader

A Python script for downloading videos from various platforms, starting with YouTube support.

## Features

- Download individual YouTube videos
- Download YouTube playlists
- Extensible architecture for adding new video platforms
- Command-line interface with multiple options
- Quality selection and format options

## Installation

### Prerequisites
- Python 3.8 or higher
- ffmpeg (required for video/audio processing)

### Installing ffmpeg
**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html or use chocolatey:
```bash
choco install ffmpeg
```

### Quick Setup (Recommended)
1. Clone this repository
2. Install ffmpeg (see above)
3. Run the setup script:
   ```bash
   ./setup.sh
   ```

### Manual Setup
1. Clone this repository
2. Install ffmpeg (see above)
3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Virtual Environment Activation

#### macOS/Linux
After initial setup, activate the environment before using ABEDL:
```bash
# Navigate to the project directory
cd /path/to/abedl

# Activate the virtual environment
source venv/bin/activate

# You should see (venv) in your terminal prompt
# Now you can run ABEDL commands
python main.py download "VIDEO_URL"
```

#### Using the activation script (shortcut)
```bash
source activate.sh
```

#### Windows
```cmd
venv\Scripts\activate
```

#### To deactivate the virtual environment
```bash
deactivate
```

**Note**: You must activate the virtual environment each time you open a new terminal session before using ABEDL.

## Usage

### Download a single video
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download a playlist
```bash
python main.py download "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Specify output directory
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir /path/to/downloads
```

### Select video quality
```bash
python main.py download "https://www.youtube.com/watch?v=VIDEO_ID" --quality best
```

### List available formats
```bash
python main.py formats "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Architecture

The project uses a plugin-based architecture where each video platform is implemented as a separate downloader class. This makes it easy to add support for new platforms in the future.

## Adding New Platforms

To add support for a new video platform:

1. Create a new downloader class inheriting from `BaseDownloader`
2. Implement the required methods
3. Register the downloader in the platform registry

See the YouTube downloader implementation for reference.

## Troubleshooting

### list-formats errors
If you encounter errors related to format listing:
- The downloader now includes automatic fallback mechanisms
- Use `python main.py formats URL` to check available formats
- Try using `--quality best` for maximum compatibility

### YouTube playlist issues
- Large playlists are processed individually to avoid timeout issues
- Private or unavailable videos in playlists are automatically skipped
- Use `python main.py info PLAYLIST_URL` to check playlist contents first

### ffmpeg not found
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **Windows**: Download from https://ffmpeg.org

### Network issues
- The downloader includes retry mechanisms for network failures
- Check your internet connection
- Some videos may be geo-restricted
