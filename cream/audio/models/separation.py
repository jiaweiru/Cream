"""Audio separation model implementations.

This module provides implementations for audio separation models based on the
python-audio-separator library which provides comprehensive source separation
capabilities using various pre-trained models.

The models support different separation architectures including VR (Vocal Remover),
MDX-Net, and HT-Demucs through the python-audio-separator library.

Example:
    Basic usage of separation models:
    
    >>> from cream.audio.models.separation import AudioSeparatorVRModel
    >>> model = AudioSeparatorVRModel(model_config)
    >>> model.load()
    >>> separated = model.separate(audio_path, output_dir)

Classes:
    SeparationModel: Abstract base class for all separation models.
    AudioSeparatorBaseModel: Base class for python-audio-separator models.
    AudioSeparatorVRModel: VR architecture model from python-audio-separator.
    AudioSeparatorMDXModel: MDX-Net architecture model.
    AudioSeparatorHTDemucsModel: HT-Demucs architecture model.
"""

from pathlib import Path
from abc import ABC, abstractmethod

from cream.core.model_factory import BaseModel
from cream.core.exceptions import ModelNotAvailableError, AudioProcessingError
from cream.core.logging import get_logger
from cream.core.config import config
from . import ModelConfig

logger = get_logger(__name__)


class SeparationModel(BaseModel, ABC):
    """Abstract base class for all audio separation models.
    
    This class provides a common interface for all separation models, ensuring
    consistency across different implementations and enabling easy extension
    with new separation models.
    
    All separation models must implement the separate method to perform
    audio source separation.
    """
    
    @abstractmethod
    def separate(self, audio_path: Path, output_dir: Path) -> list[Path]:
        """Separate audio sources from the input file.
        
        Args:
            audio_path: Path to the input audio file.
            output_dir: Directory to save separated audio files.
            
        Returns:
            List of paths to the separated audio files.
            
        Raises:
            AudioProcessingError: If separation fails.
        """
        pass


class AudioSeparatorBaseModel(SeparationModel):
    """Base class for python-audio-separator models.
    
    This class provides common functionality for all models based on the
    python-audio-separator library using the official API.
    """
    
    def __init__(self, model_config: ModelConfig) -> None:
        """Initialize the audio separator base model.
        
        Args:
            model_config: Configuration dictionary containing model parameters.
        """
        super().__init__(model_config)
        self.separator = None
    
    def load(self) -> None:
        """Load the audio separation model.
        
        Initializes the python-audio-separator with the specified model configuration.
        
        Raises:
            ModelNotAvailableError: If the model cannot be loaded.
        """
        try:
            # Import here to avoid dependency issues if library not installed
            from audio_separator.separator import Separator
            
            # Initialize separator instance  
            self.separator = Separator(
                log_level=self.config.get("log_level", "INFO"),
                log_formatter=self.config.get("log_formatter", None),
                model_file_dir=str(config.model_dir / "audio-separator"),
                output_dir=None,  # Will be set per separation call
                output_format=self.config.get("output_format", "wav"),
                normalization_threshold=self.config.get("normalization_threshold", 0.9),
                amplification_threshold=self.config.get("amplification_threshold", 0.6),
                mdx_params={
                    "hop_length": self.config.get("hop_length", 1024),
                    "segment_size": self.config.get("segment_size", 256),
                    "overlap": self.config.get("overlap", 0.25),
                    "batch_size": self.config.get("batch_size", 1),
                    "enable_denoise": self.config.get("enable_denoise", False),
                },
                vr_params={
                    "batch_size": self.config.get("vr_batch_size", 4),
                    "window_size": self.config.get("vr_window_size", 512), 
                    "aggression": self.config.get("vr_aggression", 5),
                    "enable_tta": self.config.get("vr_enable_tta", False),
                    "enable_post_process": self.config.get("vr_enable_post_process", False),
                    "post_process_threshold": self.config.get("vr_post_process_threshold", 0.2),
                    "high_end_process": self.config.get("vr_high_end_process", False),
                },
                demucs_params={
                    "segment_size": self.config.get("demucs_segment_size", "Default"),
                    "shifts": self.config.get("demucs_shifts", 2),
                    "overlap": self.config.get("demucs_overlap", 0.25),
                    "segments_enabled": self.config.get("demucs_segments_enabled", True),
                },
            )
            
            self.is_loaded = True
            logger.info("Loaded python-audio-separator")
            
        except ImportError:
            logger.error("audio_separator library not installed. Install with: pip install audio-separator")
            raise ModelNotAvailableError("audio_separator library not installed")
        except Exception as e:
            logger.exception("Failed to load python-audio-separator")
            raise ModelNotAvailableError(f"Failed to load audio-separator: {str(e)}")
    
    
    def separate(self, audio_path: Path, output_dir: Path) -> list[Path]:
        """Separate audio sources from the input file.
        
        Args:
            audio_path: Path to the input audio file.
            output_dir: Directory to save separated audio files.
            
        Returns:
            List of paths to the separated audio files.
            
        Raises:
            AudioProcessingError: If separation fails.
        """
        if not self.is_loaded:
            self.load()
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Set output directory for this separation
            self.separator.output_dir = str(output_dir)
            
            # Load the model if not already loaded
            model_filename = self.config.get("model_filename")
            if not model_filename:
                raise AudioProcessingError("model_filename not specified in configuration")
            self.separator.load_model(model_filename)
            
            # Perform separation
            primary_stem_path, secondary_stem_path = self.separator.separate(str(audio_path))
            
            # Return paths as Path objects
            output_files = []
            if primary_stem_path and Path(primary_stem_path).exists():
                output_files.append(Path(primary_stem_path))
            if secondary_stem_path and Path(secondary_stem_path).exists():
                output_files.append(Path(secondary_stem_path))
            
            logger.info(f"Successfully separated {audio_path} into {len(output_files)} stems")
            return output_files
            
        except Exception as e:
            logger.exception(f"Failed to separate audio: {audio_path}")
            raise AudioProcessingError(f"Audio separation failed: {str(e)}")


