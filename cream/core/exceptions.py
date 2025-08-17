"""Custom exception classes for the cream audio and text processing package.

This module defines a hierarchy of custom exceptions used throughout the cream
package to handle various error conditions in audio processing, model loading,
file operations, and data validation.

The exception hierarchy follows Python best practices with a base CreamError
class and specific subclasses for different types of errors.

Example:
    Catching and handling cream-specific exceptions:

    >>> try:
    ...     process_audio("invalid_file.wav")
    ... except AudioProcessingError as e:
    ...     print(f"Audio processing failed: {e}")
    ... except FileNotFoundError as e:
    ...     print(f"File not found: {e}")
    ... except CreamError as e:
    ...     print(f"General cream error: {e}")

Classes:
    CreamError: Base exception class for all cream-related errors.
    AudioProcessingError: Raised when audio processing operations fail.
    TextProcessingError: Raised when text processing operations fail.
    ValidationError: Raised when input validation fails.
"""


class CreamError(Exception):
    """Base exception class for all cream package errors.

    This is the parent class for all custom exceptions in the cream package.
    It provides a common base for catching any cream-related error and follows
    Python exception handling best practices.

    All other cream exceptions inherit from this class, allowing users to catch
    either specific exceptions or all cream exceptions using this base class.

    Example:
        Using the base exception to catch any cream error:

        >>> try:
        ...     some_cream_operation()
        ... except CreamError as e:
        ...     print(f"A cream error occurred: {e}")
    """

    pass


class AudioProcessingError(CreamError):
    """Raised when audio processing operations fail.

    This exception is raised when any audio processing operation encounters
    an error, such as file loading failures, format conversion issues,
    resampling errors, or segmentation problems.

    Args:
        message: Descriptive error message explaining what went wrong.

    Example:
        Handling audio processing errors:

        >>> try:
        ...     resample_audio("corrupted.wav", 16000)
        ... except AudioProcessingError as e:
        ...     print(f"Failed to process audio: {e}")
    """

    pass


class TextProcessingError(CreamError):
    """Raised when text processing operations fail.

    This exception is raised when any text processing operation encounters
    an error, such as normalization failures, translation issues, analysis
    problems, or text format conversion errors.

    Args:
        message: Descriptive error message explaining what went wrong.

    Example:
        Handling text processing errors:

        >>> try:
        ...     normalize_text("invalid_content")
        ... except TextProcessingError as e:
        ...     print(f"Failed to process text: {e}")
    """

    pass


class ValidationError(CreamError):
    """Raised when input validation fails.

    This exception is raised when input parameters, file contents, or data
    structures fail validation checks. This includes invalid parameter values,
    malformed data, or data that doesn't meet expected constraints.

    Args:
        message: Descriptive error message explaining what validation failed.

    Example:
        Handling validation errors:

        >>> try:
        ...     validate_sample_rate(-1000)
        ... except ValidationError as e:
        ...     print(f"Validation failed: {e}")
    """

    pass
