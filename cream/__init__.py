"""Cream: Simple and convenient audio data analysis and processing toolkit.

This module provides a comprehensive set of tools for audio and text data processing,
including audio separation, enhancement, normalization, and analysis capabilities.
It serves as the main entry point for all Cream functionality.

Example:
    Basic usage example:
        
        from cream import AudioSeparator, TextNormalizer
        
        # Audio processing
        separator = AudioSeparator()
        separated_files = separator.separate_file(input_path, output_dir, "uvr")
        
        # Text processing  
        normalizer = TextNormalizer()
        clean_text = normalizer.apply_normalization(text, "basic")

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

# Audio processing
from .audio.processing.resample import AudioResampler
from .audio.processing.segmentation import AudioSegmenter
from .audio.processing.normalization import AudioNormalizer

# Audio analysis
from .audio.analysis.mos import MOSEvaluator
from .audio.analysis.intelligibility import IntelligibilityEvaluator
from .audio.analysis.similarity import SpeakerAnalyzer
from .audio.analysis.duration_stats import DurationAnalyzer
from .audio.analysis.acoustic_frontend import AudioSeparator, AudioEnhancer

# Text processing
from .text.normalization import TextNormalizer
from .text.stats import TextStatistics

# Utilities
from .utils.file_ops import FileSampler
from .utils.indexing import IndexMatcher

__all__ = [
    # Core
    "config",
    "CreamError",
    "AudioProcessingError", 
    "InvalidFormatError",
    "ModelNotAvailableError",
    "ValidationError",
    
    # Audio processing
    "AudioResampler",
    "AudioSegmenter", 
    "AudioNormalizer",
    
    # Audio analysis
    "MOSEvaluator",
    "IntelligibilityEvaluator",
    "SpeakerAnalyzer",
    "DurationAnalyzer",
    "AudioSeparator",
    "AudioEnhancer",
    
    # Text processing
    "TextNormalizer",
    "TextStatistics",
    
    # Utilities
    "FileSampler",
    "IndexMatcher",
]
