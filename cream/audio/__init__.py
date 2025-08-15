"""Audio processing module.

This module provides audio processing capabilities including separation,
enhancement, basic processing, and analysis.
"""

from .audio_processor import AudioProcessor

from . import analysis  # noqa: F401
from . import processing  # noqa: F401

__all__ = ["AudioProcessor"]
