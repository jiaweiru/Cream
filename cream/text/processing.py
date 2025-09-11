"""Text processing templates - normalization and other processing operations."""

from pathlib import Path

from cream.core.processor import register_processor
from cream.text.text_processor import BaseTextProcessor
from cream.core.exceptions import TextProcessingError
from cream.core.logging import get_logger

logger = get_logger(__name__)


# Text Normalization Processor Example
@register_processor("basic_text_normalizer")
class BasicTextNormalizer(BaseTextProcessor):
    """Basic text normalization processor - Template Implementation."""

    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> str:
        """Normalize text content - Template Implementation."""
        self.validate_input(input_path)

        # Template implementation - replace with actual normalization logic
        error_msg = (
            "Basic text normalizer not implemented - add your normalization logic here"
        )
        logger.error(error_msg)
        raise TextProcessingError(error_msg)


# Text Transformation Processor Example
@register_processor("text_translator")
class TextTranslator(BaseTextProcessor):
    """Text translation processor - Template Implementation."""

    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> str:
        """Translate text content - Template Implementation."""
        self.validate_input(input_path)

        # Template implementation - replace with actual translation logic
        error_msg = "Text translator not implemented - add your translation logic here"
        logger.error(error_msg)
        raise TextProcessingError(error_msg)
