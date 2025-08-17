"""Configuration management for the cream audio and text processing package.

This module provides centralized configuration management for the cream package,
including supported file formats, model configurations, and processing defaults.
The global `config` instance can be imported and used throughout the package.

Example:
    Basic usage of the configuration manager:

    >>> from cream.core.config import config
    >>> config.is_audio_file(Path("audio.wav"))
    True

Classes:
    Config: Global configuration manager with file format checking and model configs.
"""

from pathlib import Path


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
        models (dict): Configuration for AI models (ASR, VAD, Speaker, Separation, Enhancement).
        max_workers (int): Maximum number of worker threads for parallel processing.

    Example:
        Creating and using a configuration instance:

        >>> config = Config()
        >>> config.is_audio_file(Path("test.wav"))
        True
        >>> config.get_model_config("asr", "paraformer-zh")
        {'path': '', 'enabled': False, 'model_type': 'toolkit', ...}
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
        self.model_dir = self.config_dir / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # Supported file formats
        self.audio_formats = [
            ".wav",
            ".flac",
            ".mp3",
            ".ogg",
            ".opus",
            ".m4a",
            ".aiff",
            ".ac3",
            ".wma",
        ]
        self.text_formats = [".txt", ".csv", ".srt", ".vtt", ".json"]

        # Processing configuration
        self.max_workers = 1  # Default to single worker

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

    def set_parallel_config(self, num_workers: int | None = None) -> None:
        """Set parallel processing configuration.

        Args:
            num_workers: Number of workers. If None, keeps current setting.
        """
        if num_workers is not None:
            self.max_workers = num_workers


config = Config()
