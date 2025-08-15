"""Text processing templates - normalization and other processing operations."""

from pathlib import Path

from cream.core.processor import processor_registry
from cream.text.text_processor import BaseTextProcessor
from cream.core.exceptions import TextProcessingError


# Text Normalization Processor Example
class BasicTextNormalizer(BaseTextProcessor):
    """Basic text normalization processor - Template Implementation."""
    
    def process_single(self, input_path: Path, output_path: Path = None, **kwargs) -> str:
        """Normalize text content - Template Implementation."""
        self.validate_input(input_path)
        
        # Template implementation - replace with actual normalization logic
        raise TextProcessingError("Basic text normalizer not implemented - add your normalization logic here")


# Text Transformation Processor Example
class TextTranslator(BaseTextProcessor):
    """Text translation processor - Template Implementation."""
    
    def process_single(self, input_path: Path, output_path: Path = None, **kwargs) -> str:
        """Translate text content - Template Implementation."""
        self.validate_input(input_path)
        
        # Template implementation - replace with actual translation logic
        raise TextProcessingError("Text translator not implemented - add your translation logic here")


# Register processors
processor_registry.register("basic_text_normalizer", BasicTextNormalizer)
processor_registry.register("text_translator", TextTranslator)