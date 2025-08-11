"""Logging configuration module using loguru for the cream package.

This module provides a centralized logging configuration system for the cream
package, utilizing the loguru library for structured, colored, and feature-rich
logging output. It offers simple configuration options for both console and file
logging with automatic log rotation, compression, and retention.

The module provides two main functions:
- get_logger(): Get a logger instance bound to a specific name
- configure_logging(): Set up logging with customizable parameters

Example:
    Basic logging setup and usage:
    
    >>> from cream.core.logging import configure_logging, get_logger
    >>> configure_logging(level="INFO", log_file="app.log")
    >>> logger = get_logger(__name__)
    >>> logger.info("Application started")
    >>> logger.error("Something went wrong")
    
    Using the default logger:
    
    >>> from cream.core.logging import cream_logger
    >>> cream_logger.info("Using default logger")

Functions:
    get_logger: Get a logger instance bound to a specific name.
    configure_logging: Configure loguru logger with comprehensive parameters.
    
Variables:
    cream_logger: Default logger instance for backward compatibility.
"""

import sys
from pathlib import Path
from loguru import logger
from loguru import Logger
import os




def get_logger(name: str | None = None) -> Logger:
    """Get a logger instance bound to a specific name.
    
    Creates and returns a loguru logger instance that can be bound to a specific
    name (typically the module name). This allows for better log organization
    and filtering by identifying which module generated each log message.
    
    Args:
        name: Logger name, typically __name__ of the calling module. If None,
            returns the base logger without name binding.
        
    Returns:
        Loguru logger instance. If name is provided, returns a logger bound to
        that name. Otherwise returns the base logger.
        
    Example:
        Getting a logger for a specific module:
        
        >>> logger = get_logger(__name__)
        >>> logger.info("This will show the module name in logs")
        
        Getting the base logger:
        
        >>> logger = get_logger()
        >>> logger.info("This uses the base logger")
    """
    if name:
        return logger.bind(name=name)
    return logger


def configure_logging(
    level: str = "INFO",
    log_file: str | Path | None = None,
    console_output: bool = True,
    colorize: bool = True,
    rotation: str = "10 MB",
    retention: str = "7 days",
    compression: str = "zip",
    safe_mode: bool = True
) -> None:
    """Configure loguru logger with comprehensive parameters.
    
    Sets up the loguru logger with the specified configuration, including
    console and file output options. Removes any existing handlers before
    applying new configuration. File logging includes automatic rotation,
    compression, and retention policies.
    
    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
            Defaults to "INFO".
        log_file: Path to the log file. If provided as a string, it will be
            converted to a Path object. Parent directories will be created
            automatically. If None, no file logging is configured.
        console_output: Whether to enable console (stderr) output. Defaults
            to True.
        colorize: Whether to enable colored output for console logging.
            Defaults to True. Has no effect if console_output is False.
        rotation: File rotation size or time. Defaults to "10 MB".
        retention: How long to keep log files. Defaults to "7 days".
        compression: Compression format for rotated logs. Defaults to "zip".
        safe_mode: Whether to disable backtrace and diagnose in production.
            Defaults to True for security.
            
    Note:
        File logging includes the following features:
        - Automatic rotation when file size exceeds 10 MB
        - Retention of logs for 7 days
        - Compression of rotated logs using zip
        - Asynchronous writing for better performance
        
    Example:
        Basic configuration with console output only:
        
        >>> configure_logging(level="DEBUG")
        
        Configuration with both console and file output:
        
        >>> configure_logging(
        ...     level="INFO",
        ...     log_file="/var/log/cream.log",
        ...     console_output=True,
        ...     colorize=True,
        ...     rotation="50 MB",
        ...     retention="14 days"
        ... )
        
        Production-safe configuration:
        
        >>> configure_logging(
        ...     level="WARNING",
        ...     log_file="errors.log",
        ...     console_output=False,
        ...     safe_mode=True
        ... )
    """
    # Default format string
    format_string = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # Remove all existing handlers
    logger.remove()
    
    # Determine if we're in production (safe mode considerations)
    is_production = safe_mode or os.getenv('CREAM_PRODUCTION', '').lower() in ('true', '1', 'yes')
    
    # Add console handler if enabled
    if console_output:
        logger.add(
            sys.stderr,
            level=level.upper(),
            format=format_string,
            colorize=colorize,
            backtrace=not is_production,
            diagnose=not is_production
        )
    
    # Add file handler if specified
    if log_file:
        try:
            log_path = Path(log_file) if isinstance(log_file, str) else log_file
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.add(
                str(log_path),
                level=level.upper(),
                format=format_string,
                rotation=rotation,
                retention=retention,
                compression=compression,
                backtrace=not is_production,
                diagnose=not is_production,
                enqueue=True
            )
        except (OSError, PermissionError) as e:
            # Fallback to console-only logging if file logging fails
            if console_output:
                logger.warning(f"Failed to configure file logging: {e}. Continuing with console-only logging.")
            else:
                # If both file and console fail, at least enable basic console logging
                logger.add(sys.stderr, level=level.upper(), format="{time} | {level} | {message}")
                logger.error(f"File logging failed and console was disabled: {e}. Enabled basic console logging.")


# Default logger instance for backward compatibility and convenience
cream_logger = get_logger("cream")