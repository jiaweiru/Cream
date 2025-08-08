"""MOS (Mean Opinion Score) evaluation functionality."""

from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError


class MOSEvaluator:
    """MOS evaluation processor using various models."""
    
    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers or config.max_workers
    
    def evaluate_file(self, audio_path: Path, model: str) -> float:
        """Evaluate MOS score for a single audio file."""
        if not config.is_audio_file(audio_path):
            raise InvalidFormatError(f"Unsupported audio format: {audio_path.suffix}")
        
        model_config = config.get_model_config("mos", model)
        if not model_config.get("enabled", False):
            raise ModelNotAvailableError(f"MOS model {model} is not available")
        
        try:
            # Placeholder for actual MOS evaluation
            # In real implementation, this would load and run NiSQA, UTMOSv2, etc.
            print(f"Evaluating MOS for {audio_path} using {model}")
            
            # Mock MOS score (1-5 scale)
            import random
            random.seed(hash(str(audio_path)) % 2147483647)  # Deterministic for same file
            mock_score = random.uniform(2.5, 4.8)
            
            return round(mock_score, 2)
            
        except Exception as e:
            raise AudioProcessingError(f"Failed to evaluate MOS for {audio_path}: {str(e)}")
    
    def evaluate_directory(self, input_dir: Path, model: str) -> dict[str, float]:
        """Evaluate MOS scores for all audio files in directory."""
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        results = {}
        
        def process_file(audio_file):
            score = self.evaluate_file(audio_file, model)
            return audio_file.name, score
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, score = future.result()
                results[file_name] = score
        
        return results
    
    def batch_evaluate(self, audio_files: list[Path], model: str) -> dict[str, float]:
        """Evaluate MOS scores for a batch of audio files."""
        results = {}
        
        def process_file(audio_file):
            score = self.evaluate_file(audio_file, model)
            return audio_file.name, score
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, score = future.result()
                results[file_name] = score
        
        return results