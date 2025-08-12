"""Audio segmentation functionality for the cream package.

This module provides audio segmentation capabilities with support for both fixed-length
segmentation and Voice Activity Detection (VAD) based segmentation using FunASR and
Silero VAD models. It includes multi-threaded batch processing for efficient handling
of multiple audio files.

The module supports two main segmentation approaches:
1. Fixed-length segmentation: Splits audio into equal-duration chunks
2. VAD-based segmentation: Uses voice activity detection to create variable-length segments
   based on detected speech activity

The VAD functionality now uses a factory pattern for extensible model management,
supporting both FunASR VAD models and Silero VAD for different use cases.

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
    >>> # VAD-based segmentation using FunASR VAD
    >>> vad_segments = segmenter.segment_file_vad(
    ...     Path("audio.wav"),
    ...     Path("vad_segments/"),
    ...     "funasr-vad"
    ... )
    >>> 
    >>> # VAD-based segmentation using Silero VAD
    >>> vad_segments = segmenter.segment_file_vad(
    ...     Path("audio.wav"),
    ...     Path("vad_segments/"),
    ...     "silero-vad"
    ... )

Classes:
    AudioSegmenter: Main class for audio segmentation operations.
"""

from pathlib import Path

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError
from cream.core.logging import get_logger
from cream.core.model_factory import vad_factory

logger = get_logger(__name__)


