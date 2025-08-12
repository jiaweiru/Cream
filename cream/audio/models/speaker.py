"""Speaker recognition model implementations.

This module provides implementations for speaker recognition models based on the
3D-Speaker toolkit through ModelScope for comprehensive speaker recognition
capabilities using official APIs.

Example:
    Basic usage of speaker models:
    
    >>> from cream.audio.models.speaker import Speaker3DCamPlusPlusModel
    >>> model = Speaker3DCamPlusPlusModel(model_config)
    >>> model.load()
    >>> embedding = model.extract_embedding(audio_path)

Classes:
    SpeakerModel: Abstract base class for all speaker recognition models.
    Speaker3DBaseModel: Base class for 3D-Speaker models via ModelScope.
    Speaker3DCamPlusPlusModel: CAM++ model from 3D-Speaker toolkit.
    Speaker3DERes2NetV2Model: ERes2NetV2 model from 3D-Speaker toolkit.
"""

import numpy as np
from pathlib import Path
from abc import ABC, abstractmethod

from cream.core.model_factory import BaseModel
from cream.core.exceptions import ModelNotAvailableError, AudioProcessingError
from cream.core.logging import get_logger
from cream.core.config import config
from . import ModelConfig

logger = get_logger(__name__)


class SpeakerModel(BaseModel, ABC):
    """Abstract base class for all speaker recognition models.
    
    This class provides a common interface for all speaker models, ensuring
    consistency across different implementations and enabling easy extension
    with new speaker recognition models.
    
    All speaker models must implement methods for speaker embedding extraction,
    verification, and identification tasks.
    """
    
    @abstractmethod
    def extract_embedding(self, audio_path: Path) -> list[float]:
        """Extract speaker embedding from audio file.
        
        Args:
            audio_path: Path to the input audio file.
            
        Returns:
            List of floats representing the speaker embedding vector.
            
        Raises:
            AudioProcessingError: If embedding extraction fails.
        """
        pass
    
    def verify_speaker(self, audio1_path: Path, audio2_path: Path) -> dict[str, float]:
        """Verify if two audio files contain the same speaker.
        
        Args:
            audio1_path: Path to the first audio file.
            audio2_path: Path to the second audio file.
            
        Returns:
            Dictionary containing verification results with keys:
            - similarity: Similarity score between speakers
            - is_same_speaker: Boolean indicating if same speaker
            - confidence: Confidence score of the verification
            
        Raises:
            AudioProcessingError: If verification fails.
        """
        # Default implementation using embeddings
        try:
            emb1 = self.extract_embedding(audio1_path)
            emb2 = self.extract_embedding(audio2_path)
            
            # Calculate cosine similarity
            emb1_array = np.array(emb1)
            emb2_array = np.array(emb2)
            
            similarity = np.dot(emb1_array, emb2_array) / (
                np.linalg.norm(emb1_array) * np.linalg.norm(emb2_array)
            )
            
            # Threshold for same speaker (can be configured)
            threshold = 0.7
            is_same_speaker = similarity > threshold
            
            return {
                "similarity": float(similarity),
                "is_same_speaker": is_same_speaker,
                "confidence": float(abs(similarity - threshold))
            }
            
        except Exception as e:
            raise AudioProcessingError(f"Speaker verification failed: {str(e)}")


