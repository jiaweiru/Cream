"""Unified text processor interface."""

from pathlib import Path

from cream.core.processor import BaseProcessor, processor_registry
from cream.core.exceptions import ValidationError
from cream.core.logging import get_logger
from cream.core.config import config

logger = get_logger()


class BaseTextProcessor(BaseProcessor):
    """Base class for text processors."""

    @property
    def SUPPORTED_FORMATS(self):
        """Get supported text formats from config."""
        return set(config.text_formats)

    def validate_input(self, input_path: Path) -> None:
        """Validate text input file."""
        super().validate_input(input_path)

        if input_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            error_msg = f"Unsupported text format: {input_path.suffix}. Supported formats: {sorted(self.SUPPORTED_FORMATS)}"
            logger.error(error_msg)
            raise ValidationError(error_msg)


class TextProcessorInterface:
    """Unified text processor interface for all text operations."""

    def __init__(self, method: str):
        """Initialize text processor.

        Args:
            method: Processing method to use.
        """
        self.method = method
        self.processor = processor_registry.create(method)

    @classmethod
    def list_all_methods(cls) -> list[str]:
        """Get all available text processing methods."""
        return processor_registry.list_processors()

    def process_file(self, input_path: Path, output_path: Path | None = None, **kwargs):
        """Process a single text file."""
        return self.processor.process_single(input_path, output_path, **kwargs)

    def process_batch(
        self,
        input_files: list[Path],
        output_dir: Path | None = None,
        num_workers: int = 1,
        **kwargs,
    ):
        """Process multiple text files."""
        return self.processor.process_batch(
            input_files, output_dir, num_workers, **kwargs
        )


# Import processing/analysis modules after class definitions to register processors
from . import processing  # noqa: E402,F401
from . import analysis  # noqa: E402,F401
