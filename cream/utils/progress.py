"""Progress bar utilities using rich library."""

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


class ProgressManager:
    """Rich progress bar manager for various operations."""
    
    def __init__(self, console: Console | None = None):
        self.console = console or Console()
    
    def create_basic_progress(self) -> Progress:
        """Create a basic progress bar."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )
    
    def create_detailed_progress(self) -> Progress:
        """Create a detailed progress bar with time estimates."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console
        )
    
    def create_simple_spinner(self) -> Progress:
        """Create a simple spinner for indeterminate progress."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
    
    def track_iterable(self, iterable: list, description: str = "Processing...",
                      total: int | None = None):
        """Track progress of an iterable with rich progress bar."""
        with self.create_detailed_progress() as progress:
            task = progress.add_task(description, total=total or len(iterable))
            
            for item in iterable:
                yield item
                progress.advance(task)
    
    def track_function(self, func: callable, items: list, description: str = "Processing...",
                      *args, **kwargs) -> list:
        """Track progress of a function applied to a list of items."""
        results = []
        
        with self.create_detailed_progress() as progress:
            task = progress.add_task(description, total=len(items))
            
            for item in items:
                result = func(item, *args, **kwargs)
                results.append(result)
                progress.advance(task)
        
        return results
    
    def show_status(self, message: str, spinner_style: str = "dots") -> None:
        """Show a status message with spinner."""
        with Progress(
            SpinnerColumn(spinner_style),
            TextColumn(f"[green]{message}[/green]"),
            console=self.console
        ) as progress:
            progress.add_task("", total=None)
            # This will show the spinner until the context exits


def create_file_progress() -> Progress:
    """Create a progress bar suitable for file operations."""
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
    """Create a progress bar suitable for audio processing."""
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
    """Create a progress bar suitable for analysis operations."""
    return Progress(
        SpinnerColumn("dots", speed=1.0),
        TextColumn("[bold yellow]{task.description}"),
        BarColumn(complete_style="yellow", finished_style="bright_yellow"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=Console()
    )