class Speaker3DBaseModel(SpeakerModel):
    """Base class for 3D-Speaker models using ModelScope API.
    
    This class provides common functionality for all models based on the
    3D-Speaker toolkit through ModelScope, following the official API patterns.
    
    Attributes:
        model: The ModelScope inference pipeline instance.
        model_id: ModelScope model identifier.
    """
    
    def __init__(self, model_config: ModelConfig) -> None:
        """Initialize the 3D-Speaker base model.
        
        Args:
            model_config: Configuration dictionary containing model parameters.
        """
        super().__init__(model_config)
        self.model = None
        self.model_id = self.config.get("model_id", "")
    
    def load(self) -> None:
        """Load the 3D-Speaker model using ModelScope API.
        
        Initializes the 3D-Speaker model through ModelScope inference pipeline.
        
        Raises:
            ModelNotAvailableError: If the model cannot be loaded.
        """
        try:
            # Import here to avoid dependency issues if library not installed
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            
            # Use the pipeline for speaker verification/embedding extraction
            self.model = pipeline(
                Tasks.speaker_verification,
                model=self.model_id,
                device=self.config.get("device", "cpu"),
                cache_dir=str(config.model_dir / "modelscope")
            )
            
            self.is_loaded = True
            logger.info(f"Loaded 3D-Speaker model: {self.model_id}")
            
        except ImportError:
            logger.error("modelscope library not installed. Install with: pip install modelscope")
            raise ModelNotAvailableError("modelscope library not installed")
        except Exception as e:
            logger.exception(f"Failed to load 3D-Speaker model: {self.model_id}")
            raise ModelNotAvailableError(f"Failed to load 3D-Speaker model: {str(e)}")
    
    
    def extract_embedding(self, audio_path: Path) -> list[float]:
        """Extract speaker embedding from audio file.
        
        Args:
            audio_path: Path to the input audio file.
            
        Returns:
            List of floats representing the speaker embedding vector.
            
        Raises:
            AudioProcessingError: If embedding extraction fails.
        """
        if not self.is_loaded:
            self.load()
        
        try:
            # Use ModelScope pipeline for embedding extraction
            result = self.model(str(audio_path))
            
            # Extract embedding from result
            if isinstance(result, dict) and 'spk_embedding' in result:
                embedding = result['spk_embedding']
            elif hasattr(result, 'embedding'):
                embedding = result.embedding
            else:
                # Fallback: assume result is the embedding
                embedding = result
            
            # Convert to list if numpy array
            if isinstance(embedding, np.ndarray):
                embedding = embedding.flatten().tolist()
            elif not isinstance(embedding, list):
                embedding = [float(embedding)]
            
            logger.info(f"Successfully extracted embedding for {audio_path}")
            return embedding
            
        except Exception as e:
            logger.exception(f"Failed to extract embedding: {audio_path}")
            raise AudioProcessingError(f"Embedding extraction failed: {str(e)}")


class Speaker3DCamPlusPlusModel(Speaker3DBaseModel):
    """CAM++ speaker recognition model from 3D-Speaker toolkit via ModelScope.
    
    This model uses the CAM++ (Channel and Spatial Attention Module++) architecture
    for high-quality speaker embedding extraction and recognition.
    
    Example:
        Using CAM++ model for speaker embedding:
        
        >>> config = {
        ...     "model_id": "iic/speech_campplus_sv_zh-cn_16k-common",
        ...     "device": "cpu"
        ... }
        >>> model = Speaker3DCamPlusPlusModel(config)
        >>> model.load()
        >>> embedding = model.extract_embedding(audio_path)
    """
    
    def __init__(self, model_config: ModelConfig) -> None:
        """Initialize CAM++ model.
        
        Args:
            model_config: Configuration dictionary for CAM++ model.
        """
        # Set default CAM++ model ID if not specified
        if "model_id" not in model_config:
            model_config["model_id"] = "iic/speech_campplus_sv_zh-cn_16k-common"
        super().__init__(model_config)


class Speaker3DERes2NetV2Model(Speaker3DBaseModel):
    """ERes2NetV2 speaker recognition model from 3D-Speaker toolkit via ModelScope.
    
    This model uses the ERes2NetV2 (Enhanced Res2Net V2) architecture
    for efficient and accurate speaker embedding extraction.
    
    Example:
        Using ERes2NetV2 model for speaker embedding:
        
        >>> config = {
        ...     "model_id": "iic/speech_eres2netv2_sv_zh-cn_16k-common",
        ...     "device": "cpu"
        ... }
        >>> model = Speaker3DERes2NetV2Model(config)
        >>> model.load()
        >>> embedding = model.extract_embedding(audio_path)
    """
    
    def __init__(self, model_config: ModelConfig) -> None:
        """Initialize ERes2NetV2 model.
        
        Args:
            model_config: Configuration dictionary for ERes2NetV2 model.
        """
        # Set default ERes2NetV2 model ID if not specified
        if "model_id" not in model_config:
            model_config["model_id"] = "iic/speech_eres2netv2_sv_zh-cn_16k-common"
        super().__init__(model_config)