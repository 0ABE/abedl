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
Configuration module for ABEDL
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from .base import DownloadOptions


class Config:
    """Configuration manager for ABEDL"""
    
    DEFAULT_CONFIG = {
        "default_output_dir": "./downloads",
        "default_quality": "best",
        "default_audio_format": "mp3",
        "default_video_format": "mp4",
        "write_info_json": False,
        "write_thumbnail": False,
        "subtitles": False,
        "embed_subtitles": False,
        "max_concurrent_downloads": 3,
        "retry_attempts": 3,
        "user_agent": "ABEDL/1.0.0",
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path"""
        config_dir = Path.home() / ".config" / "abedl"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(user_config)
                    return config
            except (json.JSONDecodeError, IOError):
                print(f"Warning: Could not load config from {self.config_path}, using defaults")
        
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config to {self.config_path}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self.config[key] = value
    
    def to_download_options(self, **overrides) -> DownloadOptions:
        """Convert config to DownloadOptions with optional overrides"""
        options = DownloadOptions(
            output_dir=overrides.get('output_dir', self.get('default_output_dir')),
            quality=overrides.get('quality', self.get('default_quality')),
            audio_only=overrides.get('audio_only', False),
            audio_format=overrides.get('audio_format', self.get('default_audio_format')),
            video_format=overrides.get('video_format', self.get('default_video_format')),
            subtitles=overrides.get('subtitles', self.get('subtitles')),
            embed_subtitles=overrides.get('embed_subtitles', self.get('embed_subtitles')),
            write_info_json=overrides.get('write_info_json', self.get('write_info_json')),
            write_thumbnail=overrides.get('write_thumbnail', self.get('write_thumbnail'))
        )
        return options


# Global config instance
_config = None


def get_config() -> Config:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config
