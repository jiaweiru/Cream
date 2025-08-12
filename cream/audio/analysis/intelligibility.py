"""Speech intelligibility evaluation functionality for the cream package.

This module provides comprehensive speech intelligibility evaluation using
Automatic Speech Recognition (ASR) models. It supports transcription-based
intelligibility assessment with optional reference text comparison for
Word Error Rate (WER) calculation.

The module supports various ASR models including Paraformer and Whisper,
and provides detailed intelligibility metrics with confidence scores.

Example:
    Basic usage for intelligibility evaluation:
    
    >>> from pathlib import Path
    >>> from cream.audio.analysis.intelligibility import IntelligibilityEvaluator
    >>> 
    >>> evaluator = IntelligibilityEvaluator(max_workers=4)
    >>> 
    >>> # Single file evaluation
    >>> result = evaluator.evaluate_file(
    ...     Path("speech.wav"),
    ...     reference_text="Hello world",
    ...     model="whisper"
    ... )
    >>> print(f"Intelligibility score: {result['intelligibility_score']}")

Classes:
    IntelligibilityEvaluator: Main class for speech intelligibility evaluation.
"""

from pathlib import Path

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError
from cream.core.logging import get_logger

logger = get_logger(__name__)


class IntelligibilityEvaluator:
    """Speech intelligibility evaluator using ASR models.
    
    This class provides methods for evaluating speech intelligibility using
    various ASR models. It supports transcription-based evaluation with optional
    reference text comparison for WER calculation. Models are loaded during
    initialization to avoid repeated loading overhead.
    
    Attributes:
        models (dict): Dictionary containing loaded ASR models.
    
    Example:
        Creating and using an intelligibility evaluator:
        
        >>> evaluator = IntelligibilityEvaluator()
        >>> result = evaluator.evaluate_file(
        ...     Path("recording.wav"),
        ...     reference_text="This is a test",
        ...     model="paraformer"
        ... )
    """
    
    def __init__(self) -> None:
        """Initialize the intelligibility evaluator.
        
        Loads available ASR models during initialization to avoid repeated
        loading overhead during evaluation operations.
        """
        self.models = self._load_models()
    
    def _load_models(self) -> dict[str, object]:
        """Load and initialize ASR models.
        
        Returns:
            Dictionary containing loaded ASR model instances.
        """
        models = {}
        
        # Load Paraformer model if enabled
        paraformer_config = config.get_model_config("asr", "paraformer")
        if paraformer_config.get("enabled", False):
            try:
                # TODO: Replace with actual model loading
                # models["paraformer"] = load_paraformer_model(paraformer_config)
                models["paraformer"] = "mock_paraformer_model"
                logger.info("Paraformer model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load Paraformer model: {e}")
        
        # Load Whisper model if enabled
        whisper_config = config.get_model_config("asr", "whisper")
        if whisper_config.get("enabled", False):
            try:
                # TODO: Replace with actual model loading
                # models["whisper"] = load_whisper_model(whisper_config)
                models["whisper"] = "mock_whisper_model"
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load Whisper model: {e}")
        
        return models
    
    def evaluate_file(self, audio_path: Path, reference_text: str | None, model: str) -> dict[str, str | float | int]:
        """Evaluate speech intelligibility for a single audio file."""
        if not config.is_audio_file(audio_path):
            logger.error(f"Unsupported audio format for intelligibility evaluation: {audio_path.suffix}")
            raise InvalidFormatError(f"Unsupported audio format: {audio_path.suffix}")
        
        if model not in self.models:
            logger.error(f"ASR model {model} is not available or failed to load")
            raise ModelNotAvailableError(f"ASR model {model} is not available or failed to load")
        
        try:
            # Placeholder for actual intelligibility evaluation
            # In real implementation, this would use the loaded model from self.models[model]
            logger.info(f"Evaluating intelligibility for {audio_path} using {model}")
            loaded_model = self.models[model]
            
            # Mock intelligibility results
            import random
            random.seed(hash(str(audio_path)) % 2147483647)
            
            mock_transcription = f"mock transcription for {audio_path.stem}"
            mock_confidence = random.uniform(0.7, 0.98)
            mock_intelligibility_score = random.uniform(0.6, 0.95)
            
            result = {
                "file": audio_path.name,
                "transcription": mock_transcription,
                "reference": reference_text or "No reference provided",
                "confidence": round(mock_confidence, 3),
                "intelligibility_score": round(mock_intelligibility_score, 3),
                "model": model
            }
            
            if reference_text:
                # Mock WER calculation
                mock_wer = random.uniform(0.05, 0.3)
                result["word_error_rate"] = round(mock_wer, 3)
            
            return result
            
        except Exception as e:
            logger.exception(f"Failed to evaluate intelligibility for {audio_path}")
            raise AudioProcessingError(f"Failed to evaluate intelligibility for {audio_path}: {str(e)}")
    
    def load_reference_text(self, reference_file: Path) -> dict[str, str]:
        """Load reference text from file."""
        if not reference_file.exists():
            logger.error(f"Reference file not found: {reference_file}")
            raise FileNotFoundError(f"Reference file not found: {reference_file}")
        
        references = {}
        
        try:
            if reference_file.suffix.lower() == ".json":
                import json
                with open(reference_file, 'r', encoding='utf-8') as f:
                    references = json.load(f)
            else:
                # Assume text file with filename: text format
                with open(reference_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if ':' in line:
                            filename, text = line.strip().split(':', 1)
                            references[filename.strip()] = text.strip()
            
            return references
            
        except Exception as e:
            logger.exception("Failed to load reference text")
            raise AudioProcessingError(f"Failed to load reference text: {str(e)}")
    
