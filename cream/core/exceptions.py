"""Custom exceptions for cream package."""


class CreamError(Exception):
    """Base exception for cream package."""
    pass


class AudioProcessingError(CreamError):
    """Raised when audio processing fails."""
    pass


class ModelNotAvailableError(CreamError):
    """Raised when requested model is not available."""
    pass


class InvalidFormatError(CreamError):
    """Raised when file format is not supported."""
    pass


class FileNotFoundError(CreamError):
    """Raised when required file is not found."""
    pass


class ValidationError(CreamError):
    """Raised when input validation fails."""
    pass