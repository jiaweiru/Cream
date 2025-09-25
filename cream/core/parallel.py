"""Simple parallel processing with automatic task distribution."""

import multiprocessing as mp

from cream.core.logging import get_logger
from cream.core.progress import (
    create_progress,
    log_progress_start,
    log_progress_complete,
)

logger = get_logger()


class ParallelProcessor:
    """Simple parallel processor with automatic task distribution."""

    def __init__(self, num_workers: int = 1):
        self.num_workers = num_workers

    def process_batch(
        self, tasks: list, worker_func, description: str = "Processing"
    ) -> list:
        """Process tasks with progress tracking."""
        if not tasks:
            return []

        # Single worker uses simple sequential processing
        if self.num_workers == 1:
            log_progress_start(description, len(tasks))
            with create_progress() as progress:
                task_progress = progress.add_task(description, total=len(tasks))
                results = []
                for task in tasks:
                    results.append(worker_func(task))
                    progress.update(task_progress, advance=1)
            log_progress_complete(description, len(tasks))
            return results

        # Multiple workers use multiprocessing Pool with real-time progress
        log_progress_start(description, len(tasks))
        with mp.Pool(self.num_workers) as pool:
            with create_progress() as progress:
                task_progress = progress.add_task(description, total=len(tasks))

                # Use pool.imap_unordered for real-time progress tracking
                results = []
                for result in pool.imap_unordered(worker_func, tasks):
                    results.append(result)
                    progress.update(task_progress, advance=1)

        log_progress_complete(description, len(tasks))
        return results
