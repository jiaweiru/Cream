"""File operations utilities including sampling and copying."""

from pathlib import Path
import random
import shutil

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError
from cream.core.logging import get_logger
from cream.core.parallel import ParallelProcessor

logger = get_logger(__name__)


class FileSampler:
    """File sampling utility for random selection and copying."""

    def __init__(self, seed: int | None = None, num_workers: int | None = None):
        """Initialize FileSampler with parallel processing configuration.

        Args:
            seed: Random seed for reproducible sampling.
            num_workers: Number of workers for parallel processing.
        """
        self.processor = ParallelProcessor(
            num_workers=num_workers or config.max_workers,
            show_progress=True,  # Always show progress as per CLAUDE.md
        )

        if seed is not None:
            random.seed(seed)

    def get_matching_files(
        self, input_dir: Path, pattern: str = "*", recursive: bool = True
    ) -> list[Path]:
        """Get all files matching pattern in directory."""
        if not input_dir.exists():
            logger.error(f"Input directory not found for file operations: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        if recursive:
            files = list(input_dir.rglob(pattern))
        else:
            files = list(input_dir.glob(pattern))

        # Filter out directories
        files = [f for f in files if f.is_file()]

        return files

    def sample_files(self, files: list[Path], count: int) -> list[Path]:
        """Sample a specified number of files from the list."""
        if count >= len(files):
            return files.copy()

        return random.sample(files, count)

    def copy_file(self, src: Path, dst: Path, preserve_structure: bool = True) -> bool:
        """Copy a single file to destination."""
        try:
            if preserve_structure:
                dst.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(src, dst)
            return True

        except Exception:
            logger.exception(f"Failed to copy {src} to {dst}")
            return False

    def sample_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        count: int,
        pattern: str = "*",
        preserve_structure: bool = False,
    ) -> list[Path]:
        """Sample files from input directory and copy to output directory."""
        if not input_dir.exists():
            logger.error(f"Input directory not found for file operations: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Get all matching files
        all_files = self.get_matching_files(input_dir, pattern)

        if not all_files:
            logger.error(f"No files found matching pattern {pattern} in {input_dir}")
            raise AudioProcessingError(
                f"No files found matching pattern {pattern} in {input_dir}"
            )

        # Sample the specified number of files
        sampled_files = self.sample_files(all_files, count)

        output_dir.mkdir(parents=True, exist_ok=True)
        copied_files = []

        def copy_file_task(src_file):
            if preserve_structure:
                # Preserve directory structure
                relative_path = src_file.relative_to(input_dir)
                dst_file = output_dir / relative_path
            else:
                # Flat structure
                dst_file = output_dir / src_file.name

                # Handle name conflicts in flat structure
                counter = 1
                original_dst = dst_file
                while dst_file.exists():
                    stem = original_dst.stem
                    suffix = original_dst.suffix
                    dst_file = output_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

            if self.copy_file(src_file, dst_file, preserve_structure):
                return dst_file
            return None

        # Use batch processor with progress bar
        results = self.processor.process_batch(
            sampled_files, copy_file_task, "Copying files"
        )
        copied_files = [result for result in results if result is not None]

        return copied_files

    def stratified_sample(
        self,
        input_dir: Path,
        output_dir: Path,
        count_per_subdir: int,
        pattern: str = "*",
    ) -> dict[str, list[Path]]:
        """Sample files from each subdirectory separately."""
        if not input_dir.exists():
            logger.error(f"Input directory not found for file operations: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        results = {}

        # Find all subdirectories
        subdirs = [d for d in input_dir.iterdir() if d.is_dir()]

        if not subdirs:
            # No subdirectories, sample from root
            sampled = self.sample_directory(
                input_dir, output_dir, count_per_subdir, pattern
            )
            results["root"] = sampled
            return results

        for subdir in subdirs:
            try:
                subdir_output = output_dir / subdir.name
                sampled = self.sample_directory(
                    subdir,
                    subdir_output,
                    count_per_subdir,
                    pattern,
                    preserve_structure=True,
                )
                results[subdir.name] = sampled
            except Exception:
                logger.exception(f"Failed to sample from {subdir}")
                continue

        return results

    def filter_files_by_size(
        self,
        files: list[Path],
        min_size: int | None = None,
        max_size: int | None = None,
    ) -> list[Path]:
        """Filter files by size in bytes."""
        filtered_files = []

        for file_path in files:
            try:
                size = file_path.stat().st_size

                if min_size is not None and size < min_size:
                    continue
                if max_size is not None and size > max_size:
                    continue

                filtered_files.append(file_path)

            except Exception:
                continue

        return filtered_files

    def get_sampling_stats(
        self, original_files: list[Path], sampled_files: list[Path]
    ) -> dict[str, int | float]:
        """Get statistics about the sampling process."""
        original_size = sum(f.stat().st_size for f in original_files if f.exists())
        sampled_size = sum(f.stat().st_size for f in sampled_files if f.exists())

        # Group by file extension
        original_extensions = {}
        sampled_extensions = {}

        for f in original_files:
            ext = f.suffix.lower()
            original_extensions[ext] = original_extensions.get(ext, 0) + 1

        for f in sampled_files:
            ext = f.suffix.lower()
            sampled_extensions[ext] = sampled_extensions.get(ext, 0) + 1

        stats = {
            "original_count": len(original_files),
            "sampled_count": len(sampled_files),
            "sampling_ratio": len(sampled_files) / len(original_files)
            if original_files
            else 0,
            "original_size_mb": round(original_size / (1024 * 1024), 2),
            "sampled_size_mb": round(sampled_size / (1024 * 1024), 2),
            "original_extensions": original_extensions,
            "sampled_extensions": sampled_extensions,
        }

        return stats
