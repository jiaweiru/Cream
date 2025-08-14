"""Text processing module.

This module provides text processing capabilities including normalization,
analysis, and other text operations.
"""

from .text_processor import TextProcessor

# Import templates to trigger registration  
from . import analysis
from . import processing

__all__ = ["TextProcessor"]