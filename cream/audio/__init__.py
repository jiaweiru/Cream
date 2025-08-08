"""Audio processing and analysis module."""

# Audio processing classes
from .processing.resample import AudioResampler
from .processing.segmentation import AudioSegmenter
from .processing.normalization import AudioNormalizer

# Audio analysis classes
from .analysis.mos import MOSEvaluator
from .analysis.intelligibility import IntelligibilityEvaluator
from .analysis.similarity import SpeakerAnalyzer
from .analysis.duration_stats import DurationAnalyzer
from .analysis.acoustic_frontend import AcousticFrontend

__all__ = [
    # Processing
    "AudioResampler",
    "AudioSegmenter",
    "AudioNormalizer",
    
    # Analysis
    "MOSEvaluator",
    "IntelligibilityEvaluator", 
    "SpeakerAnalyzer",
    "DurationAnalyzer",
    "AcousticFrontend"
]