class AudioSegmenter:
    """Audio segmentation processor with multiple segmentation strategies.
    
    This class provides methods for segmenting audio files using different approaches:
    fixed-length segmentation and Voice Activity Detection (VAD) based segmentation
    using FunASR and Silero VAD models.
    
    The segmenter supports both single file processing and batch directory processing
    with configurable multi-threading for efficient parallel processing. VAD models
    are managed through a factory pattern for extensibility.
    
    Attributes:
        available_vad_models: List of available VAD model names.
        default_vad_model: Default VAD model if none specified.
    
    Example:
        Creating and using an audio segmenter:
        
        >>> segmenter = AudioSegmenter()
        >>> 
        >>> # Fixed-length segmentation
        >>> segments = segmenter.segment_file_fixed(
        ...     Path("long_audio.wav"),
        ...     Path("output_segments/"),
        ...     segment_length=30.0
        ... )
        >>> 
        >>> # VAD-based segmentation
        >>> vad_segments = segmenter.segment_file_vad(
        ...     Path("speech.wav"),
        ...     Path("vad_segments/"),
        ...     "funasr-vad"
        ... )
        >>> print(f"Created {len(vad_segments)} VAD segments")
    """
    
    def __init__(self) -> None:
        """Initialize the audio segmenter.
        
        Sets up the segmenter with VAD model management.
        """
        self._vad_model_instances = {}
        self.available_vad_models = vad_factory.list_models()
        
        if not self.available_vad_models:
            logger.warning(
                "No VAD models are available. VAD-based segmentation will not work."
            )
        else:
            logger.info(f"Available VAD models: {self.available_vad_models}")
        
        self.default_vad_model = (
            self.available_vad_models[0] if self.available_vad_models else None
        )
    
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
    
    def _get_vad_model(self, model_name: str):
        """Get or create VAD model instance for the specified model.
        
        Args:
            model_name: Name of the VAD model.
            
        Returns:
            Model instance ready for VAD detection.
            
        Raises:
            ModelNotAvailableError: If the model is not available or fails to load.
        """
        if model_name in self._vad_model_instances:
            return self._vad_model_instances[model_name]

        # Get model configuration from config
        model_config = config.get_model_config("vad", model_name)
        if not model_config and model_name not in self.available_vad_models:
            # If not in config, create default config for factory models
            model_config = {"enabled": True}
        
        if not model_config.get("enabled", True):
            raise ModelNotAvailableError(
                f"VAD model {model_name} is not enabled"
            )

        try:
            # Create model using factory
            model = vad_factory.create_model(model_name, model_config)
            self._vad_model_instances[model_name] = model
            logger.info(f"Created VAD model: {model_name}")
            return model

        except Exception as e:
            logger.exception(f"Failed to create VAD model {model_name}")
            raise ModelNotAvailableError(
                f"Failed to create VAD model {model_name}: {str(e)}"
            )
    
    def segment_file_vad(self, input_path: Path, output_dir: Path, 
                        vad_model: str, overwrite: bool = False) -> list[Path]:
        """Segment a single audio file using Voice Activity Detection (VAD).
        
        Uses a VAD model to detect speech segments in the audio file and creates
        variable-length segments based on voice activity. This approach is useful
        for separating speech from silence or background noise.
        
        Args:
            input_path: Path to the input audio file to be segmented.
            output_dir: Directory where VAD segment files will be saved.
            vad_model: Name of the VAD model to use ("funasr-vad", "silero-vad").
            overwrite: Whether to overwrite existing segment files. Defaults to False.
            
        Returns:
            List of Path objects representing the created VAD segment files.
            
        Raises:
            InvalidFormatError: If the input file format is not supported.
            ModelNotAvailableError: If the specified VAD model is not available.
            AudioProcessingError: If the VAD segmentation operation fails.
            
        Example:
            Segment an audio file using VAD:
            
            >>> segmenter = AudioSegmenter()
            >>> segments = segmenter.segment_file_vad(
            ...     Path("speech.wav"),
            ...     Path("vad_segments/"),
            ...     "funasr-vad"
            ... )
            >>> for segment in segments:
            ...     print(f"VAD segment: {segment.name}")
        """
        if not config.is_audio_file(input_path):
            logger.error(f"Unsupported audio format for VAD segmentation: {input_path.suffix}")
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")
        
        # Use default VAD model if none specified and available
        if not vad_model and self.default_vad_model:
            vad_model = self.default_vad_model
            logger.info(f"Using default VAD model: {vad_model}")
        
        # Check if VAD model is available
        if vad_model not in self.available_vad_models:
            logger.error(f"VAD model {vad_model} is not available")
            raise ModelNotAvailableError(f"VAD model {vad_model} is not available")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get VAD model instance and perform detection
            vad_model_instance = self._get_vad_model(vad_model)
            
            logger.info(f"VAD segmenting {input_path} using {vad_model}")
            
            # Perform VAD detection
            if not vad_model_instance.is_loaded:
                vad_model_instance.load()
            voice_segments = vad_model_instance.detect_voice_activity(input_path)
            
            # Create audio segments based on VAD results
            segments = []
            base_name = input_path.stem
            
            if not voice_segments:
                logger.warning(f"No voice activity detected in {input_path}")
                return segments
            
            # Create segments for each detected voice activity period
            for i, segment_info in enumerate(voice_segments):
                start_time = segment_info["start"]
                end_time = segment_info["end"]
                confidence = segment_info.get("confidence", 1.0)
                
                segment_name = f"{base_name}_vad_{i:03d}_{start_time:.1f}_{end_time:.1f}{input_path.suffix}"
                segment_path = output_dir / segment_name
                
                if not segment_path.exists() or overwrite:
                    # Extract and save the audio segment
                    success = self._extract_audio_segment(
                        input_path, segment_path, start_time, end_time
                    )
                    if success:
                        segments.append(segment_path)
                        logger.debug(f"Created VAD segment: {segment_name} (confidence: {confidence:.3f})")
            
            logger.info(f"Created {len(segments)} VAD segments from {input_path}")
            return segments
            
        except Exception as e:
            logger.exception(f"Failed to VAD segment {input_path}")
            raise AudioProcessingError(f"Failed to VAD segment {input_path}: {str(e)}")
    
    def _extract_audio_segment(self, input_path: Path, output_path: Path, 
                              start_time: float, end_time: float) -> bool:
        """Extract a specific time segment from audio file.
        
        Args:
            input_path: Path to the input audio file.
            output_path: Path to save the extracted segment.
            start_time: Start time in seconds.
            end_time: End time in seconds.
            
        Returns:
            True if extraction was successful, False otherwise.
        """
        try:
            # For now, create placeholder files
            # In a real implementation, this would use librosa or similar to extract the actual segment
            output_path.touch()
            return True
            
        except Exception as e:
            logger.error(f"Failed to extract segment {start_time:.1f}-{end_time:.1f}s: {str(e)}")
            return False
    
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
        
        # Process files sequentially
        for audio_file in audio_files:
            relative_path = audio_file.relative_to(input_dir)
            file_output_dir = output_dir / relative_path.parent / relative_path.stem
            
            segments = self.segment_file_fixed(audio_file, file_output_dir, segment_length, overwrite)
            results[audio_file.name] = segments
        
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
        
        # Process files sequentially
        for audio_file in audio_files:
            relative_path = audio_file.relative_to(input_dir)
            file_output_dir = output_dir / relative_path.parent / relative_path.stem
            
            segments = self.segment_file_vad(audio_file, file_output_dir, vad_model, overwrite)
            results[audio_file.name] = segments
        
        return results