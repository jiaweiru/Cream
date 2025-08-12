"""ASR (Automatic Speech Recognition) model implementations.

This module provides implementations for ASR models based on the
FunASR toolkit for comprehensive Chinese speech recognition capabilities
using official APIs.

The models support the Paraformer architecture from FunASR toolkit.

Example:
    Basic usage of ASR models:
    
    >>> from cream.audio.models.asr import ParaformerZhModel
    >>> model = ParaformerZhModel(model_config)
    >>> model.load()
    >>> result = model.recognize(audio_path)

Classes:
    ASRModel: Abstract base class for all ASR models.
    ParaformerZhModel: Chinese Paraformer model from FunASR.
"""

from pathlib import Path
from abc import ABC, abstractmethod

from cream.core.model_factory import BaseModel
from cream.core.exceptions import ModelNotAvailableError, AudioProcessingError
from cream.core.logging import get_logger
from cream.core.config import config
from . import ModelConfig

logger = get_logger(__name__)


class ASRModel(BaseModel, ABC):
    """Abstract base class for all ASR (Automatic Speech Recognition) models.
    
    This class provides a common interface for all ASR models, ensuring
    consistency across different implementations and enabling easy extension
    with new ASR models.
    
    All ASR models must implement the recognize method to perform speech
    recognition on audio files.
    """
    
    @abstractmethod
    def recognize(self, audio_path: Path) -> dict[str, str | float | list]:
        """Perform speech recognition on audio file.
        
        Args:
            audio_path: Path to the input audio file.
            
        Returns:
            Dictionary containing recognition results with keys:
            - text: Recognized text
            - confidence: Recognition confidence score
            - timestamp: Word-level timestamps (if available)
            - language: Detected or specified language
            - model: Model name used for recognition
            
        Raises:
            AudioProcessingError: If recognition fails.
        """
        pass


class ParaformerZhModel(ASRModel):
    """Chinese Paraformer ASR model from FunASR using official API.
    
    This model provides high-quality Chinese speech recognition using the
    Paraformer architecture from the FunASR toolkit with integrated VAD and
    punctuation restoration.
    
    Example:
        Using Paraformer for Chinese speech recognition:
        
        >>> config = {
        ...     "model": "paraformer-zh",
        ...     "vad_model": "fsmn-vad", 
        ...     "punc_model": "ct-punc",
        ...     "device": "cpu"
        ... }
        >>> model = ParaformerZhModel(config)
        >>> model.load()
        >>> result = model.recognize(audio_path)
        >>> print(result["text"])
    """
    
    def __init__(self, model_config: ModelConfig) -> None:
        """Initialize Paraformer model.
        
        Args:
            model_config: Configuration dictionary for Paraformer model.
        """
        super().__init__(model_config)
        self.model = None
        self.model_name = self.config.get("model", "paraformer-zh")
        self.vad_model = self.config.get("vad_model", "fsmn-vad")
        self.punc_model = self.config.get("punc_model", "ct-punc")
        self.device = self.config.get("device", "cpu")
    
    def load(self) -> None:
        """Load the Paraformer ASR model using FunASR AutoModel.
        
        Raises:
            ModelNotAvailableError: If FunASR cannot be loaded.
        """
        try:
            from funasr import AutoModel
            
            # Initialize the model with VAD and punctuation
            # Following official FunASR API
            self.model = AutoModel(
                model=self.model_name,
                vad_model=self.vad_model,
                vad_kwargs={"max_single_segment_time": self.config.get("max_single_segment_time", 60000)},
                punc_model=self.punc_model,
                device=self.device,
                disable_update=self.config.get("disable_update", True),
                disable_log=self.config.get("disable_log", False),
                cache_dir=str(config.model_dir / "funasr"),
            )
            
            self.is_loaded = True
            logger.info(f"Loaded FunASR Paraformer model: {self.model_name}")
            
        except ImportError:
            logger.error("FunASR library not installed. Install with: pip install funasr")
            raise ModelNotAvailableError("FunASR library not installed")
        except Exception as e:
            logger.exception("Failed to load FunASR Paraformer model")
            raise ModelNotAvailableError(f"Failed to load Paraformer model: {str(e)}")
    
    
    def recognize(self, audio_path: Path) -> dict[str, str | float | list]:
        """Perform speech recognition on audio file.
        
        Args:
            audio_path: Path to the input audio file.
            
        Returns:
            Dictionary containing recognition results with keys:
            - text: Recognized text
            - confidence: Recognition confidence score
            - timestamp: Word-level timestamps (if available)
            - language: Detected language
            - model: Model name used
            
        Raises:
            AudioProcessingError: If recognition fails.
        """
        if not self.is_loaded:
            self.load()
        
        try:
            # Perform recognition using FunASR API
            # Following official documentation patterns
            result = self.model.generate(
                input=str(audio_path),
                batch_size_s=self.config.get("batch_size_s", 300),
                batch_size_threshold_s=self.config.get("batch_size_threshold_s", 60),
                hotword=self.config.get("hotword", "")
            )
            
            # Extract results from FunASR output format
            if isinstance(result, list) and len(result) > 0:
                recognition_result = result[0]
                
                # Get text result
                if isinstance(recognition_result, dict):
                    text = recognition_result.get("text", "")
                    # FunASR may provide confidence in different formats
                    confidence = recognition_result.get("confidence", recognition_result.get("score", 1.0))
                    timestamp = recognition_result.get("timestamp", [])
                else:
                    # If result is just string
                    text = str(recognition_result)
                    confidence = 1.0
                    timestamp = []
            else:
                # Fallback for different result formats
                text = str(result) if result else ""
                confidence = 1.0 if text else 0.0
                timestamp = []
            
            return {
                "text": text,
                "confidence": float(confidence),
                "timestamp": timestamp,
                "language": "zh",
                "model": self.model_name
            }
            
        except Exception as e:
            logger.exception(f"Failed to recognize audio: {audio_path}")
            raise AudioProcessingError(f"ASR recognition failed: {str(e)}")


