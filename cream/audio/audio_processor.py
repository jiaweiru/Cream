"""Unified audio processor interface."""

from pathlib import Path

from cream.core.processor import BaseProcessor, processor_registry
from cream.core.exceptions import ValidationError
from cream.core.logging import get_logger
from cream.core.config import config

logger = get_logger()


class BaseAudioProcessor(BaseProcessor):
    """Base class for audio processors."""

    @property
    def SUPPORTED_FORMATS(self):
        """Get supported audio formats from config."""
        return set(config.audio_formats)

    def validate_input(self, input_path: Path) -> None:
        """Validate audio input file."""
        super().validate_input(input_path)

        if input_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            error_msg = f"Unsupported audio format: {input_path.suffix}. Supported formats: {sorted(self.SUPPORTED_FORMATS)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)


class AudioProcessorInterface:
    """Unified audio processor interface for all audio operations."""

    def __init__(self, method: str):
        """Initialize audio processor.

        Args:
            method: Processing method to use.
        """
        self.method = method
        self.processor = processor_registry.create(method)

    @classmethod
    def list_all_methods(cls) -> list[str]:
        """Get all available audio processing methods."""
        return processor_registry.list_processors()

    def process_file(self, input_path: Path, output_path: Path | None = None, **kwargs):
        """Process a single audio file."""
        return self.processor.process_single(input_path, output_path, **kwargs)

    def process_batch(
        self,
        input_files: list[Path],
        output_dir: Path | None = None,
        num_workers: int = 1,
        **kwargs,
    ):
        """Process multiple audio files."""
        return self.processor.process_batch(
            input_files, output_dir, num_workers, **kwargs
        )


# Import processing/analysis modules after class definitions to register processors
from . import processing  # noqa: E402, F401
from . import analysis  # noqa: E402,F401
