"""Cream: Simple and convenient audio data analysis and processing toolkit.

This module provides a comprehensive set of tools for audio and text data processing,
including audio separation, enhancement, normalization, and analysis capabilities.
It serves as the main entry point for all Cream functionality.

Example:
    Basic usage example:
        
        from cream import AudioProcessor, TextProcessor
        
        # Audio processing
        processor = AudioProcessor(method="uvr_separation")
        result = processor.process_file(input_path, output_path)
        
        # Text processing  
        processor = TextProcessor(method="basic_normalization")
        result = processor.process_file(input_path, output_path)

Attributes:
    __version__ (str): Package version.
    __author__ (str): Package author.
    __description__ (str): Package description.
"""

__version__ = "0.1.0"
__author__ = "Jiawei Ru"
__description__ = "Simple and convenient audio data analysis and processing toolkit"

# Initialize logging with sensible defaults
from .core.logging import setup

# Main classes and functions for easy access
from .core.config import config
from .core.exceptions import (
    CreamError,
    AudioProcessingError,
    InvalidFormatError,
    ModelNotAvailableError,
    ValidationError
)

# Unified processing interfaces
from .audio.audio_processor import AudioProcessor
from .text.text_processor import TextProcessor

# Utilities
from .utils.file_ops import FileSampler
from .utils.indexing import IndexMatcher

# Core processing framework
from .core.processor import processor_registry, BaseProcessor

__all__ = [
    # Core
    "config",
    "CreamError",
    "AudioProcessingError", 
    "InvalidFormatError",
    "ModelNotAvailableError",
    "ValidationError",
    
    # Processing interfaces
    "AudioProcessor",
    "TextProcessor",
    
    # Utilities
    "FileSampler",
    "IndexMatcher",
    
    # Core framework
    "processor_registry",
    "BaseProcessor",
]
