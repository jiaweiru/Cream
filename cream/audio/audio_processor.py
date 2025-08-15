"""Unified audio processor interface."""

from pathlib import Path

from cream.core.processor import BaseProcessor, processor_registry
from cream.core.exceptions import ValidationError
from cream.core.logging import get_logger

from . import processing  # noqa: F401
from . import analysis  # noqa: F401

logger = get_logger(__name__)


class BaseAudioProcessor(BaseProcessor):
    """Base class for audio processors."""
    
    SUPPORTED_FORMATS = {'.wav', '.mp3', '.flac', '.m4a', '.ogg', '.wma'}
    
    def validate_input(self, input_path: Path) -> None:
        """Validate audio input file."""
        super().validate_input(input_path)
        
        if input_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValidationError(
                f"Unsupported audio format: {input_path.suffix}. "
                f"Supported formats: {sorted(self.SUPPORTED_FORMATS)}"
            )


class AudioProcessorInterface:
    """Unified audio processor interface for all audio operations."""

    def __init__(self, method: str, config: dict[str, str | int | float | bool] = None):
        """Initialize audio processor.

        Args:
            method: Processing method to use.
            config: Configuration for the processor.
        """
        self.method = method
        self.processor = processor_registry.create(method, config)

    @classmethod
    def list_all_methods(cls) -> dict[str, list[str]]:
        """Get all available methods grouped by category."""
        all_methods = processor_registry.list_processors()

        return {
            "separation": [
                m for m in all_methods if "separator" in m or "spleeter" in m
            ],
            "enhancement": [m for m in all_methods if "enhancer" in m],
            "basic_processing": [
                m
                for m in all_methods
                if any(x in m for x in ["resampler", "normalizer", "segmenter"])
            ],
            "analysis": [
                m
                for m in all_methods
                if any(x in m for x in ["evaluator", "analyzer", "asr", "vad"])
            ],
        }

    def process_file(self, input_path: Path, output_path: Path = None, **kwargs):
        """Process a single audio file."""
        return self.processor.process_single(input_path, output_path, **kwargs)

    def process_batch(
        self,
        input_files: list[Path],
        output_dir: Path = None,
        num_workers: int = 1,
        **kwargs,
    ):
        """Process multiple audio files."""
        return self.processor.process_batch(
            input_files, output_dir, num_workers, **kwargs
        )
