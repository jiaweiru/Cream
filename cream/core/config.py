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
    CreamConfig: Global configuration manager with file format checking and model configs.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from contextlib import contextmanager

from .logging import get_logger

logger = get_logger()


@contextmanager
def set_env(**environ):
    old_values = {}
    to_delete = []

    environ_str = {
        k: str(v) if isinstance(v, (Path, int, float)) else v
        for k, v in environ.items()
    }

    for k, v in environ_str.items():
        if k in os.environ:
            old_values[k] = os.environ[k]
        else:
            to_delete.append(k)
        os.environ[k] = v

    try:
        yield
    finally:
        for k, v in old_values.items():
            os.environ[k] = v
        for k in to_delete:
            os.environ.pop(k, None)


@dataclass
class CreamConfig:
    """Central configuration for Cream application.

    This dataclass manages all configuration settings including supported file formats,
    processing parameters, directory paths, and logging settings.
    """

    # Directory settings
    home_dir: Path = field(default_factory=Path.home)
    config_dir: Path = field(init=False)
    model_dir: Path = field(init=False)

    # File format settings
    audio_formats: list[str] = field(
        default_factory=lambda: [
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
    )
    text_formats: list[str] = field(
        default_factory=lambda: [".txt", ".csv", ".tsv", ".json"]
    )

    # Processing settings
    max_workers: int = 1
    enable_progress_bars: bool = True

    # Logging settings
    log_level: str = "INFO"
    log_file: str | None = None

    def __post_init__(self):
        """Initialize derived paths and validate configuration after initialization."""
        self.config_dir = self.home_dir / ".cream"
        self.model_dir = self.config_dir / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.validate_config()

    def validate_config(self) -> None:
        """Validate configuration settings."""
        if self.max_workers < 1:
            logger.warning(
                f"max_workers must be >= 1, got {self.max_workers}. Setting to 1."
            )
            self.max_workers = 1

        if self.log_file and not Path(self.log_file).parent.exists():
            logger.warning(f"Log file parent directory does not exist: {self.log_file}")

    def validate_directories(self) -> None:
        """Validate and ensure required directories exist."""
        try:
            self.model_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured model directory exists: {self.model_dir}")
        except Exception as e:
            logger.error(f"Failed to create model directory: {e}")

    def is_audio_file(self, path: Path) -> bool:
        """Check if a file has a supported audio format extension.

        Args:
            path: Path object representing the file to check.

        Returns:
            True if the file extension is in the supported audio formats list.
        """
        return path.suffix.lower() in self.audio_formats

    def is_text_file(self, path: Path) -> bool:
        """Check if a file has a supported text format extension.

        Args:
            path: Path object representing the file to check.

        Returns:
            True if the file extension is in the supported text formats list.
        """
        return path.suffix.lower() in self.text_formats

    def set_parallel_config(
        self, num_workers: int | None = None, enable_progress_bars: bool | None = None
    ) -> None:
        """Set parallel processing configuration.

        Args:
            num_workers: Number of workers. If None, keeps current setting.
            enable_progress_bars: Whether to show progress bars. If None, keeps current setting.
        """
        if num_workers is not None:
            self.max_workers = max(1, num_workers)
            logger.debug(f"Updated max_workers: {self.max_workers}")

        if enable_progress_bars is not None:
            self.enable_progress_bars = enable_progress_bars
            logger.debug(f"Updated enable_progress_bars: {self.enable_progress_bars}")

    def update_from_cli_args(self, **kwargs) -> None:
        """Update configuration from command line arguments.

        Args:
            **kwargs: Configuration values to update.
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
                logger.debug(f"Updated config: {key}={value}")

    @property
    def supported_audio_formats(self) -> list[str]:
        """Get list of supported audio formats."""
        return self.audio_formats.copy()

    @property
    def supported_text_formats(self) -> list[str]:
        """Get list of supported text formats."""
        return self.text_formats.copy()

    @property
    def all_supported_formats(self) -> list[str]:
        """Get list of all supported file formats."""
        return self.audio_formats + self.text_formats


# Global configuration instance
config = CreamConfig()
