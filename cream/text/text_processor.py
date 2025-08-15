"""Unified text processor interface."""

from pathlib import Path

from cream.core.processor import BaseProcessor, processor_registry
from cream.core.exceptions import ValidationError
from cream.core.logging import get_logger

# Import processing methods to trigger registration
from . import processing, analysis

logger = get_logger(__name__)


class BaseTextProcessor(BaseProcessor):
    """Base class for text processors."""
    
    SUPPORTED_FORMATS = {'.txt', '.srt', '.vtt', '.json'}
    
    def validate_input(self, input_path: Path) -> None:
        """Validate text input file."""
        super().validate_input(input_path)
        
        if input_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValidationError(
                f"Unsupported text format: {input_path.suffix}. "
                f"Supported formats: {sorted(self.SUPPORTED_FORMATS)}"
            )


class TextProcessorInterface:
    """Unified text processor interface for all text operations."""
    
    def __init__(self, method: str, config: dict[str, str | int | float | bool] = None):
        """Initialize text processor.
        
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
            "normalization": [m for m in all_methods if "normalizer" in m],
            "processing": [m for m in all_methods if any(x in m for x in ["translator", "summarizer", "cleaner"])], 
            "analysis": [m for m in all_methods if any(x in m for x in ["analyzer", "detector"])]
        }
    
    def process_file(self, input_path: Path, output_path: Path = None, **kwargs):
        """Process a single text file."""
        return self.processor.process_single(input_path, output_path, **kwargs)
    
    def process_batch(self, input_files: list[Path], output_dir: Path = None,
                     num_workers: int = 1, **kwargs):
        """Process multiple text files."""
        return self.processor.process_batch(input_files, output_dir, num_workers, **kwargs)