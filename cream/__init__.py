"""Cream: Simple and convenient audio data analysis and processing toolkit."""

__version__ = "0.1.0"
__author__ = "Jiawei Ru"
__description__ = "Simple and convenient audio data analysis and processing toolkit"

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
from .audio.analysis.acoustic_frontend import AcousticFrontend

# Text processing
from .text.normalization import TextNormalizer
from .text.stats import TextStatistics

# Utilities
from .utils.file_ops import FileSampler
from .utils.indexing import IndexMatcher
from .utils.validation import InputValidator, validator
from .utils.progress import ProgressManager

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
    "AcousticFrontend",
    
    # Text processing
    "TextNormalizer",
    "TextStatistics",
    
    # Utilities
    "FileSampler",
    "IndexMatcher",
    "InputValidator",
    "validator",
    "ProgressManager"
]
