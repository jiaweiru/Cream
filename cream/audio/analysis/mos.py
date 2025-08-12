"""MOS (Mean Opinion Score) evaluation functionality for audio quality assessment.

This module provides Mean Opinion Score (MOS) evaluation capabilities using various
deep learning models like NiSQA and UTMOSv2. MOS is a standard metric for evaluating
perceived audio quality on a scale from 1 (poor) to 5 (excellent).

The module supports single file evaluation with models loaded during initialization
to avoid repeated loading overhead.

Example:
    Basic usage for MOS evaluation:
    
    >>> from pathlib import Path
    >>> from cream.audio.analysis.mos import MOSEvaluator
    >>> 
    >>> evaluator = MOSEvaluator()
    >>> 
    >>> # Single file evaluation
    >>> score = evaluator.evaluate_file(
    ...     Path("audio.wav"),
    ...     model="nisqa"
    ... )
    >>> print(f"MOS score: {score}")

Classes:
    MOSEvaluator: Main class for MOS evaluation operations.
"""

from pathlib import Path

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError
from cream.core.logging import get_logger

logger = get_logger(__name__)


class MOSEvaluator:
    """MOS evaluation processor using various deep learning models.
    
    This class provides methods for evaluating Mean Opinion Score (MOS) of audio
    files using different deep learning models such as NiSQA and UTMOSv2. The models
    are loaded during initialization to avoid repeated loading overhead.
    
    The evaluator validates input file formats, checks model availability, and
    includes comprehensive error handling and logging for all operations.
    
    Attributes:
        models (dict): Dictionary containing loaded MOS models.
    
    Example:
        Creating and using a MOS evaluator:
        
        >>> evaluator = MOSEvaluator()
        >>> score = evaluator.evaluate_file(
        ...     Path("speech_sample.wav"),
        ...     model="nisqa"
        ... )
        >>> print(f"Audio quality score: {score}/5.0")
    """
    
    def __init__(self) -> None:
        """Initialize the MOS evaluator.
        
        Loads available MOS models during initialization to avoid repeated
        loading overhead during evaluation operations.
        """
        self.models = self._load_models()
    
    def _load_models(self) -> dict[str, object]:
        """Load and initialize MOS models.
        
        Returns:
            Dictionary containing loaded model instances.
        """
        models = {}
        
        # Load NiSQA model if enabled
        nisqa_config = config.get_model_config("mos", "nisqa")
        if nisqa_config.get("enabled", False):
            try:
                # TODO: Replace with actual model loading
                # models["nisqa"] = load_nisqa_model(nisqa_config)
                models["nisqa"] = "mock_nisqa_model"
                logger.info("NiSQA model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load NiSQA model: {e}")
        
        # Load UTMOSv2 model if enabled
        utmosv2_config = config.get_model_config("mos", "utmosv2")
        if utmosv2_config.get("enabled", False):
            try:
                # TODO: Replace with actual model loading
                # models["utmosv2"] = load_utmosv2_model(utmosv2_config)
                models["utmosv2"] = "mock_utmosv2_model"
                logger.info("UTMOSv2 model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load UTMOSv2 model: {e}")
        
        return models
    
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
        
        if model not in self.models:
            logger.error(f"MOS model {model} is not available or failed to load")
            raise ModelNotAvailableError(f"MOS model {model} is not available or failed to load")
        
        try:
            # Placeholder for actual MOS evaluation
            # In real implementation, this would use the loaded model from self.models[model]
            logger.info(f"Evaluating MOS for {audio_path} using {model}")
            loaded_model = self.models[model]
            
            # Mock MOS score (1-5 scale)
            import random
            random.seed(hash(str(audio_path)) % 2147483647)  # Deterministic for same file
            mock_score = random.uniform(2.5, 4.8)
            
            return round(mock_score, 2)
            
        except Exception as e:
            logger.exception(f"Failed to evaluate MOS for {audio_path}")
            raise AudioProcessingError(f"Failed to evaluate MOS for {audio_path}: {str(e)}")
    
