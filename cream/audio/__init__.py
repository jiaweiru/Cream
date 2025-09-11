"""Audio processing module.

Provides audio processing capabilities including resampling, normalization,
and analysis. Importing submodules triggers method registration.
"""

from .audio_processor import AudioProcessorInterface, BaseAudioProcessor

from . import analysis  # noqa: F401
from . import processing  # noqa: F401

__all__ = ["AudioProcessorInterface", "BaseAudioProcessor"]
