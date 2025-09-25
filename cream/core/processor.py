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

logger = get_logger()


def _process_single_task(args):
    """Top-level helper so multiprocessing can pickle task execution."""
    processor, input_path, output_dir, extra_kwargs = args
    output_path = output_dir / input_path.name if output_dir is not None else None
    return processor.process_single(input_path, output_path, **extra_kwargs)


class BaseProcessor(ABC):
    """Base class for all processors.

    This abstract class defines the common interface for all audio and text
    processors. It provides a framework for implementing different analysis
    and processing algorithms in a consistent way.
    """

    def __init__(self) -> None:
        """Initialize the processor (no stored configuration or logger)."""
        pass

    @abstractmethod
    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ):
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
            error_msg = f"Input file not found: {input_path}"
            logger.error(error_msg)
            raise ValidationError(error_msg)

    def process_batch(
        self,
        input_files: list[Path],
        output_dir: Path | None = None,
        num_workers: int | None = None,
        **kwargs,
    ):
        """Process multiple files in parallel.

        Args:
            input_files: List of input file paths.
            output_dir: Optional output directory.
            num_workers: Number of parallel workers.
            **kwargs: Additional processing parameters.

        Returns:
            List of processing results.
        """

        tasks = [
            (self, input_file, output_dir, dict(kwargs)) for input_file in input_files
        ]

        processor = ParallelProcessor(num_workers or config.max_workers)
        description = f"Processing with {self.__class__.__name__}"

        return processor.process_batch(tasks, _process_single_task, description)


class ModelBackedProcessor(BaseProcessor):
    """Base class for processors that manage a loaded model.

    Loads the model on construction. No global cache is maintained.
    """

    def __init__(self) -> None:
        super().__init__()
        # Load the model during initialization
        self.model = self.load_model()

    @abstractmethod
    def load_model(self):
        """Load and return the model instance (subclasses implement)."""
        raise NotImplementedError


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
        logger.debug(f"Registered processor: {name}")

    def register_decorator(self, name: str):
        """Decorator for registering processor classes.

        Args:
            name: Unique name for the processor.

        Returns:
            Decorator function.

        Example:
            @processor_registry.register_decorator("my_processor")
            class MyProcessor(AudioProcessor):
                def process_single(self, input_path, output_path=None, **kwargs):
                    # Implementation here
                    pass
        """

        def decorator(processor_class: type[BaseProcessor]) -> type[BaseProcessor]:
            self.register(name, processor_class)
            return processor_class

        return decorator

    def create(self, name: str) -> BaseProcessor:
        """Create a processor instance.

        Args:
            name: Name of the processor.

        Returns:
            Processor instance.

        Raises:
            ValidationError: If processor not found.
        """
        if name not in self._processors:
            available = list(self._processors.keys())
            error_msg = f"Processor '{name}' not found. Available: {available}"
            logger.error(error_msg)
            raise ValidationError(error_msg)

        return self._processors[name]()

    def list_processors(self) -> list[str]:
        """Get list of registered processors."""
        return list(self._processors.keys())

    def list_processors_by_base(self, base_class: type[BaseProcessor]) -> list[str]:
        """List registered processor names that subclass a given base.

        This helps CLIs filter methods by domain (e.g., audio vs text).

        Args:
            base_class: Base class to filter by.

        Returns:
            List of processor names whose classes inherit from base_class.
        """
        results: list[str] = []
        for name, cls in self._processors.items():
            try:
                if issubclass(cls, base_class):
                    results.append(name)
            except Exception:
                # Be defensive if a non-class somehow got registered
                continue
        return results

    def get_processor_classes(self) -> dict[str, type[BaseProcessor]]:
        """Expose a copy of the registry mapping name -> class.

        Intended for read-only introspection (e.g., advanced CLIs/tests).
        """
        return dict(self._processors)


# Global registry instance
processor_registry = ProcessorRegistry()

# Convenience decorator for easy processor registration
register_processor = processor_registry.register_decorator
