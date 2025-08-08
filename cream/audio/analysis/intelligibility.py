"""Speech intelligibility evaluation functionality."""

from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError


class IntelligibilityEvaluator:
    """Speech intelligibility evaluator using ASR models."""
    
    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers or config.max_workers
    
    def evaluate_file(self, audio_path: Path, reference_text: str | None, model: str) -> dict[str, str | float | int]:
        """Evaluate speech intelligibility for a single audio file."""
        if not config.is_audio_file(audio_path):
            raise InvalidFormatError(f"Unsupported audio format: {audio_path.suffix}")
        
        model_config = config.get_model_config("asr", model)
        if not model_config.get("enabled", False):
            raise ModelNotAvailableError(f"ASR model {model} is not available")
        
        try:
            # Placeholder for actual intelligibility evaluation
            # In real implementation, this would use Paraformer, Whisper, etc.
            print(f"Evaluating intelligibility for {audio_path} using {model}")
            
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
            raise AudioProcessingError(f"Failed to evaluate intelligibility for {audio_path}: {str(e)}")
    
    def load_reference_text(self, reference_file: Path) -> dict[str, str]:
        """Load reference text from file."""
        if not reference_file.exists():
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
            raise AudioProcessingError(f"Failed to load reference text: {str(e)}")
    
    def evaluate_directory(self, input_dir: Path, reference_file: Path | None, model: str) -> dict[str, dict[str, str | float | int]]:
        """Evaluate intelligibility for all audio files in directory."""
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        # Load reference texts if provided
        references = {}
        if reference_file:
            references = self.load_reference_text(reference_file)
        
        results = {}
        
        def process_file(audio_file):
            file_stem = audio_file.stem
            reference_text = references.get(file_stem) or references.get(audio_file.name)
            
            result = self.evaluate_file(audio_file, reference_text, model)
            return audio_file.name, result
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, result = future.result()
                results[file_name] = result
        
        return results
    
    def calculate_metrics(self, results: dict[str, dict[str, str | float | int]]) -> dict[str, float]:
        """Calculate overall intelligibility metrics from results."""
        if not results:
            return {}
        
        total_files = len(results)
        total_confidence = sum(r.get("confidence", 0) for r in results.values())
        total_intelligibility = sum(r.get("intelligibility_score", 0) for r in results.values())
        
        metrics = {
            "average_confidence": round(total_confidence / total_files, 3),
            "average_intelligibility_score": round(total_intelligibility / total_files, 3),
            "total_files": total_files
        }
        
        # Calculate average WER if available
        wer_scores = [r.get("word_error_rate") for r in results.values() if "word_error_rate" in r]
        if wer_scores:
            metrics["average_word_error_rate"] = round(sum(wer_scores) / len(wer_scores), 3)
        
        return metrics