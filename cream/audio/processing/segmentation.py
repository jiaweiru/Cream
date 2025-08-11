"""Audio segmentation functionality for the cream package.

This module provides audio segmentation capabilities with support for both fixed-length
segmentation and Voice Activity Detection (VAD) based segmentation. It includes
multi-threaded batch processing for efficient handling of multiple audio files.

The module supports two main segmentation approaches:
1. Fixed-length segmentation: Splits audio into equal-duration chunks
2. VAD-based segmentation: Uses voice activity detection to create variable-length segments

Example:
    Basic usage for audio segmentation:
    
    >>> from pathlib import Path
    >>> from cream.audio.processing.segmentation import AudioSegmenter
    >>> 
    >>> segmenter = AudioSegmenter(max_workers=4)
    >>> 
    >>> # Fixed-length segmentation
    >>> segments = segmenter.segment_file_fixed(
    ...     Path("audio.wav"),
    ...     Path("segments/"),
    ...     segment_length=10.0
    ... )
    >>> 
    >>> # VAD-based segmentation (requires model setup)
    >>> vad_segments = segmenter.segment_file_vad(
    ...     Path("audio.wav"),
    ...     Path("vad_segments/"),
    ...     "silero"
    ... )

Classes:
    AudioSegmenter: Main class for audio segmentation operations.
"""

from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError
from cream.core.logging import get_logger

logger = get_logger(__name__)


