"""Audio models submodule.

This module contains AI model implementations for audio processing tasks.
Models are organized by functionality (separation, enhancement, ASR, VAD, speaker).
"""

from typing import Union

# Common type definitions for model configurations
ConfigValue = Union[str, int, float, bool, list]
ModelConfig = dict[str, ConfigValue]