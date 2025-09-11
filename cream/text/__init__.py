"""Text processing module.

Provides text processing and analysis utilities. Importing submodules triggers
method registration.
"""

from .text_processor import TextProcessorInterface, BaseTextProcessor

# Import templates to trigger registration
from . import analysis  # noqa: F401
from . import processing  # noqa: F401

__all__ = ["TextProcessorInterface", "BaseTextProcessor"]
