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
    ModelNotAvailableError: Raised when a requested AI model is not available.
    InvalidFormatError: Raised when a file format is not supported.
    FileNotFoundError: Raised when a required file cannot be found.
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


class ModelNotAvailableError(CreamError):
    """Raised when a requested AI model is not available or cannot be loaded.
    
    This exception is raised when attempting to use an AI model (MOS, ASR, VAD, etc.)
    that is not properly configured, not downloaded, or cannot be loaded due to
    missing dependencies or incompatible versions.
    
    Args:
        message: Descriptive error message explaining which model is unavailable.
        
    Example:
        Handling model availability errors:
        
        >>> try:
        ...     load_mos_model("nisqa")
        ... except ModelNotAvailableError as e:
        ...     print(f"Model not available: {e}")
    """
    pass


class InvalidFormatError(CreamError):
    """Raised when a file format is not supported by the cream package.
    
    This exception is raised when attempting to process files with unsupported
    formats or extensions. The cream package supports specific audio and text
    formats as defined in the configuration.
    
    Args:
        message: Descriptive error message indicating the unsupported format.
        
    Example:
        Handling unsupported file format errors:
        
        >>> try:
        ...     process_file("document.pdf")
        ... except InvalidFormatError as e:
        ...     print(f"Unsupported format: {e}")
    """
    pass


class FileNotFoundError(CreamError):
    """Raised when a required file cannot be found.
    
    This exception is raised when the cream package cannot locate a file that
    is required for processing, such as input audio files, configuration files,
    or model files.
    
    Note:
        This overrides Python's built-in FileNotFoundError to provide cream-specific
        error handling while maintaining the same semantic meaning.
        
    Args:
        message: Descriptive error message indicating which file was not found.
        
    Example:
        Handling file not found errors:
        
        >>> try:
        ...     load_audio("missing_file.wav")
        ... except FileNotFoundError as e:
        ...     print(f"File not found: {e}")
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