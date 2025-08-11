"""Configuration management for the cream audio and text processing package.

This module provides centralized configuration management for the cream package,
including supported file formats, model configurations, and processing defaults.
The global `config` instance can be imported and used throughout the package.

Example:
    Basic usage of the configuration manager:
    
    >>> from cream.core.config import config
    >>> config.is_audio_file(Path("audio.wav"))
    True
    >>> config.default_sample_rate
    16000

Classes:
    Config: Global configuration manager with file format checking and model configs.
"""

from pathlib import Path
import os


class Config:
    """Global configuration manager for the cream package.
    
    This class manages all configuration settings including supported file formats,
    model configurations, processing defaults, and user-specific directories.
    It automatically creates a configuration directory in the user's home folder
    and provides methods to check file formats and retrieve model configurations.
    
    Attributes:
        home_dir (Path): User's home directory path.
        config_dir (Path): Cream configuration directory (~/.cream).
        audio_formats (list[str]): List of supported audio file extensions.
        text_formats (list[str]): List of supported text file extensions.
        models (dict): Configuration for various AI models (MOS, ASR, VAD, Speaker).
        default_sample_rate (int): Default audio sample rate in Hz.
        default_segment_length (float): Default audio segment length in seconds.
        max_workers (int): Maximum number of worker threads for parallel processing.
    
    Example:
        Creating and using a configuration instance:
        
        >>> config = Config()
        >>> config.is_audio_file(Path("test.wav"))
        True
        >>> config.get_model_config("mos", "nisqa")
        {'path': '', 'enabled': False}
    """
    
    def __init__(self) -> None:
        """Initialize the configuration manager.
        
        Sets up default configurations, creates the config directory if it doesn't
        exist, and initializes all default values for audio formats, text formats,
        model configurations, and processing parameters.
        
        The configuration directory is created at ~/.cream and will be used for
        storing user-specific settings and cached model files in the future.
        """
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".cream"
        self.config_dir.mkdir(exist_ok=True)
        
        # Default configurations
        self.audio_formats = [".wav", ".flac", ".mp3", ".ogg", ".opus", ".m4a", ".aiff", ".ac3"]
        self.text_formats = [".txt", ".json", ".csv"]
        
        # Model configurations (placeholders for future use)
        self.models = {
            "mos": {
                "nisqa": {"path": "", "enabled": False},
                "utmosv2": {"path": "", "enabled": False}
            },
            "asr": {
                "paraformer": {"path": "", "enabled": False},
                "whisper": {"path": "", "enabled": False}
            },
            "vad": {
                "silero": {"path": "", "enabled": False}
            },
            "speaker": {
                "3d-speaker": {"path": "", "enabled": False}
            }
        }
        
        # Processing defaults
        self.default_sample_rate = 16000
        self.default_segment_length = 10.0
        self.max_workers = os.cpu_count() or 4
    
    def get_model_config(self, category: str, model_name: str) -> dict[str, str | bool]:
        """Get configuration for a specific AI model.
        
        Retrieves the configuration dictionary for the specified model within
        the given category. Returns an empty dictionary if the category or
        model is not found.
        
        Args:
            category: Model category (e.g., "mos", "asr", "vad", "speaker").
            model_name: Specific model name within the category.
            
        Returns:
            Dictionary containing model configuration with 'path' and 'enabled' keys.
            Returns empty dict if category or model not found.
            
        Example:
            >>> config = Config()
            >>> config.get_model_config("mos", "nisqa")
            {'path': '', 'enabled': False}
            >>> config.get_model_config("invalid", "model")
            {}
        """
        return self.models.get(category, {}).get(model_name, {})
    
    def is_audio_file(self, path: Path) -> bool:
        """Check if a file has a supported audio format extension.
        
        Compares the file extension (case-insensitive) against the list of
        supported audio formats defined in self.audio_formats.
        
        Args:
            path: Path object representing the file to check.
            
        Returns:
            True if the file extension is in the supported audio formats list,
            False otherwise.
            
        Example:
            >>> config = Config()
            >>> config.is_audio_file(Path("audio.wav"))
            True
            >>> config.is_audio_file(Path("document.pdf"))
            False
        """
        return path.suffix.lower() in self.audio_formats
    
    def is_text_file(self, path: Path) -> bool:
        """Check if a file has a supported text format extension.
        
        Compares the file extension (case-insensitive) against the list of
        supported text formats defined in self.text_formats.
        
        Args:
            path: Path object representing the file to check.
            
        Returns:
            True if the file extension is in the supported text formats list,
            False otherwise.
            
        Example:
            >>> config = Config()
            >>> config.is_text_file(Path("data.txt"))
            True
            >>> config.is_text_file(Path("audio.wav"))
            False
        """
        return path.suffix.lower() in self.text_formats


config = Config()