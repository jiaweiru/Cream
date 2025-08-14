"""Simple parallel processing with automatic task distribution."""

import multiprocessing as mp
from pathlib import Path

from cream.core.logging import get_logger
from cream.utils.progress import create_progress, log_progress_start, log_progress_complete

logger = get_logger(__name__)


class ParallelProcessor:
    """Simple parallel processor with automatic task distribution."""
    
    def __init__(self, num_workers: int = 1):
        self.num_workers = num_workers
        
    def process_batch(self, tasks: list, worker_func, description: str = "Processing") -> list:
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
                
                # Use pool.imap for real-time progress tracking
                results = []
                for result in pool.imap(worker_func, tasks):
                    results.append(result)
                    progress.update(task_progress, advance=1)
                
        log_progress_complete(description, len(tasks))
        return results


def process_files(files: list[Path], process_func, output_dir: Path = None, 
                 description: str = "Processing files", num_workers: int = 1) -> list:
    """Process files with optional output directory."""
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        def wrapper_func(f):
            return process_func(f, output_dir)
    else:
        wrapper_func = process_func
    
    processor = ParallelProcessor(num_workers)
    return processor.process_batch(files, wrapper_func, description)


def create_processor(num_workers: int = 1) -> ParallelProcessor:
    """Create a parallel processor."""
    return ParallelProcessor(num_workers)