class AudioSeparatorVRModel(AudioSeparatorBaseModel):
    """VR (Vocal Remover) architecture model from python-audio-separator.
    
    This model uses the VR architecture for high-quality vocal separation.
    
    Example:
        Using VR model for separation:
        
        >>> config = {
        ...     "model_filename": "UVR_MDXNET_KARA_2.onnx",
        ...     "vr_batch_size": 4,
        ...     "vr_aggression": 5
        ... }
        >>> model = AudioSeparatorVRModel(config)
    """
    
    def __init__(self, model_config: ModelConfig) -> None:
        """Initialize VR model.
        
        Args:
            model_config: Configuration dictionary for VR model.
        """
        # Set default VR model if not specified
        if "model_filename" not in model_config:
            model_config["model_filename"] = "UVR_MDXNET_KARA_2.onnx"
        super().__init__(model_config)


class AudioSeparatorMDXModel(AudioSeparatorBaseModel):
    """MDX-Net architecture model from python-audio-separator.
    
    This model uses the MDX-Net architecture for efficient and high-quality
    source separation.
    
    Example:
        Using MDX model for separation:
        
        >>> config = {
        ...     "model_filename": "UVR-MDX-NET-Inst_HQ_3.onnx",
        ...     "segment_size": 256,
        ...     "overlap": 0.25
        ... }
        >>> model = AudioSeparatorMDXModel(config)
    """
    
    def __init__(self, model_config: ModelConfig) -> None:
        """Initialize MDX model.
        
        Args:
            model_config: Configuration dictionary for MDX model.
        """
        # Set default MDX model if not specified  
        if "model_filename" not in model_config:
            model_config["model_filename"] = "UVR-MDX-NET-Inst_HQ_3.onnx"
        super().__init__(model_config)


class AudioSeparatorHTDemucsModel(AudioSeparatorBaseModel):
    """HT-Demucs architecture model from python-audio-separator.
    
    This model uses the HT-Demucs architecture, which provides excellent
    separation quality for full-band audio separation.
    
    Example:
        Using HT-Demucs model for separation:
        
        >>> config = {
        ...     "model_filename": "htdemucs_ft.yaml", 
        ...     "demucs_shifts": 2,
        ...     "demucs_overlap": 0.25
        ... }
        >>> model = AudioSeparatorHTDemucsModel(config)
    """
    
    def __init__(self, model_config: ModelConfig) -> None:
        """Initialize HT-Demucs model.
        
        Args:
            model_config: Configuration dictionary for HT-Demucs model.
        """
        # Set default Demucs model if not specified
        if "model_filename" not in model_config:
            model_config["model_filename"] = "htdemucs_ft.yaml"
        super().__init__(model_config)


