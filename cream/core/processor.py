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

    def __init__(
        self, processor_config: dict[str, str | int | float | bool] | None = None
    ):
        """Initialize the processor.

        Args:
            processor_config: Configuration dictionary for the processor.
        """
        self.config = processor_config or {}
        self.logger = get_logger(self.__class__.__name__)

    def set_config(self, config: dict[str, str | int | float | bool] | None = None, **kwargs) -> None:
        """Update the processor's configuration.

        You can pass a dict via ``config`` and/or key‑value pairs as kwargs.
        Keys with value None are ignored.

        Example:
            proc.set_config({"model_path": "~/models/m.bin"}, device="cuda")
        """
        if config:
            for k, v in config.items():
                if v is not None:
                    self.config[k] = v
        for k, v in kwargs.items():
            if v is not None:
                self.config[k] = v

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

        def process_wrapper(input_path: Path, output_dir: Path | None = None):
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
        processor = ParallelProcessor(num_workers or config.max_workers)
        description = f"Processing with {self.__class__.__name__}"

        return processor.process_batch(input_files, wrapper_func, description)


class ModelBackedProcessor(BaseProcessor):
    """Base class for processors that load a model once and reuse it.

    Uses a simple in‑process cache keyed by absolute ``model_path``. If
    ``model_path`` is missing, falls back to the class name as the key.
    """

    _model_cache: dict[str, object] = {}

    def __init__(
        self, processor_config: dict[str, str | int | float | bool] | None = None
    ):
        super().__init__(processor_config)
        key = self._resolve_model_key()

        model = self._model_cache.get(key)
        if model is None:
            self.logger.info(f"Loading model for key: {key}")
            model = self.load_model()
            self._model_cache[key] = model

        self._model_key = key
        self.model = model

    @abstractmethod
    def load_model(self):
        """Load and return the model instance (subclasses implement)."""
        raise NotImplementedError

    def set_config(self, config: dict[str, str | int | float | bool] | None = None, **kwargs) -> None:
        """Update config and rebind model if ``model_path`` changes."""
        super().set_config(config, **kwargs)
        key = self._resolve_model_key()

        if key != getattr(self, "_model_key", None):
            model = self._model_cache.get(key)
            if model is None:
                self.logger.info(f"Loading model for key: {key}")
                model = self.load_model()
                self._model_cache[key] = model
            self._model_key = key
            self.model = model

    def _resolve_model_key(self):
        """Build a clear, unified cache key.

        Prefer absolute model path; otherwise fall back to class name.
        Format examples:
        - model_path=/abs/path/to/model.bin
        - model_class=MyProcessor
        """
        mpath = self.config.get("model_path")
        if mpath:
            try:
                abs_path = Path(str(mpath)).expanduser().resolve()
                return f"model_path={abs_path}"
            except Exception:
                pass
        return f"model_class={self.__class__.__name__}"


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

    def create(
        self, name: str, config: dict[str, str | int | float | bool] | None = None
    ) -> BaseProcessor:
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
            error_msg = f"Processor '{name}' not found. Available: {available}"
            logger.error(error_msg)
            raise ValidationError(error_msg)

        return self._processors[name](config)

    def list_processors(self) -> list[str]:
        """Get list of registered processors."""
        return list(self._processors.keys())


# Global registry instance
processor_registry = ProcessorRegistry()

# Convenience decorator for easy processor registration
register_processor = processor_registry.register_decorator
