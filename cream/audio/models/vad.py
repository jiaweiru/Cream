"""Voice Activity Detection (VAD) model implementations.

This module provides implementations for VAD models based on the
FunASR toolkit for comprehensive voice activity detection capabilities.

The models support the FSMN-VAD architecture from FunASR toolkit.

Example:
    Basic usage of VAD models:
    
    >>> from cream.audio.models.vad import FunASRVADModel
    >>> model = FunASRVADModel(model_config)
    >>> model.load()
    >>> segments = model.detect_voice_activity(audio_path)

Classes:
    VADModel: Abstract base class for all VAD models.
    FunASRVADModel: FSMN-VAD model from FunASR toolkit.
"""

from pathlib import Path
from abc import ABC, abstractmethod

from cream.core.model_factory import BaseModel
from cream.core.exceptions import ModelNotAvailableError, AudioProcessingError
from cream.core.logging import get_logger
from cream.core.config import config
from . import ModelConfig

logger = get_logger(__name__)


class VADModel(BaseModel, ABC):
    """Abstract base class for all VAD (Voice Activity Detection) models.
    
    This class provides a common interface for all VAD models, ensuring
    consistency across different implementations and enabling easy extension
    with new VAD models.
    
    All VAD models must implement the detect_voice_activity method to perform
    voice activity detection on audio files.
    """
    
    @abstractmethod
    def detect_voice_activity(self, audio_path: Path) -> list[dict[str, float]]:
        """Perform voice activity detection on audio file.
        
        Args:
            audio_path: Path to the input audio file.
            
        Returns:
            List of dictionaries containing voice activity segments with keys:
            - start: Start time in seconds
            - end: End time in seconds
            - confidence: Detection confidence score
            
        Raises:
            AudioProcessingError: If VAD detection fails.
        """
        pass


class FunASRVADModel(VADModel):
    """FSMN-VAD model from FunASR toolkit using official API.
    
    This model provides high-quality voice activity detection using the
    FSMN (Feed-forward Sequential Memory Network) architecture from the
    FunASR toolkit, particularly effective for Chinese and multilingual VAD.
    
    Example:
        Using FunASR VAD for voice activity detection:
        
        >>> config = {
        ...     "model": "fsmn-vad",
        ...     "device": "cpu",
        ...     "batch_size": 1
        ... }
        >>> model = FunASRVADModel(config)
        >>> model.load()
        >>> segments = model.detect_voice_activity(audio_path)
        >>> for segment in segments:
        ...     print(f"Speech: {segment['start']:.2f}s - {segment['end']:.2f}s")
    """
    
    def __init__(self, model_config: ModelConfig) -> None:
        """Initialize FunASR VAD model.
        
        Args:
            model_config: Configuration dictionary for FunASR VAD model.
        """
        super().__init__(model_config)
        self.model = None
        self.model_name = self.config.get("model", "fsmn-vad")
        self.device = self.config.get("device", "cpu")
        self.batch_size = self.config.get("batch_size", 1)
    
    def load(self) -> None:
        """Load the FunASR VAD model using AutoModel.
        
        Raises:
            ModelNotAvailableError: If FunASR cannot be loaded.
        """
        try:
            from funasr import AutoModel
            
            # Initialize the VAD model following official FunASR API
            self.model = AutoModel(
                model=self.model_name,
                device=self.device,
                batch_size=self.batch_size,
                disable_update=self.config.get("disable_update", True),
                disable_log=self.config.get("disable_log", False),
                cache_dir=str(config.model_dir / "funasr"),
            )
            
            self.is_loaded = True
            logger.info(f"Loaded FunASR VAD model: {self.model_name}")
            
        except ImportError:
            logger.error("FunASR library not installed. Install with: pip install funasr")
            raise ModelNotAvailableError("FunASR library not installed")
        except Exception as e:
            logger.exception("Failed to load FunASR VAD model")
            raise ModelNotAvailableError(f"Failed to load FunASR VAD model: {str(e)}")
    
    
    def detect_voice_activity(self, audio_path: Path) -> list[dict[str, float]]:
        """Perform voice activity detection on audio file.
        
        Args:
            audio_path: Path to the input audio file.
            
        Returns:
            List of dictionaries containing voice activity segments with keys:
            - start: Start time in seconds
            - end: End time in seconds
            - confidence: Detection confidence score
            
        Raises:
            AudioProcessingError: If VAD detection fails.
        """
        if not self.is_loaded:
            self.load()
        
        try:
            # Perform VAD detection using FunASR API
            result = self.model.generate(input=str(audio_path))
            
            # Parse FunASR VAD results
            segments = []
            if isinstance(result, list) and len(result) > 0:
                vad_result = result[0]
                
                # FunASR VAD returns segments with timestamps
                if isinstance(vad_result, dict) and "value" in vad_result:
                    # Standard FunASR VAD output format
                    for segment_info in vad_result["value"]:
                        if len(segment_info) >= 2:
                            start_time = float(segment_info[0]) / 1000.0  # Convert ms to seconds
                            end_time = float(segment_info[1]) / 1000.0
                            confidence = float(segment_info[2]) if len(segment_info) > 2 else 1.0
                            
                            segments.append({
                                "start": start_time,
                                "end": end_time,
                                "confidence": confidence
                            })
                elif isinstance(vad_result, dict) and "text" in vad_result:
                    # Fallback: if no detailed timestamps but has text, create single segment
                    if vad_result["text"].strip():
                        segments.append({
                            "start": 0.0,
                            "end": self._get_audio_duration(audio_path),
                            "confidence": 1.0
                        })
                else:
                    # Try to parse other possible formats
                    logger.warning(f"Unexpected VAD result format: {type(vad_result)}")
            
            logger.info(f"Detected {len(segments)} voice activity segments in {audio_path}")
            return segments
            
        except Exception as e:
            logger.exception(f"Failed to detect voice activity: {audio_path}")
            raise AudioProcessingError(f"VAD detection failed: {str(e)}")
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get audio file duration in seconds."""
        try:
            import librosa
            duration = librosa.get_duration(path=str(audio_path))
            return float(duration)
        except ImportError:
            logger.warning("librosa not available for duration calculation, using default")
            return 10.0  # Default duration
        except Exception:
            logger.warning(f"Failed to get duration for {audio_path}, using default")
            return 10.0


