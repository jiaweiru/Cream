"""Text processing and analysis module."""

from .normalization import TextNormalizer
from .stats import TextStatistics

__all__ = [
    "TextNormalizer",
    "TextStatistics"
]