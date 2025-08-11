"""Progress bar utilities using the rich library for the cream package.

This module provides pre-configured progress bar components for different types
of operations in the cream package. It uses the rich library to create visually
appealing and informative progress indicators.

The module offers specialized progress bars for:
- File operations (copying, sampling, etc.)
- Audio processing (resampling, segmentation, etc.)
- Analysis operations (MOS evaluation, similarity analysis, etc.)

Example:
    Basic usage of progress bars:
    
    >>> from cream.utils.progress import create_file_progress
    >>> 
    >>> with create_file_progress() as progress:
    ...     task = progress.add_task("Processing files...", total=100)
    ...     for i in range(100):
    ...         # Do some file operation
    ...         progress.update(task, advance=1)
    >>> 
    >>> # For audio processing
    >>> from cream.utils.progress import create_audio_progress
    >>> with create_audio_progress() as progress:
    ...     task = progress.add_task("Resampling audio...", total=50)
    ...     # Process audio files...

Functions:
    create_file_progress: Create progress bar for file operations.
    create_audio_progress: Create progress bar for audio processing.
    create_analysis_progress: Create progress bar for analysis operations.
"""

from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn, 
    TimeRemainingColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
    TaskProgressColumn
)
from rich.console import Console




def create_file_progress() -> Progress:
    """Create a progress bar optimized for file operations.
    
    Creates a rich Progress instance with components suitable for file
    operations such as copying, sampling, and directory processing.
    Includes spinner, task description, progress bar, file counts, and timing.
    
    Returns:
        Progress instance configured for file operations with:
        - Spinner animation
        - Task description in bold blue
        - Progress bar
        - "M of N" completion counter
        - Percentage complete
        - Time elapsed
        
    Example:
        Using the file progress bar:
        
        >>> progress = create_file_progress()
        >>> with progress:
        ...     task = progress.add_task("Copying files", total=1000)
        ...     for i in range(1000):
        ...         # Copy file operation here
        ...         progress.update(task, advance=1)
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=Console()
    )


def create_audio_progress() -> Progress:
    """Create a progress bar optimized for audio processing operations.
    
    Creates a rich Progress instance with components suitable for audio
    processing tasks such as resampling, segmentation, and normalization.
    Uses audio-themed styling and includes time remaining estimates.
    
    Returns:
        Progress instance configured for audio processing with:
        - Audio-themed spinner animation
        - Task description in bold green
        - Green-styled progress bar
        - "M of N" completion counter
        - Percentage complete
        - Time remaining estimate
        
    Example:
        Using the audio progress bar:
        
        >>> progress = create_audio_progress()
        >>> with progress:
        ...     task = progress.add_task("Resampling audio files", total=50)
        ...     for audio_file in audio_files:
        ...         # Resample audio file here
        ...         progress.update(task, advance=1)
    """
    return Progress(
        SpinnerColumn("audio", speed=0.8),
        TextColumn("[bold green]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=Console()
    )


def create_analysis_progress() -> Progress:
    """Create a progress bar optimized for analysis and evaluation operations.
    
    Creates a rich Progress instance with components suitable for analysis
    tasks such as MOS evaluation, similarity analysis, and statistical
    computations. Uses analysis-themed styling without time estimates.
    
    Returns:
        Progress instance configured for analysis operations with:
        - Dots spinner animation
        - Task description in bold yellow
        - Yellow-styled progress bar
        - Percentage complete
        - Time elapsed
        
    Example:
        Using the analysis progress bar:
        
        >>> progress = create_analysis_progress()
        >>> with progress:
        ...     task = progress.add_task("Computing MOS scores", total=200)
        ...     for audio_file in audio_files:
        ...         # Compute MOS score here
        ...         progress.update(task, advance=1)
    """
    return Progress(
        SpinnerColumn("dots", speed=1.0),
        TextColumn("[bold yellow]{task.description}"),
        BarColumn(complete_style="yellow", finished_style="bright_yellow"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=Console()
    )