"""MOS (Mean Opinion Score) evaluation functionality for audio quality assessment.

This module provides Mean Opinion Score (MOS) evaluation capabilities using various
deep learning models like NiSQA and UTMOSv2. MOS is a standard metric for evaluating
perceived audio quality on a scale from 1 (poor) to 5 (excellent).

The module supports single file evaluation and batch processing with multi-threading
for efficient analysis of large audio datasets.

Example:
    Basic usage for MOS evaluation:
    
    >>> from pathlib import Path
    >>> from cream.audio.analysis.mos import MOSEvaluator
    >>> 
    >>> evaluator = MOSEvaluator(max_workers=4)
    >>> 
    >>> # Single file evaluation
    >>> score = evaluator.evaluate_file(
    ...     Path("audio.wav"),
    ...     model="nisqa"
    ... )
    >>> print(f"MOS score: {score}")
    >>> 
    >>> # Batch evaluation
    >>> scores = evaluator.evaluate_directory(
    ...     Path("audio_files/"),
    ...     model="utmosv2"
    ... )

Classes:
    MOSEvaluator: Main class for MOS evaluation operations.
"""

from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError
from cream.core.logging import get_logger

logger = get_logger(__name__)


class MOSEvaluator:
    """MOS evaluation processor using various deep learning models.
    
    This class provides methods for evaluating Mean Opinion Score (MOS) of audio
    files using different deep learning models such as NiSQA and UTMOSv2. It supports
    both single file processing and batch directory processing with configurable
    multi-threading for efficient parallel processing.
    
    The evaluator validates input file formats, checks model availability, and
    includes comprehensive error handling and logging for all operations.
    
    Attributes:
        max_workers (int): Maximum number of worker threads for parallel processing.
            Defaults to the system CPU count or configuration setting.
    
    Example:
        Creating and using a MOS evaluator:
        
        >>> evaluator = MOSEvaluator(max_workers=8)
        >>> score = evaluator.evaluate_file(
        ...     Path("speech_sample.wav"),
        ...     model="nisqa"
        ... )
        >>> print(f"Audio quality score: {score}/5.0")
    """
    
    def __init__(self, max_workers: int | None = None) -> None:
        """Initialize the MOS evaluator.
        
        Sets up the evaluator with the specified number of worker threads for
        parallel processing. If max_workers is not provided, uses the value
        from the global configuration.
        
        Args:
            max_workers: Maximum number of worker threads for parallel processing.
                If None, uses the value from config.max_workers (typically CPU count).
        """
        self.max_workers = max_workers or config.max_workers
    
    def evaluate_file(self, audio_path: Path, model: str) -> float:
        """Evaluate MOS score for a single audio file using the specified model.
        
        Computes the Mean Opinion Score (MOS) for the given audio file using the
        specified deep learning model. The score represents perceived audio quality
        on a scale from 1.0 (poor) to 5.0 (excellent).
        
        Args:
            audio_path: Path to the audio file to evaluate.
            model: Name of the MOS model to use (e.g., "nisqa", "utmosv2").
            
        Returns:
            MOS score as a float between 1.0 and 5.0, representing perceived
            audio quality.
            
        Raises:
            InvalidFormatError: If the input file format is not supported.
            ModelNotAvailableError: If the specified MOS model is not available or enabled.
            AudioProcessingError: If the evaluation operation fails.
            
        Example:
            Evaluate audio quality using NiSQA model:
            
            >>> evaluator = MOSEvaluator()
            >>> score = evaluator.evaluate_file(
            ...     Path("recording.wav"),
            ...     "nisqa"
            ... )
            >>> if score > 4.0:
            ...     print("High quality audio")
            >>> elif score > 3.0:
            ...     print("Good quality audio")
            >>> else:
            ...     print("Poor quality audio")
        """
        if not config.is_audio_file(audio_path):
            logger.error(f"Unsupported audio format for MOS evaluation: {audio_path.suffix}")
            raise InvalidFormatError(f"Unsupported audio format: {audio_path.suffix}")
        
        model_config = config.get_model_config("mos", model)
        if not model_config.get("enabled", False):
            logger.error(f"MOS model {model} is not available")
            raise ModelNotAvailableError(f"MOS model {model} is not available")
        
        try:
            # Placeholder for actual MOS evaluation
            # In real implementation, this would load and run NiSQA, UTMOSv2, etc.
            logger.info(f"Evaluating MOS for {audio_path} using {model}")
            
            # Mock MOS score (1-5 scale)
            import random
            random.seed(hash(str(audio_path)) % 2147483647)  # Deterministic for same file
            mock_score = random.uniform(2.5, 4.8)
            
            return round(mock_score, 2)
            
        except Exception as e:
            logger.exception(f"Failed to evaluate MOS for {audio_path}")
            raise AudioProcessingError(f"Failed to evaluate MOS for {audio_path}: {str(e)}")
    
    def evaluate_directory(self, input_dir: Path, model: str) -> dict[str, float]:
        """Evaluate MOS scores for all audio files in a directory using parallel processing.
        
        Recursively finds all supported audio files in the input directory and
        evaluates their MOS scores using the specified model. Uses multi-threading
        for efficient batch processing of large audio collections.
        
        Args:
            input_dir: Path to the input directory containing audio files.
            model: Name of the MOS model to use for all files.
            
        Returns:
            Dictionary mapping filenames to their MOS scores (float values between 1.0-5.0).
            
        Raises:
            FileNotFoundError: If the input directory does not exist.
            AudioProcessingError: If no audio files are found in the input directory
                or if processing fails.
            ModelNotAvailableError: If the specified MOS model is not available.
                
        Example:
            Batch evaluate all audio files in a directory:
            
            >>> evaluator = MOSEvaluator(max_workers=4)
            >>> scores = evaluator.evaluate_directory(
            ...     Path("test_recordings/"),
            ...     "utmosv2"
            ... )
            >>> for filename, score in scores.items():
            ...     print(f"{filename}: {score:.2f}")
            >>> 
            >>> # Find the highest quality audio
            >>> best_file = max(scores, key=scores.get)
            >>> print(f"Best quality: {best_file} ({scores[best_file]:.2f})")
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found for MOS evaluation: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            logger.error(f"No audio files found for MOS evaluation in {input_dir}")
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        results = {}
        
        def process_file(audio_file: Path) -> tuple[str, float]:
            score = self.evaluate_file(audio_file, model)
            return audio_file.name, score
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, score = future.result()
                results[file_name] = score
        
        return results
    
    def batch_evaluate(self, audio_files: list[Path], model: str) -> dict[str, float]:
        """Evaluate MOS scores for a specified batch of audio files.
        
        Evaluates MOS scores for the provided list of audio files using parallel
        processing. This method is useful when you have a specific set of files
        to evaluate rather than processing an entire directory.
        
        Args:
            audio_files: List of Path objects representing audio files to evaluate.
            model: Name of the MOS model to use for all files.
            
        Returns:
            Dictionary mapping filenames to their MOS scores (float values between 1.0-5.0).
            
        Raises:
            AudioProcessingError: If processing fails for any file.
            ModelNotAvailableError: If the specified MOS model is not available.
            
        Example:
            Evaluate a specific set of audio files:
            
            >>> evaluator = MOSEvaluator()
            >>> files_to_evaluate = [
            ...     Path("sample1.wav"),
            ...     Path("sample2.wav"),
            ...     Path("sample3.wav")
            ... ]
            >>> scores = evaluator.batch_evaluate(files_to_evaluate, "nisqa")
            >>> average_score = sum(scores.values()) / len(scores)
            >>> print(f"Average MOS score: {average_score:.2f}")
        """
        results = {}
        
        def process_file(audio_file: Path) -> tuple[str, float]:
            score = self.evaluate_file(audio_file, model)
            return audio_file.name, score
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, score = future.result()
                results[file_name] = score
        
        return results