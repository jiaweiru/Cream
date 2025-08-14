"""Generic processor framework for audio and text analysis.

This module provides a unified framework for implementing analysis and processing
tasks. It separates the processing logic from specific implementation methods,
making it easy to add new algorithms and models.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from cream.core.config import config
from cream.core.exceptions import ValidationError
from cream.core.logging import get_logger
from cream.core.parallel import ParallelProcessor

logger = get_logger(__name__)


class BaseProcessor(ABC):
    """Base class for all processors.
    
    This abstract class defines the common interface for all audio and text
    processors. It provides a framework for implementing different analysis
    and processing algorithms in a consistent way.
    """
    
    def __init__(self, processor_config: dict[str, str | int | float | bool] = None):
        """Initialize the processor.
        
        Args:
            processor_config: Configuration dictionary for the processor.
        """
        self.config = processor_config or {}
        self.logger = get_logger(self.__class__.__name__)
        
    @abstractmethod
    def process_single(self, input_path: Path, output_path: Path = None, **kwargs):
        """Process a single file.
        
        Args:
            input_path: Path to input file.
            output_path: Optional path for output file.
            **kwargs: Additional processing parameters.
            
        Returns:
            Processing result.
            
        Raises:
            ValidationError: If input validation fails.
            CreamError: If processing fails.
        """
        pass
    
    def validate_input(self, input_path: Path) -> None:
        """Validate input file.
        
        Args:
            input_path: Path to input file.
            
        Raises:
            ValidationError: If validation fails.
        """
        if not input_path.exists():
            raise ValidationError(f"Input file not found: {input_path}")
    
    def process_batch(self, input_files: list[Path], output_dir: Path = None, 
                     num_workers: int = None, **kwargs):
        """Process multiple files in parallel.
        
        Args:
            input_files: List of input file paths.
            output_dir: Optional output directory.
            num_workers: Number of parallel workers.
            **kwargs: Additional processing parameters.
            
        Returns:
            List of processing results.
        """
        def process_wrapper(input_path: Path, output_dir: Path = None):
            output_path = None
            if output_dir:
                output_path = output_dir / input_path.name
            return self.process_single(input_path, output_path, **kwargs)
        
        if output_dir:
            def wrapper_func(f):
                return process_wrapper(f, output_dir)
        else:
            def wrapper_func(f):
                return process_wrapper(f)
        
        # Get processing configuration
        proc_config = config.get_processor_config()
        processor = ParallelProcessor(num_workers or proc_config['max_workers'])
        description = f"Processing with {self.__class__.__name__}"
        
        return processor.process_batch(input_files, wrapper_func, description)


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


class ProcessorRegistry:
    """Registry for managing processor implementations."""
    
    def __init__(self):
        self._processors: dict[str, type[BaseProcessor]] = {}
        
    def register(self, name: str, processor_class: type[BaseProcessor]) -> None:
        """Register a processor implementation.
        
        Args:
            name: Unique name for the processor.
            processor_class: Processor class.
        """
        self._processors[name] = processor_class
        logger.info(f"Registered processor: {name}")
    
    def create(self, name: str, config: dict[str, str | int | float | bool] = None) -> BaseProcessor:
        """Create a processor instance.
        
        Args:
            name: Name of the processor.
            config: Configuration for the processor.
            
        Returns:
            Processor instance.
            
        Raises:
            ValidationError: If processor not found.
        """
        if name not in self._processors:
            available = list(self._processors.keys())
            raise ValidationError(f"Processor '{name}' not found. Available: {available}")
        
        return self._processors[name](config)
    
    def list_processors(self) -> list[str]:
        """Get list of registered processors."""
        return list(self._processors.keys())


# Global registry instance
processor_registry = ProcessorRegistry()