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

# Activation script for ABEDL virtual environment
# 
# USAGE:
#   source activate.sh    # Correct - activates in current shell
#   . activate.sh         # Also correct - same as source
#   ./activate.sh         # WRONG - runs in subshell, activation lost

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "❌ ERROR: This script must be sourced, not executed!"
    echo ""
    echo "Run it like this:"
    echo "  source activate.sh"
    echo "  or"
    echo "  . activate.sh"
    echo ""
    echo "Do NOT run it like: ./activate.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    return 1
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

echo "✓ ABEDL virtual environment activated"
echo "Available commands:"
echo "  abedl --help          # Show help"
echo "  abedl platforms       # List supported platforms"
echo "  abedl info URL        # Get video/playlist info"
echo "  abedl download URL    # Download video/playlist"
echo "  abedl keysforkids     # Download Keys for Kids devotionals"
echo ""
echo "To deactivate: deactivate"