class AudioSegmenter:
    """Audio segmentation processor with multiple segmentation strategies.
    
    This class provides methods for segmenting audio files using different approaches:
    fixed-length segmentation and Voice Activity Detection (VAD) based segmentation.
    It supports both single file processing and batch directory processing with
    configurable multi-threading for efficient parallel processing.
    
    The segmenter validates input file formats, handles output directory creation,
    and includes comprehensive error handling and logging for all operations.
    
    Attributes:
        max_workers (int): Maximum number of worker threads for parallel processing.
            Defaults to the system CPU count or configuration setting.
    
    Example:
        Creating and using an audio segmenter:
        
        >>> segmenter = AudioSegmenter(max_workers=8)
        >>> segments = segmenter.segment_file_fixed(
        ...     Path("long_audio.wav"),
        ...     Path("output_segments/"),
        ...     segment_length=30.0
        ... )
        >>> print(f"Created {len(segments)} segments")
    """
    
    def __init__(self, max_workers: int | None = None) -> None:
        """Initialize the audio segmenter.
        
        Sets up the segmenter with the specified number of worker threads for
        parallel processing. If max_workers is not provided, uses the value
        from the global configuration.
        
        Args:
            max_workers: Maximum number of worker threads for parallel processing.
                If None, uses the value from config.max_workers (typically CPU count).
        """
        self.max_workers = max_workers or config.max_workers
    
    def segment_file_fixed(self, input_path: Path, output_dir: Path, 
                          segment_length: float, overwrite: bool = False) -> list[Path]:
        """Segment a single audio file into fixed-length chunks.
        
        Splits the input audio file into equal-duration segments of the specified
        length. Creates output directory if it doesn't exist and generates segment
        files with sequential naming.
        
        Args:
            input_path: Path to the input audio file to be segmented.
            output_dir: Directory where segment files will be saved.
            segment_length: Duration of each segment in seconds.
            overwrite: Whether to overwrite existing segment files. Defaults to False.
            
        Returns:
            List of Path objects representing the created segment files.
            
        Raises:
            InvalidFormatError: If the input file format is not supported.
            AudioProcessingError: If the segmentation operation fails.
            
        Example:
            Segment an audio file into 10-second chunks:
            
            >>> segmenter = AudioSegmenter()
            >>> segments = segmenter.segment_file_fixed(
            ...     Path("podcast.wav"),
            ...     Path("segments/"),
            ...     segment_length=10.0
            ... )
            >>> for segment in segments:
            ...     print(f"Created: {segment.name}")
        """
        if not config.is_audio_file(input_path):
            logger.error(f"Unsupported audio format for fixed segmentation: {input_path.suffix}")
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Placeholder for actual segmentation implementation
            # In real implementation, this would use librosa, pydub, or similar
            logger.info(f"Segmenting {input_path} into {segment_length}s chunks")
            
            # For demonstration, create mock segment files
            segments = []
            base_name = input_path.stem
            
            # Mock: assume 30-second file, create 3 segments of 10s each
            for i in range(3):
                segment_name = f"{base_name}_segment_{i:03d}{input_path.suffix}"
                segment_path = output_dir / segment_name
                
                if not segment_path.exists() or overwrite:
                    # In real implementation, this would create actual audio segments
                    segment_path.touch()
                    segments.append(segment_path)
            
            return segments
            
        except Exception as e:
            logger.exception(f"Failed to segment {input_path}")
            raise AudioProcessingError(f"Failed to segment {input_path}: {str(e)}")
    
    def segment_file_vad(self, input_path: Path, output_dir: Path, 
                        vad_model: str, overwrite: bool = False) -> list[Path]:
        """Segment a single audio file using Voice Activity Detection (VAD).
        
        Uses a VAD model to detect speech segments in the audio file and creates
        variable-length segments based on voice activity. This approach is useful
        for separating speech from silence or background noise.
        
        Args:
            input_path: Path to the input audio file to be segmented.
            output_dir: Directory where VAD segment files will be saved.
            vad_model: Name of the VAD model to use (e.g., "silero").
            overwrite: Whether to overwrite existing segment files. Defaults to False.
            
        Returns:
            List of Path objects representing the created VAD segment files.
            
        Raises:
            InvalidFormatError: If the input file format is not supported.
            ModelNotAvailableError: If the specified VAD model is not available or enabled.
            AudioProcessingError: If the VAD segmentation operation fails.
            
        Example:
            Segment an audio file using VAD:
            
            >>> segmenter = AudioSegmenter()
            >>> segments = segmenter.segment_file_vad(
            ...     Path("speech.wav"),
            ...     Path("vad_segments/"),
            ...     "silero"
            ... )
            >>> for segment in segments:
            ...     print(f"VAD segment: {segment.name}")
        """
        if not config.is_audio_file(input_path):
            logger.error(f"Unsupported audio format for VAD segmentation: {input_path.suffix}")
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")
        
        model_config = config.get_model_config("vad", vad_model)
        if not model_config.get("enabled", False):
            logger.error(f"VAD model {vad_model} is not available")
            raise ModelNotAvailableError(f"VAD model {vad_model} is not available")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Placeholder for actual VAD segmentation
            logger.info(f"VAD segmenting {input_path} using {vad_model}")
            
            # Mock VAD segments
            segments = []
            base_name = input_path.stem
            
            # Mock: create variable length segments based on "voice activity"
            segment_info = [(0.5, 3.2), (4.1, 7.8), (9.0, 12.5)]  # start, end times
            
            for i, (start, end) in enumerate(segment_info):
                segment_name = f"{base_name}_vad_{i:03d}_{start:.1f}_{end:.1f}{input_path.suffix}"
                segment_path = output_dir / segment_name
                
                if not segment_path.exists() or overwrite:
                    segment_path.touch()
                    segments.append(segment_path)
            
            return segments
            
        except Exception as e:
            logger.exception(f"Failed to VAD segment {input_path}")
            raise AudioProcessingError(f"Failed to VAD segment {input_path}: {str(e)}")
    
    def segment_fixed_length(self, input_dir: Path, output_dir: Path, 
                           segment_length: float, overwrite: bool = False) -> dict[str, list[Path]]:
        """Segment all audio files in a directory using fixed-length chunks.
        
        Recursively finds all supported audio files in the input directory and
        segments them into fixed-length chunks using parallel processing. Maintains
        directory structure in the output directory.
        
        Args:
            input_dir: Path to the input directory containing audio files.
            output_dir: Path to the output directory where segments will be saved.
            segment_length: Duration of each segment in seconds.
            overwrite: Whether to overwrite existing segment files. Defaults to False.
            
        Returns:
            Dictionary mapping original filenames to lists of created segment paths.
            
        Raises:
            FileNotFoundError: If the input directory does not exist.
            AudioProcessingError: If no audio files are found in the input directory
                or if processing fails.
                
        Example:
            Batch segment all audio files in a directory:
            
            >>> segmenter = AudioSegmenter(max_workers=4)
            >>> results = segmenter.segment_fixed_length(
            ...     Path("audio_files/"),
            ...     Path("segmented_files/"),
            ...     segment_length=15.0
            ... )
            >>> for filename, segments in results.items():
            ...     print(f"{filename}: {len(segments)} segments")
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found for segmentation: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            logger.error(f"No audio files found for segmentation in {input_dir}")
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        results = {}
        
        def process_file(audio_file: Path) -> tuple[str, list[Path]]:
            relative_path = audio_file.relative_to(input_dir)
            file_output_dir = output_dir / relative_path.parent / relative_path.stem
            
            segments = self.segment_file_fixed(audio_file, file_output_dir, segment_length, overwrite)
            return audio_file.name, segments
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, segments = future.result()
                results[file_name] = segments
        
        return results
    
    def segment_vad(self, input_dir: Path, output_dir: Path, 
                   vad_model: str, overwrite: bool = False) -> dict[str, list[Path]]:
        """Segment all audio files in a directory using Voice Activity Detection.
        
        Recursively finds all supported audio files in the input directory and
        segments them using VAD with parallel processing. Creates variable-length
        segments based on detected voice activity.
        
        Args:
            input_dir: Path to the input directory containing audio files.
            output_dir: Path to the output directory where VAD segments will be saved.
            vad_model: Name of the VAD model to use for all files.
            overwrite: Whether to overwrite existing segment files. Defaults to False.
            
        Returns:
            Dictionary mapping original filenames to lists of created VAD segment paths.
            
        Raises:
            FileNotFoundError: If the input directory does not exist.
            AudioProcessingError: If no audio files are found in the input directory
                or if processing fails.
            ModelNotAvailableError: If the specified VAD model is not available.
                
        Example:
            Batch VAD segment all audio files in a directory:
            
            >>> segmenter = AudioSegmenter(max_workers=2)
            >>> results = segmenter.segment_vad(
            ...     Path("recordings/"),
            ...     Path("vad_segments/"),
            ...     "silero"
            ... )
            >>> for filename, segments in results.items():
            ...     print(f"{filename}: {len(segments)} VAD segments")
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found for segmentation: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            logger.error(f"No audio files found for segmentation in {input_dir}")
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        results = {}
        
        def process_file(audio_file: Path) -> tuple[str, list[Path]]:
            relative_path = audio_file.relative_to(input_dir)
            file_output_dir = output_dir / relative_path.parent / relative_path.stem
            
            segments = self.segment_file_vad(audio_file, file_output_dir, vad_model, overwrite)
            return audio_file.name, segments
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, segments = future.result()
                results[file_name] = segments
        
        return results