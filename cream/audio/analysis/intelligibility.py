"""Speech intelligibility evaluation functionality for the cream package.

This module provides comprehensive speech intelligibility evaluation using
Automatic Speech Recognition (ASR) models from FunASR and OpenAI Whisper.
It supports transcription-based intelligibility assessment with optional
reference text comparison for Word Error Rate (WER) calculation.

The module now uses a factory pattern for extensible ASR model management,
supporting FunASR Paraformer-zh for Chinese speech recognition and Whisper
for multilingual recognition.

Example:
    Basic usage for intelligibility evaluation:
    
    >>> from pathlib import Path
    >>> from cream.audio.analysis.intelligibility import IntelligibilityEvaluator
    >>> 
    >>> evaluator = IntelligibilityEvaluator(max_workers=4)
    >>> 
    >>> # Chinese speech evaluation using Paraformer
    >>> result = evaluator.evaluate_file(
    ...     Path("chinese_speech.wav"),
    ...     reference_text="你好世界",
    ...     model="paraformer-zh"
    ... )
    >>> 
    >>> # Multilingual evaluation using Whisper
    >>> result = evaluator.evaluate_file(
    ...     Path("english_speech.wav"),
    ...     reference_text="Hello world",
    ...     model="whisper"
    ... )
    >>> print(f"Intelligibility score: {result['intelligibility_score']}")

Classes:
    IntelligibilityEvaluator: Main class for speech intelligibility evaluation.
"""

from pathlib import Path
import difflib

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError
from cream.core.logging import get_logger
from cream.core.model_factory import asr_factory

logger = get_logger(__name__)


