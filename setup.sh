#!/bin/bash
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

# Setup script for ABEDL

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Setting up ABEDL - Abe's Extensible Downloader"
echo "================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if ffmpeg is available
if command -v ffmpeg &> /dev/null; then
    echo "✓ ffmpeg found: $(ffmpeg -version | head -1)"
else
    echo "⚠️  ffmpeg not found. Installing ffmpeg is highly recommended for full functionality."
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   Windows: choco install ffmpeg or download from https://ffmpeg.org"
    echo ""
    read -p "Continue without ffmpeg? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. Please install ffmpeg and try again."
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "📦 Installing dependencies..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✓ Dependencies installed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Install package in editable mode
echo "📦 Installing abedl package..."
pip install -e "$SCRIPT_DIR"
if [ $? -ne 0 ]; then
    echo "❌ Failed to install abedl package"
    exit 1
fi
echo "✓ abedl package installed"

# Check for successful installation
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 ABEDL setup completed successfully!"
    echo ""
    echo "To use ABEDL:"
    echo "  1. Activate the environment: source activate.sh"
    echo "  2. Run commands: abedl --help"
    echo ""
    echo "Example usage:"
    echo "  abedl info 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'"
    echo "  abedl download 'https://www.youtube.com/watch?v=VIDEO_ID'"
    echo "  abedl keysforkids --last-days 7"
else
    # Installation failed
    echo "❌ Setup completed but installation failed."
    exit 1
fi
