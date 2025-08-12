"""Audio enhancement model implementations.

This module provides implementations for audio enhancement models
based on ClearerVoice-Studio using the FRCRN model following
official ModelScope API patterns.

Example:
    Basic usage of FRCRN enhancement model:
    
    >>> from cream.audio.models.enhancement import FRCRNModel
    >>> model = FRCRNModel(model_config)
    >>> model.load()
    >>> enhanced = model.enhance(audio_path, output_path)

Classes:
    EnhancementModel: Abstract base class for all enhancement models.
    FRCRNModel: FRCRN speech denoising model from ClearerVoice-Studio via ModelScope.
"""

from pathlib import Path
from abc import ABC, abstractmethod

from cream.core.model_factory import BaseModel
from cream.core.exceptions import ModelNotAvailableError, AudioProcessingError
from cream.core.logging import get_logger
from cream.core.config import config
from . import ModelConfig

logger = get_logger(__name__)


class EnhancementModel(BaseModel, ABC):
    """Abstract base class for all audio enhancement models.
    
    This class provides a common interface for all enhancement models, ensuring
    consistency across different implementations and enabling easy extension
    with new enhancement models.
    
    All enhancement models must implement the enhance method to perform
    audio enhancement and noise reduction.
    """
    
    @abstractmethod
    def enhance(self, audio_path: Path, output_path: Path) -> bool:
        """Enhance audio quality and reduce noise.
        
        Args:
            audio_path: Path to the input audio file.
            output_path: Path to save the enhanced audio file.
            
        Returns:
            True if enhancement was successful, False otherwise.
            
        Raises:
            AudioProcessingError: If enhancement fails.
        """
        pass


class FRCRNModel(EnhancementModel):
    """FRCRN speech denoising model from ClearerVoice-Studio via ModelScope.
    
    This model uses the FRCRN (Fast Residual Convolutional Recurrent Network) architecture
    for high-quality speech denoising and enhancement. The model has been used over 3 million
    times on ModelScope and provides excellent noise suppression capabilities.
    
    Example:
        Using FRCRN model for speech enhancement:
        
        >>> config = {
        ...     "model_id": "damo/speech_frcrn_ans_cirm_16k",
        ...     "sample_rate": 16000
        ... }
        >>> model = FRCRNModel(config)
        >>> model.load()
        >>> enhanced = model.enhance(audio_path, output_path)
    """
    
    def __init__(self, model_config: ModelConfig) -> None:
        """Initialize FRCRN model.
        
        Args:
            model_config: Configuration dictionary for FRCRN model.
        """
        super().__init__(model_config)
        self.model = None
        self.model_id = self.config.get("model_id", "damo/speech_frcrn_ans_cirm_16k")
        self.sample_rate = self.config.get("sample_rate", 16000)
    
    def load(self) -> None:
        """Load the FRCRN enhancement model using ModelScope API.
        
        Initializes the FRCRN model through ModelScope pipeline for acoustic noise suppression.
        
        Raises:
            ModelNotAvailableError: If the model cannot be loaded.
        """
        try:
            # Import ModelScope pipeline for acoustic noise suppression
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            
            # Initialize FRCRN model using official ModelScope API
            self.model = pipeline(
                Tasks.acoustic_noise_suppression,
                model=self.model_id,
                cache_dir=str(config.model_dir / "modelscope")
            )
            
            self.is_loaded = True
            logger.info(f"Loaded FRCRN model: {self.model_id}")
            
        except ImportError:
            logger.error("modelscope library not installed. Install with: pip install modelscope")
            raise ModelNotAvailableError("modelscope library not installed")
        except Exception as e:
            logger.exception(f"Failed to load FRCRN model: {self.model_id}")
            raise ModelNotAvailableError(f"Failed to load FRCRN model: {str(e)}")
    
    
    def enhance(self, audio_path: Path, output_path: Path) -> bool:
        """Enhance audio quality using FRCRN.
        
        Args:
            audio_path: Path to the input audio file.
            output_path: Path to save the enhanced audio file.
            
        Returns:
            True if enhancement was successful.
            
        Raises:
            AudioProcessingError: If enhancement fails.
        """
        if not self.is_loaded:
            self.load()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Enhance audio using FRCRN model following official API
            self.model(
                str(audio_path),
                output_path=str(output_path)
            )
            
            # Check if enhancement was successful
            if output_path.exists():
                logger.info(f"Successfully enhanced {audio_path} -> {output_path}")
                return True
            else:
                logger.error(f"Enhancement failed: output file not created at {output_path}")
                return False
            
        except Exception as e:
            logger.exception(f"Failed to enhance audio: {audio_path}")
            raise AudioProcessingError(f"FRCRN enhancement failed: {str(e)}")