class IntelligibilityEvaluator:
    """Speech intelligibility evaluator using multiple ASR models.
    
    This class provides methods for evaluating speech intelligibility using
    various ASR models including FunASR Paraformer-zh and OpenAI Whisper.
    It supports transcription-based evaluation with optional reference text
    comparison for Word Error Rate (WER) calculation.
    
    Models are managed through a factory pattern for extensibility and
    support both single file and batch directory processing with configurable
    multi-threading for efficient parallel processing.
    
    Attributes:
        available_models: List of available ASR model names.
        default_model: Default ASR model if none specified.
    
    Example:
        Creating and using an intelligibility evaluator:
        
        >>> evaluator = IntelligibilityEvaluator()
        >>> 
        >>> # Chinese speech evaluation
        >>> result = evaluator.evaluate_file(
        ...     Path("chinese_recording.wav"),
        ...     reference_text="这是一个测试",
        ...     model="paraformer-zh"
        ... )
        >>> 
        >>> # English speech evaluation
        >>> result = evaluator.evaluate_file(
        ...     Path("english_recording.wav"),
        ...     reference_text="This is a test",
        ...     model="whisper"
        ... )
    """
    
    def __init__(self) -> None:
        """Initialize the intelligibility evaluator."""
        self._model_instances = {}
        self.available_models = asr_factory.list_models()
        
        if not self.available_models:
            logger.warning(
                "No ASR models are available. Check model configuration."
            )
        else:
            logger.info(f"Available ASR models: {self.available_models}")
        
        self.default_model = (
            self.available_models[0] if self.available_models else None
        )
    
    def _get_model(self, model_name: str):
        """Get or create ASR model instance for the specified model.
        
        Args:
            model_name: Name of the ASR model.
            
        Returns:
            Model instance ready for recognition.
            
        Raises:
            ModelNotAvailableError: If the model is not available or fails to load.
        """
        if model_name in self._model_instances:
            return self._model_instances[model_name]

        # Get model configuration from config
        model_config = config.get_model_config("asr", model_name)
        if not model_config and model_name not in self.available_models:
            # If not in config, create default config for factory models
            model_config = {"enabled": True}
        
        if not model_config.get("enabled", True):
            raise ModelNotAvailableError(
                f"ASR model {model_name} is not enabled"
            )

        try:
            # Create model using factory
            model = asr_factory.create_model(model_name, model_config)
            self._model_instances[model_name] = model
            logger.info(f"Created ASR model: {model_name}")
            return model

        except Exception as e:
            logger.exception(f"Failed to create ASR model {model_name}")
            raise ModelNotAvailableError(
                f"Failed to create ASR model {model_name}: {str(e)}"
            )
    
    def evaluate_file(self, audio_path: Path, reference_text: str | None, model: str) -> dict[str, str | float | int]:
        """Evaluate speech intelligibility for a single audio file.
        
        Args:
            audio_path: Path to the input audio file.
            reference_text: Reference text for WER calculation (optional).
            model: ASR model name to use for evaluation.
            
        Returns:
            Dictionary containing evaluation results with keys:
            - file: Audio file name
            - transcription: ASR transcription result
            - reference: Reference text (if provided)
            - confidence: ASR confidence score
            - intelligibility_score: Calculated intelligibility score
            - word_error_rate: WER if reference text provided
            - model: Model name used
            
        Raises:
            InvalidFormatError: If audio file format is not supported.
            ModelNotAvailableError: If the specified model is not available.
            AudioProcessingError: If evaluation fails.
        """
        if not config.is_audio_file(audio_path):
            logger.error(f"Unsupported audio format for intelligibility evaluation: {audio_path.suffix}")
            raise InvalidFormatError(f"Unsupported audio format: {audio_path.suffix}")
        
        # Use default model if none specified and available
        if not model and self.default_model:
            model = self.default_model
            logger.info(f"Using default ASR model: {model}")
        
        # Check if model is available
        if model not in self.available_models:
            logger.error(f"ASR model {model} is not available")
            raise ModelNotAvailableError(f"ASR model {model} is not available")
        
        try:
            # Get model instance and perform recognition
            asr_model = self._get_model(model)
            
            logger.info(f"Evaluating intelligibility for {audio_path} using {model}")
            
            # Perform ASR recognition
            if not asr_model.is_loaded:
                asr_model.load()
            recognition_result = asr_model.recognize(audio_path)
            
            transcription = recognition_result.get("text", "")
            confidence = recognition_result.get("confidence", 0.0)
            language = recognition_result.get("language", "unknown")
            
            # Calculate intelligibility score based on confidence and text quality
            intelligibility_score = self._calculate_intelligibility_score(
                transcription, confidence, reference_text
            )
            
            result = {
                "file": audio_path.name,
                "transcription": transcription,
                "reference": reference_text or "No reference provided",
                "confidence": round(confidence, 3),
                "intelligibility_score": round(intelligibility_score, 3),
                "language": language,
                "model": model
            }
            
            # Calculate WER if reference text is provided
            if reference_text and transcription:
                wer = self._calculate_wer(reference_text, transcription)
                result["word_error_rate"] = round(wer, 3)
            
            return result
            
        except Exception as e:
            logger.exception(f"Failed to evaluate intelligibility for {audio_path}")
            raise AudioProcessingError(f"Failed to evaluate intelligibility for {audio_path}: {str(e)}")
    
    def _calculate_intelligibility_score(self, transcription: str, confidence: float, reference_text: str | None = None) -> float:
        """Calculate intelligibility score based on ASR results.
        
        Args:
            transcription: ASR transcription result.
            confidence: ASR confidence score.
            reference_text: Reference text for comparison (optional).
            
        Returns:
            Intelligibility score between 0 and 1.
        """
        if not transcription.strip():
            return 0.0
        
        # Base score from ASR confidence
        base_score = confidence
        
        # Adjust based on transcription quality indicators
        text_length = len(transcription.strip())
        if text_length > 0:
            # Bonus for reasonable text length
            length_bonus = min(0.1, text_length / 100)
            base_score += length_bonus
        
        # If reference text is available, use similarity for adjustment
        if reference_text:
            similarity = self._calculate_text_similarity(reference_text, transcription)
            # Weight the similarity more heavily
            base_score = 0.4 * base_score + 0.6 * similarity
        
        return min(1.0, max(0.0, base_score))
    
    def _calculate_text_similarity(self, ref_text: str, hyp_text: str) -> float:
        """Calculate similarity between reference and hypothesis text.
        
        Args:
            ref_text: Reference text.
            hyp_text: Hypothesis text from ASR.
            
        Returns:
            Similarity score between 0 and 1.
        """
        if not ref_text.strip() or not hyp_text.strip():
            return 0.0
        
        # Use SequenceMatcher for similarity calculation
        similarity = difflib.SequenceMatcher(None, ref_text.lower(), hyp_text.lower()).ratio()
        return similarity
    
    def _calculate_wer(self, reference: str, hypothesis: str) -> float:
        """Calculate Word Error Rate (WER) between reference and hypothesis.
        
        Args:
            reference: Reference text.
            hypothesis: Hypothesis text from ASR.
            
        Returns:
            Word Error Rate as a float between 0 and 1.
        """
        ref_words = reference.strip().split()
        hyp_words = hypothesis.strip().split()
        
        if not ref_words:
            return 1.0 if hyp_words else 0.0
        
        # Dynamic programming for edit distance
        d = [[0 for _ in range(len(hyp_words) + 1)] for _ in range(len(ref_words) + 1)]
        
        for i in range(len(ref_words) + 1):
            d[i][0] = i
        for j in range(len(hyp_words) + 1):
            d[0][j] = j
        
        for i in range(1, len(ref_words) + 1):
            for j in range(1, len(hyp_words) + 1):
                if ref_words[i-1] == hyp_words[j-1]:
                    d[i][j] = d[i-1][j-1]
                else:
                    d[i][j] = min(d[i-1][j], d[i][j-1], d[i-1][j-1]) + 1
        
        return d[len(ref_words)][len(hyp_words)] / len(ref_words)
    
    def evaluate_directory(self, input_dir: Path, reference_file: Path | None, model: str) -> dict[str, dict]:
        """Evaluate intelligibility for all audio files in a directory.
        
        Args:
            input_dir: Path to the input directory containing audio files.
            reference_file: Path to reference text file (optional).
            model: ASR model name to use for evaluation.
            
        Returns:
            Dictionary mapping audio filenames to evaluation results.
            
        Raises:
            FileNotFoundError: If the input directory does not exist.
            AudioProcessingError: If no audio files are found or processing fails.
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Load reference texts if provided
        references = {}
        if reference_file:
            references = self.load_reference_text(reference_file)
        
        # Find all audio files
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            logger.error(f"No audio files found in {input_dir}")
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        results = {}
        
        def process_file(audio_file: Path) -> tuple[str, dict]:
            """Process a single audio file."""
            reference_text = references.get(audio_file.name, None)
            try:
                result = self.evaluate_file(audio_file, reference_text, model)
                return audio_file.name, result
            except Exception as e:
                logger.error(f"Failed to evaluate {audio_file}: {str(e)}")
                return audio_file.name, {"error": str(e)}
        
        # Process files sequentially
        for audio_file in audio_files:
            reference_text = references.get(audio_file.name, None)
            try:
                result = self.evaluate_file(audio_file, reference_text, model)
                results[audio_file.name] = result
            except Exception as e:
                logger.error(f"Failed to evaluate {audio_file}: {str(e)}")
                results[audio_file.name] = {"error": str(e)}
        
        successful = sum(1 for result in results.values() if "error" not in result)
        logger.info(f"Processed {len(audio_files)} files, {successful} successful")
        return results
    
    def load_reference_text(self, reference_file: Path) -> dict[str, str]:
        """Load reference text from file.
        
        Args:
            reference_file: Path to the reference text file.
            
        Returns:
            Dictionary mapping audio filenames to reference texts.
            
        Raises:
            FileNotFoundError: If the reference file does not exist.
            AudioProcessingError: If loading fails.
        """
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
            
            logger.info(f"Loaded {len(references)} reference texts from {reference_file}")
            return references
            
        except Exception as e:
            logger.exception("Failed to load reference text")
            raise AudioProcessingError(f"Failed to load reference text: {str(e)}")
    
