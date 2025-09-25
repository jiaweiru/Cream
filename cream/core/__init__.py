"""Core framework components.

This module provides the core framework for audio and text processing,
including configuration management, processors, parallel processing,
and exception handling.
"""

from .config import config
from .exceptions import (
    AudioProcessingError,
    CreamError,
    TextProcessingError,
    ValidationError,
)
from .processor import BaseProcessor, ModelBackedProcessor, processor_registry

__all__ = [
    "config",
    "CreamError",
    "AudioProcessingError",
    "TextProcessingError",
    "ValidationError",
    "BaseProcessor",
    "ModelBackedProcessor",
    "processor_registry",
]
