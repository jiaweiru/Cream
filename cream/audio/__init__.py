"""Audio processing module.

This module provides audio processing capabilities including separation,
enhancement, basic processing, and analysis.
"""

from .audio_processor import AudioProcessor

# Import templates to trigger registration
from . import analysis
from . import processing

__all__ = ["AudioProcessor"]