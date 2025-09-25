"""Simple progress bar utilities using Rich."""

from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
)
from rich.console import Console
import sys

from cream.core.logging import get_logger
from cream.core.config import config

logger = get_logger()


def create_progress(worker_id: int | None = None) -> Progress:
    """Create a progress bar with real-time processing count.

    Args:
        worker_id: If provided, labels the progress bar for a specific worker.

    Returns:
        Progress instance with consistent styling and real-time count display.

    Example:
        # Standard progress bar
        with create_progress() as progress:
            task = progress.add_task("Processing files", total=100)
            for i in range(100):
                progress.update(task, advance=1)

        # Worker progress bar
        with create_progress(worker_id=2) as progress:
            task = progress.add_task("Processing batch", total=50)
            # Shows: "Worker 2: Processing batch [██████████] 25/50 50% 0:01:30"
    """
    if worker_id is not None:
        description = f"[bold blue]Worker {worker_id}: {{task.description}}"
    else:
        description = "[bold blue]{task.description}"

    # Allow disabling via global config
    if not getattr(config, "enable_progress_bars", True):

        class _DummyProgress:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def add_task(self, *_args, **_kwargs):
                return 0

            def update(self, *_args, **_kwargs):
                return None

        return _DummyProgress()  # type: ignore[return-value]

    # Create console that only outputs to terminal (not log files)
    console = Console(file=sys.stderr, force_terminal=True)

    return Progress(
        TextColumn(description),
        BarColumn(),
        MofNCompleteColumn(),  # Shows "25/100" format
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    )


def log_progress_start(description: str, total: int, worker_id: int | None = None):
    """Log progress start to file."""
    worker_info = f"Worker {worker_id}: " if worker_id is not None else ""
    logger.debug(f"{worker_info}{description} started - {total} tasks")


def log_progress_complete(description: str, total: int, worker_id: int | None = None):
    """Log progress completion to file."""
    worker_info = f"Worker {worker_id}: " if worker_id is not None else ""
    logger.debug(f"{worker_info}{description} completed - {total} tasks processed")
